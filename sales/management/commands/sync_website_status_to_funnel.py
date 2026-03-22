# main/management/commands/sync_website_status_to_funnel.py

from django.core.management.base import BaseCommand
from main.models import LeadFull
from sales.models import Funnel


class Command(BaseCommand):
    help = "Sync website_status field to Funnel assignment (idempotent)"

    def handle(self, *args, **kwargs):

        mapping = {
            "sin_web": "sin-web",
            "web_caida": "web-caida",
            "solo_redes": "solo-redes",
            "wordpress": "wordpress",
            "no_responde": "lead-frio",
        }

        updated = 0
        skipped = 0

        for lead in LeadFull.objects.all():

            status = lead.website_status

            if not status:
                skipped += 1
                continue

            slug = mapping.get(status)

            if not slug:
                skipped += 1
                continue

            try:
                funnel = Funnel.objects.get(slug=slug)
            except Funnel.DoesNotExist:
                skipped += 1
                continue

            # 🔥 Siempre asigna aunque ya esté
            if lead.funnel_id != funnel.id:
                lead.funnel = funnel
                lead.save(update_fields=["funnel"])
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync completed. Updated: {updated}, Skipped: {skipped}"
            )
        )
