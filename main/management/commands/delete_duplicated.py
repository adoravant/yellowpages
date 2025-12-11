import re
from django.core.management.base import BaseCommand
from django.db.models import Q
from main.models import LeadFull as Lead
from collections import defaultdict

class Command(BaseCommand):
    help = "Gestiona duplicados: CORE y NO_CORES, consolidando alt_phone y preservando email único"

    WHATSAPP_PREFIX = "https://api.whatsapp.com/send?phone="

    def extract_phone_from_whatsapp(self, url):
        """Extrae el número de teléfono del whatsapp_url"""
        if not url or self.WHATSAPP_PREFIX not in url:
            return None
        match = re.search(r'phone=(\d+)', url)
        return match.group(1) if match else None

    def handle(self, *args, **options):
        total_deleted = 0
        total_consolidated = 0
        total_email_skipped = 0

        # -------------------
        # POOL CORE
        # -------------------
        core_leads = Lead.objects.filter(
            Q(website__isnull=True) |
            Q(website__icontains="facebook") |
            Q(website__icontains="instagram") |
            Q(website__icontains="linkedin") |
            Q(website__icontains="linktr")
        ).exclude(name__isnull=True).exclude(name="")

        self.stdout.write("🔹 Procesando pool NO_WEB, SOCIAL")
        deleted_core, consolidated_core = self.process_core_pool(core_leads)
        total_deleted += deleted_core
        total_consolidated += consolidated_core

        # -------------------
        # POOL NO_CORES
        # -------------------
        no_core_leads = Lead.objects.filter(website_status="NO_CORES").exclude(name__isnull=True).exclude(name="")

        self.stdout.write("🔹 Procesando pool NO_CORES")
        deleted_no_core, consolidated_no_core, email_skipped = self.process_no_core_pool(no_core_leads)
        total_deleted += deleted_no_core
        total_consolidated += consolidated_no_core
        total_email_skipped += email_skipped

        # -------------------
        # Resumen final
        # -------------------
        self.stdout.write(self.style.SUCCESS(f"✔ Total eliminados: {total_deleted}"))
        self.stdout.write(self.style.SUCCESS(f"✔ Total WhatsApp consolidados en alt_phone: {total_consolidated}"))
        self.stdout.write(self.style.SUCCESS(f"✔ Emails no copiados por UNIQUE constraint: {total_email_skipped}"))

    # -------------------
    # Funciones auxiliares
    # -------------------
    def process_core_pool(self, leads):
        from collections import defaultdict
        total_deleted = 0
        total_consolidated = 0
        grouped = defaultdict(list)
        for lead in leads:
            clean_name = lead.name.strip().lower().replace("\t", " ").replace("\n", " ")
            grouped[clean_name].append(lead)

        for name, items in grouped.items():
            if len(items) <= 1:
                continue
            valid = [lead for lead in items if lead.whatsapp_url and self.WHATSAPP_PREFIX in lead.whatsapp_url]
            invalid = [lead for lead in items if not (lead.whatsapp_url and self.WHATSAPP_PREFIX in lead.whatsapp_url)]

            if valid:
                for lead in invalid:
                    lead.delete()
                    total_deleted += 1
                kept_items = valid
            else:
                to_keep = invalid[0]
                for lead in invalid[1:]:
                    lead.delete()
                    total_deleted += 1
                kept_items = [to_keep]

            while len(kept_items) > 1:
                main = kept_items[0]
                duplicate = kept_items[1]
                phone_extra = self.extract_phone_from_whatsapp(duplicate.whatsapp_url)
                if phone_extra:
                    main.alt_phone = phone_extra
                    main.save()
                    total_consolidated += 1
                duplicate.delete()
                total_deleted += 1
                kept_items.pop(1)

            kept_ids = [lead.id for lead in kept_items]
            self.stdout.write(f"♻ {name}: conservados IDs {kept_ids}, eliminados {len(items)-len(kept_ids)}")

        return total_deleted, total_consolidated

    def process_no_core_pool(self, leads):
        from collections import defaultdict
        total_deleted = 0
        total_consolidated = 0
        total_email_skipped = 0

        grouped = defaultdict(list)
        for lead in leads:
            clean_name = lead.name.strip().lower().replace("\t", " ").replace("\n", " ")
            grouped[clean_name].append(lead)

        for name, items in grouped.items():
            if len(items) <= 1:
                continue
            main = items[0]
            duplicates = items[1:]

            for dup in duplicates:
                # Consolidar WhatsApp a alt_phone
                phone_extra = self.extract_phone_from_whatsapp(dup.whatsapp_url)
                if phone_extra:
                    main.alt_phone = phone_extra
                    total_consolidated += 1

                # Copiar email solo si no rompe UNIQUE
                if dup.email and not main.email:
                    if not Lead.objects.filter(email=dup.email).exclude(pk=main.pk).exists():
                        main.email = dup.email
                    else:
                        total_email_skipped += 1

                main.save()

                # Eliminamos el duplicado
                dup.delete()
                total_deleted += 1

            self.stdout.write(f"♻ {name}: conservado ID {main.id}, duplicados eliminados {len(duplicates)}")

        return total_deleted, total_consolidated, total_email_skipped
