from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = "Delete ALL objects from ALL models in the 'funnels' app."

    def handle(self, *args, **kwargs):
        app_label = "funnels"
        app_config = apps.get_app_config(app_label)

        # list models in correct deletion order (reverse to avoid FK constraints)
        models = list(app_config.get_models())
        models.reverse()

        for model in models:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {count} from {model.__name__}"))

        self.stdout.write(self.style.SUCCESS("All funnels app data wiped clean."))
