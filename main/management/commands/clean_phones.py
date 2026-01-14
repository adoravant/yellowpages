import re
from django.core.management.base import BaseCommand
from main.models import LeadFull


class Command(BaseCommand):
    help = "Limpieza incremental de LeadFull.phone (idempotente, con doble pasada para +549 y auditoría final)"

    def handle(self, *args, **options):
        # ==== Pipeline principal con hasta 2 pasadas ====
        for pass_num in range(2):
            qs = (
                LeadFull.objects
                .exclude(phone__isnull=True)
                .exclude(phone="")
            )

            to_update = []

            for lead in qs.iterator(chunk_size=1000):
                original = lead.phone

                # Paso 1: solo dígitos
                phone = re.sub(r"\D", "", original)

                # Paso 2: quitar un solo 0 inicial
                if phone.startswith("0"):
                    phone = phone[1:]

                # Paso 3: quitar '15' BA / Neuquén
                phone = re.sub(r"^(11|299)15", r"\1", phone)

                # Paso 4: característica (2 a 4) + 15 en números de 12 sin 54
                if not phone.startswith("54") and len(phone) == 12:
                    phone = re.sub(r"^(\d{2,4})15", r"\1", phone)

                # Paso 5: 0800 (empiezan con 8 → volver a poner 0)
                if phone.startswith("8"):
                    phone = "0" + phone

                # Paso 6: WhatsApp normalization
                if not phone.startswith("+"):
                    # 10 dígitos → +549
                    if len(phone) == 10:
                        phone = "+549" + phone
                    # 13 dígitos empezando con 549 → +549...
                    elif len(phone) == 13 and phone.startswith("549"):
                        phone = "+" + phone

                # Paso 7: recortar números demasiado largos
                # solo si no empieza con +, 08 o 549 y tiene al menos 11 dígitos
                if not phone.startswith(("+", "08", "549")) and len(phone) >= 11:
                    phone = phone[:10]  # dejamos solo los primeros 10 dígitos

                # Guardar solo si cambió
                if phone and phone != original:
                    lead.phone = phone
                    to_update.append(lead)

            if to_update:
                LeadFull.objects.bulk_update(to_update, ["phone"], batch_size=1000)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Pasada {pass_num + 1}: Procesados: {qs.count()} | Actualizados: {len(to_update)}"
                )
            )

            # Si no se actualizaron registros, no hace falta segunda pasada
            if not to_update:
                break

        # ==== Paso final: auditoría de formatos ====
        total_plus549 = 0
        total_0800 = 0
        total_menos10 = 0

        for lead in LeadFull.objects.exclude(phone__isnull=True).exclude(phone=""):
            phone = lead.phone.strip()
            phone_digits = re.sub(r"\D", "", phone)  # solo dígitos

            if re.fullmatch(r"\+549\d{10}", phone):
                total_plus549 += 1
            elif re.fullmatch(r"0(810|800)\d{7}", phone_digits):  # 11 dígitos total
                total_0800 += 1
            elif len(phone_digits) < 10:
                total_menos10 += 1

        self.stdout.write(self.style.SUCCESS(
            "\n==== Auditoría final de formatos ===="
        ))
        self.stdout.write(f"Leads +549XXXXXXXXXX: {total_plus549}")
        self.stdout.write(f"Leads 0800/0810 (11 dígitos): {total_0800}")
        self.stdout.write(f"Leads con menos de 10 dígitos: {total_menos10}")
        