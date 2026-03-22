from django.db import transaction
from django.utils import timezone
from .models import MatrixScenario, MatrixButtonConfig, EventTypeConfig
from sales.models import Event
from events import Events, create_event

# CONFIGURACIÓN MAESTRA (La Única Fuente de Verdad)
#UNA INSTANCIA DE VALIDATION INTENT DISTINTA A HOLA SOS EL DUEÑO?. 
# TIPO "HOLA POR QUE LA PAGINA ESTA CAIDA? LUEGO PUEDO 
# ENTRAR NO SOY UN CLIENTE; LOS CLIENTES NO TE LLAMAN NI TE AVISAN; SE VAN CON LA COMPETENCIA, CALL ENTRADA"
# TOP TIER;

# =====================================================




#validation_pain_money;intent_pain_adv_tech,intent_pain_adv_urgency
#avanzo a pain intent, esto setea pain reply, con 3 objecesiones sobre money, urgency o el pain que elegi.
#como las objecioens siempre son o 1 externas, de 2 autoridad, o 3 personales. 
# podemos dejar esas 3 generales "pero especificas", 
# dependiendo donde deposita la objecion el tipo.
# en solpa 2 tengo reframes aristotelicos. Mientras no se soluciones > pain pain pain.
#ENTONCES EL FLOW ES ALGO ASI COMO. > ESTABLEZCO EL PAIN DE LA PAGINA CAIDA O LO QUE SEA,
#CUANDO EL RESPONDE TENGO LISTAS MIS OBJECTION REBATE QUE VIENEN ENCAMINADAS SEGUN EL TIPO 1,2,3 Y EL FLAVOR QUE LE MANDE.
#Entonces, ponele si yo le digo, "Tenes la pagina caida, estas perdiendo plata"


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


class MatrixResolver:
    def __init__(self, progress):
        self.progress = progress
        self.lead = progress.lead


    def get_scenario(self):
        current_stage = self.progress.current_stage

        # Último evento con intent
        last_event = self.lead.events.filter(
            event_type__slug__icontains="intent"
        ).order_by('-created_at').first()

        last_intent_slug = None
        if last_event:
            flavor = last_event.metadata.get('flavor', '')
            last_intent_slug = f"{last_event.event_type.slug}_{flavor}"

        # Buscamos escenario específico
        scenario = MatrixScenario.objects.filter(
            stage=current_stage,
            last_intent_slug=last_intent_slug
        ).first()

        # Fallback al escenario inicial de la etapa
        if not scenario:
            scenario = MatrixScenario.objects.filter(
                stage=current_stage,
                last_intent_slug__isnull=True
            ).first()

        # 🔥 Si todavía no hay escenario, lo creamos y llenamos desde config maestra
        if not scenario:
            sync_matrix_from_config()
            scenario = MatrixScenario.objects.filter(
                stage=current_stage,
                last_intent_slug__isnull=True
            ).first()

        return scenario
    
    @transaction.atomic
    def execute_click(self, button_id, technician=None):
        """
        Procesa el click, genera el evento y mueve el stage si es necesario.
        """
        btn = MatrixButtonConfig.objects.get(id=button_id)
        
        # 1. Crear el evento usando tu lógica de sales/events.py
        # El event_slug viene del event_type asociado al botón
        new_event = create_event(
            lead=self.lead,
            event_slug=btn.event_type.slug,
            metadata={'flavor': btn.flavor, 'technician_id': technician.id if technician else None}
        )

        # 2. El Salto de Etapa (Validación implícita)
        if btn.next_stage != self.progress.current_stage:
            self.progress.current_stage = btn.next_stage
            # Sincronizamos los hitos en el LeadProgress (validated, pain, etc.)
            self.progress.sync_from_event(new_event)
            self.progress.save()

        # 3. Calculamos el nuevo tablero resultante
        new_scenario = self.get_scenario()
        
        return {
            "event": new_event,
            "next_stage": self.progress.current_stage,
            "scenario": new_scenario
        }

# UTILIDAD PARA SINCRONIZAR (Pipeline)
# =====================================================
def sync_matrix_from_config():
    """
    Lee el STAGES_CONFIG y reconstruye botones y escenarios base.
    """
    ROW_MAPPING = {
        'AVANCE': ['slot_adv_1', 'slot_adv_2', 'slot_adv_3'],
        'OBJECION': ['slot_sta_1', 'slot_sta_2', 'slot_sta_3'],
        'HOOK_SALIDA': ['slot_out_1', 'slot_out_2', 'slot_out_3']
    }

    with transaction.atomic():
        # Limpiamos escenarios base para reconstruir
        MatrixScenario.objects.filter(last_intent_slug__isnull=True).delete()

        for stage_name, categories in STAGES_CONFIG.items():
            # Crear escenario base de la etapa
            sc = MatrixScenario.objects.create(stage=stage_name, last_intent_slug=None)

            for cat_name, btn_list in categories.items():
                slot_fields = ROW_MAPPING[cat_name]
                
                for i, btn_data in enumerate(btn_list):
                    # Parsear slug para obtener tipo y sabor
                    # ej: intent_pain_adv_money -> tipo: intent_pain, flavor: money
                    parts = btn_data['id'].split('_')
                    event_base = f"{parts[0]}_{parts[1]}"
                    flavor = parts[-1]

                    et, _ = EventTypeConfig.objects.get_or_create(slug=event_base)

                    btn, _ = MatrixButtonConfig.objects.update_or_create(
                        label=btn_data['label'],
                        defaults={
                            'event_type': et,
                            'flavor': flavor,
                            'icon': btn_data['icon'],
                            'next_stage': btn_data['next_stage'],
                        }
                    )

                    setattr(sc, slot_fields[i], btn)
            sc.save()
    return True