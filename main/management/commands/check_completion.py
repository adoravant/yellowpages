# main/management/commands/check_leadfull_fields.py
from django.core.management.base import BaseCommand
from main.models import LeadFull

EXCEPT_FIELDS = ['logo_url', 'search_tag', 'website_type', 'website_status', 'rubros', 'redes_sociales', 'tiendas']
DEFAULT_FILL = "NO-DATA"  # Opcional, si querés rellenar los campos vacíos

class Command(BaseCommand):
    help = "Verifica LeadFull y reporta campos None excepto los excepcionados"

    def handle(self, *args, **options):
        leads = LeadFull.objects.all()
        total_checked = 0
        total_missing = 0

        for lead in leads:
            missing_fields = []
            for field in lead._meta.get_fields():
                # Nos quedamos solo con campos de tipo CharField o IntegerField
                if field.name in EXCEPT_FIELDS:
                    continue

                if field.concrete and not field.many_to_many and not field.one_to_many:
                    value = getattr(lead, field.name)
                    if value is None:
                        missing_fields.append(field.name)

                        # Si querés rellenar con valor por defecto:
                        setattr(lead, field.name, DEFAULT_FILL)

            if missing_fields:
                total_missing += 1
                self.stdout.write(f"Lead ID {lead.id} tiene campos vacíos: {missing_fields}")
            
            # Guardar cambios si rellenamos con DEFAULT_FILL
            if missing_fields:
                lead.save()

            total_checked += 1

        self.stdout.write(self.style.SUCCESS(
            f"Chequeo completado: {total_checked} leads revisados, {total_missing} tenían campos vacíos."
        ))

