import re
from django.core.management.base import BaseCommand
from main.models import LeadFull

class Command(BaseCommand):
    help = "Trunca detalle_url hasta el id=XXXXX, eliminando parámetros extra después del id"

    URL_PATTERN = re.compile(r'^(https://www\.guiacores\.com\.ar/index\.php\?r=search/detail&id=\d+)')

    def handle(self, *args, **options):
        leads = LeadFull.objects.exclude(detalle_url__isnull=True).exclude(detalle_url='')

        modified_count = 0

        for lead in leads:
            url = lead.detalle_url
            match = self.URL_PATTERN.match(url)
            if match:
                new_url = match.group(1)
                if new_url != url:
                    lead.detalle_url = new_url
                    lead.save()
                    modified_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✔ Total URLs modificadas: {modified_count}"
        ))

