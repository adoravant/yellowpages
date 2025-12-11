from django.core.management.base import BaseCommand
from main.models import LeadFull

class Command(BaseCommand):
    help = "Contador de estado de websites y redes sociales de leads, sumando totales + detectar unaccounted"

    def handle(self, *args, **options):
        total_leads = LeadFull.objects.count()
        print(f"Total leads: {total_leads}\n")

        # ============================
        # 1. DEFINIR QUERIES REALES
        # ============================

        q_timeout = LeadFull.objects.filter(website_status="TIMEOUT")
        q_down = LeadFull.objects.filter(website_status="DOWN")
        q_ssl_error = LeadFull.objects.filter(website_status="SSL_ERROR")
        q_error = LeadFull.objects.filter(website_status="ERROR")
        q_cores = LeadFull.objects.filter(website_status="CORES")
        q_facebook = LeadFull.objects.filter(website__contains="facebook")
        q_no_cores = LeadFull.objects.filter(website_status="NO_CORES").exclude(website__contains="facebook")
        q_sin_website = LeadFull.objects.filter(website__isnull=True)
        q_unchecked = LeadFull.objects.filter(
            website__isnull=False,
            website_status__isnull=True
        ).exclude(website__contains="facebook")

        # Todas las categorías
        CATEGORIES = {
            "SIN WEBSITE": q_sin_website,
            "TIMEOUT": q_timeout,
            "DOWN": q_down,
            "SSL_ERROR": q_ssl_error,
            "ERROR": q_error,
            "CORES": q_cores,
            "FACEBOOK": q_facebook,
            "NO_CORES": q_no_cores,
            "UNCHECKED": q_unchecked,
        }

        # ============================
        # 2. IMPRIMIR COUNTS
        # ============================

        print("=== Categorías Website ===")
        for name, qs in CATEGORIES.items():
            print(f"{name}: {qs.count()}")

        # ============================
        # 3. SUMA TOTAL SIN DUPLICADOS
        # ============================

        counted_pks = set()

        for qs in CATEGORIES.values():
            counted_pks.update(qs.values_list("pk", flat=True))

        accounted_total = len(counted_pks)

        print(f"\nSuma de categorías sin duplicados: {accounted_total}")
        print(f"Total leads: {total_leads}")
        print(f"Coincide con el total? {'Sí' if accounted_total == total_leads else 'No'}")

        # ============================
        # 4. DETECTAR UNACCOUNTED
        # ============================

        if accounted_total != total_leads:
            missing_qs = LeadFull.objects.exclude(pk__in=counted_pks)
            missing_count = missing_qs.count()

            print(f"\nUNACCOUNTED (no entran en ninguna categoría): {missing_count}")

            # Mostrar hasta 50 para inspección
            for lead in missing_qs[:50]:
                print(f"- ID {lead.pk}: website={lead.website}, status={lead.website_status}")

        print("\nProceso finalizado.\n")
