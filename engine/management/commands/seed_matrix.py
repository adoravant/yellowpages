from django.core.management.base import BaseCommand
from django.db import transaction
from engine.models import EventTypeConfig, MatrixButtonConfig, MatrixScenario

STAGES_CONFIG = {
    'VALIDATION': {
        'AVANCE': [
            {'id': 'intent_pain_adv_money', 'label': 'Hook: Dolor Dinero ($)', 'next_stage': 'PAIN', 'icon': 'dollar-sign'},
            {'id': 'intent_pain_adv_tech', 'label': 'Hook: Dolor Técnico', 'next_stage': 'PAIN', 'icon': 'cpu'},
            {'id': 'intent_pain_adv_urgency', 'label': 'Hook: Dolor Urgencia', 'next_stage': 'PAIN', 'icon': 'alert-circle'},
        ],
        'OBJECION': [
            {'id': 'intent_val_obj_who', 'label': 'Filtro: Quién soy', 'next_stage': 'VALIDATION', 'icon': 'help-circle'},
            {'id': 'intent_val_obj_source', 'label': 'Filtro: Origen Data', 'next_stage': 'VALIDATION', 'icon': 'database'},
            {'id': 'intent_val_obj_value', 'label': 'Filtro: Valor Corto', 'next_stage': 'VALIDATION', 'icon': 'zap'},
        ],
        'HOOK_SALIDA': [
            {'id': 'intent_val_out_close', 'label': 'Archive / No califica', 'next_stage': 'CLOSED', 'icon': 'trash-2'},
            {'id': 'intent_val_out_spam', 'label': 'Marcar Spam', 'next_stage': 'CLOSED', 'icon': 'shield-off'},
            {'id': 'intent_val_out_nurture', 'label': 'A Nurturing', 'next_stage': 'CLOSED', 'icon': 'clock'},
        ]
    },
    'PAIN': {
        'AVANCE': [
            {'id': 'intent_call_adv_direct', 'label': 'Ask: Call Directa', 'next_stage': 'CALL', 'icon': 'phone-call'},
            {'id': 'intent_call_adv_calendar', 'label': 'Ask: Enviar Calendly', 'next_stage': 'CALL', 'icon': 'calendar'},
            {'id': 'intent_call_adv_options', 'label': 'Ask: Dar Opciones Horario', 'next_stage': 'CALL', 'icon': 'list'},
        ],
        'OBJECION': [
            {'id': 'intent_pain_obj_how', 'label': 'Duda: ¿Cómo lo hacen?', 'next_stage': 'PAIN', 'icon': 'settings'},
            {'id': 'intent_pain_obj_social', 'label': 'Duda: Casos de Éxito', 'next_stage': 'PAIN', 'icon': 'users'},
            {'id': 'intent_pain_obj_later', 'label': 'Duda: Dejar para después', 'next_stage': 'PAIN', 'icon': 'calendar-x'},
        ],
        'HOOK_SALIDA': [
            {'id': 'intent_pain_out_ghost', 'label': 'Perdí Interés (Ghost)', 'next_stage': 'CLOSED', 'icon': 'ghost'},
            {'id': 'intent_pain_out_competitor', 'label': 'Usa Competencia', 'next_stage': 'CLOSED', 'icon': 'shredder'},
            {'id': 'intent_pain_out_followup', 'label': 'Seguimiento 15 días', 'next_stage': 'CLOSED', 'icon': 'mail'},
        ]
    },
    'CALL': {
        'AVANCE': [
            {'id': 'intent_call_adv_schedule', 'label': 'Confirmar Horario', 'next_stage': 'CALL', 'icon': 'calendar-check'},
            {'id': 'intent_call_adv_notes', 'label': 'Agregar Nota', 'next_stage': 'CALL', 'icon': 'edit-2'},
            {'id': 'intent_call_adv_followup', 'label': 'Programar Seguimiento', 'next_stage': 'CLOSED', 'icon': 'clock'},
        ],
        'OBJECION': [
            {'id': 'intent_call_obj_busy', 'label': 'Lead ocupado', 'next_stage': 'CALL', 'icon': 'alert-circle'},
            {'id': 'intent_call_obj_no_answer', 'label': 'No responde', 'next_stage': 'CALL', 'icon': 'phone-off'},
            {'id': 'intent_call_obj_wrong_number', 'label': 'Número equivocado', 'next_stage': 'CLOSED', 'icon': 'x-circle'},
        ],
        'HOOK_SALIDA': [
            {'id': 'intent_call_out_closed', 'label': 'Cerrado con éxito', 'next_stage': 'CLOSED', 'icon': 'check-circle'},
            {'id': 'intent_call_out_failed', 'label': 'No se concretó', 'next_stage': 'CLOSED', 'icon': 'x-circle'},
            {'id': 'intent_call_out_followup', 'label': 'Seguimiento futuro', 'next_stage': 'CLOSED', 'icon': 'clock'},
        ]
    }
}

class Command(BaseCommand):
    help = 'Limpia y recrea los escenarios de Matrix con iconos y lógica de slugs'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Iniciando Matrix Seed...")

        with transaction.atomic():
            # 1. Limpieza total de escenarios previos
            MatrixScenario.objects.all().delete()

            ROW_MAPPING = {
                'AVANCE': ['slot_adv_1', 'slot_adv_2', 'slot_adv_3'],
                'OBJECION': ['slot_sta_1', 'slot_sta_2', 'slot_sta_3'],
                'HOOK_SALIDA': ['slot_out_1', 'slot_out_2', 'slot_out_3']
            }

            for stage_name, categories in STAGES_CONFIG.items():
                self.stdout.write(f"🛠️ Configurando Tablero: {stage_name}")
                
                # Creamos el escenario base (Home) de la etapa
                sc = MatrixScenario.objects.create(
                    stage=stage_name, 
                    last_intent_slug=None # Crucial para el Resolver
                )

                for cat_name, btn_list in categories.items():
                    slot_fields = ROW_MAPPING[cat_name]
                    
                    for i, btn_data in enumerate(btn_list):
                        # 1. Extraer Slugs: de 'intent_pain_adv_money' -> 'intent_pain' + 'money'
                        parts = btn_data['id'].split('_')
                        event_slug = f"{parts[0]}_{parts[1]}" 
                        flavor = parts[-1]
                        
                        et, _ = EventTypeConfig.objects.get_or_create(
                            slug=event_slug,
                            defaults={'name': event_slug.replace('_', ' ').title()}
                        )

                        # 2. Crear/Actualizar Botón (GUARDANDO EL ICONO)
                        btn, _ = MatrixButtonConfig.objects.update_or_create(
                            label=btn_data['label'],
                            defaults={
                                'event_type': et,
                                'flavor': flavor,
                                'icon': btn_data.get('icon', 'help-circle'), # <--- AQUÍ ESTÁ EL FIX
                                'next_stage': btn_data['next_stage'],
                                'active': True
                            }
                        )

                        # 3. Asignar al slot del modelo
                        field_name = slot_fields[i]
                        setattr(sc, field_name, btn)
                
                sc.save()

        self.stdout.write(self.style.SUCCESS("✅ Matrix Seed finalizado con éxito."))