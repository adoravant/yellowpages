from django.core.management.base import BaseCommand
from django.db import transaction
from engine.models import MatrixButtonConfig, MsgTemplate

class Command(BaseCommand):
    help = 'Genera plantillas (MsgTemplate) automáticas basadas en los botones de la Matrix'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("🔄 Iniciando sincronización de plantillas..."))
        
        # Canales a generar
        CHANNELS = ['WHATSAPP', 'EMAIL']
        created_count = 0
        existing_count = 0

        # Traemos todos los botones activos
        buttons = MatrixButtonConfig.objects.filter(active=True)

        with transaction.atomic():
            for btn in buttons:
                # El ADN que une el botón con la plantilla
                intent_slug = btn.resolve_slug() # ej: intent_val_obj_who
                
                for channel in CHANNELS:
                    # Buscamos si ya existe la plantilla genérica (segment=None) para ese slug y canal
                    template, created = MsgTemplate.objects.get_or_create(
                        slug=intent_slug,
                        channel=channel,
                        segment__isnull=True, # Genérica
                        defaults={
                            'content': (
                                f"Hola {{name}}, [Respuesta automática para: {btn.label}]\n"
                                f"Referencia: {intent_slug}"
                            ),
                            'active': True,
                            'subject': f"Re: {btn.label}" if channel == 'EMAIL' else None
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f"  ✅ Creada: {intent_slug} [{channel}]")
                    else:
                        existing_count += 1

        self.stdout.write("---")
        self.stdout.write(self.style.SUCCESS(
            f"🎯 Sincronización finalizada.\n"
            f"   Nuevas: {created_count}\n"
            f"   Existentes: {existing_count}\n"
            f"   Total templates: {created_count + existing_count}"
        ))