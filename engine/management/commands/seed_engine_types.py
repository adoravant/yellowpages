# engine/management/commands/sync_engine_types.py

from django.core.management.base import BaseCommand
from engine.services import build_event_types, build_action_types


class Command(BaseCommand):
    help = "Sync EventTypeConfig and ActionTypeConfig from code constants"

    def handle(self, *args, **kwargs):
        self.stdout.write("\n🔄 Syncing Event Types...\n")
        try:
            created, updated = build_event_types()
            self.stdout.write(f"✅ Events -> created: {created} | updated: {updated}\n")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error syncing Event Types: {e}"))

        self.stdout.write("🔄 Syncing Action Types...\n")
        try:
            created, updated = build_action_types()
            self.stdout.write(f"✅ Actions -> created: {created} | updated: {updated}\n")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error syncing Action Types: {e}"))

        self.stdout.write(self.style.SUCCESS("\n🎯 Engine types synchronized successfully.\n"))