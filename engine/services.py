from django.db import transaction
from engine.models import EventTypeConfig, ActionTypeConfig
from events import Events  # Tu clase con los slugs de strings
from functions import FUNCTIONS_AVAILABLE
from .eventconfig import EVENT_DEFAULTS

# -----------------------------------------
# Helpers
# -----------------------------------------

def _humanize(slug: str):
    return slug.replace("_", " ").title()

def _detect_category(slug: str):
    """Detecta categoría por prefijo (STATUS_, REPLY_, etc.)"""
    prefix = slug.split("_")[0].upper()
    mapping = {
        "STATUS": "STATUS",
        "INTENT": "INTENT",
        "REPLY": "REPLY",
        "COMM": "COMMUNICATION",
        "CTX": "CONTEXT",
        "LIFE": "LIFECYCLE",
        "STR": "STRATEGY",
        "TIME": "TIME",
        "MISC": "MISC",
    }
    return mapping.get(prefix, "OTHER")

def _detect_channel(fn_name):
    fn = fn_name.lower()
    if "whatsapp" in fn: return "WHATSAPP"
    if "email" in fn: return "EMAIL"
    if "call" in fn: return "CALL"
    return None

# -----------------------------------------
# Core Sync Functions
# -----------------------------------------

@transaction.atomic
def build_event_types():
    created = 0
    updated = 0

    # Extraer slugs de la clase Events
    attrs = [
        v for k, v in vars(Events).items()
        if not k.startswith("_") and isinstance(v, str)
    ]

    # Valores de seguridad TOTAL (Hardcoded para evitar el error de base de datos)
    SAFE_BASE = {
        "should_alert": False,
        "alert_priority": 5,
        "allowed_auto": True,
        "max_consumes": 1  # El default real que la DB espera
    }

    for slug in attrs:
        name = _humanize(slug)
        category = _detect_category(slug)
        
        # 1. Buscamos lo que definiste en tu archivo eventconfig.py
        user_config = EVENT_DEFAULTS.get(slug, {})

        # 2. Mezclamos con SAFE_BASE. 
        # Esto garantiza que aunque el slug NO ESTÉ en eventconfig, 
        # el diccionario tenga todas las llaves necesarias.
        final_config = {**SAFE_BASE, **user_config}

        # 3. Limpieza de None para evitar el error de CONSTRAINT
        # Si pusiste max_consumes=None en el dict, pero tu DB no acepta NULL,
        # lo convertimos a un valor seguro (ej: 999 o 0 según prefieras)
        if final_config["max_consumes"] is None:
            final_config["max_consumes"] = 99  # O el valor que signifique "infinito" para vos

        obj, is_created = EventTypeConfig.objects.update_or_create(
            slug=slug,
            defaults={
                "name": name,
                "category": category,
                "should_alert": final_config["should_alert"],
                "alert_priority": final_config["alert_priority"],
                "allowed_auto": final_config["allowed_auto"],
                "max_consumes": final_config["max_consumes"],
            },
        )

        if is_created: created += 1
        else: updated += 1

    return created, updated
@transaction.atomic
def build_action_types():
    created = 0
    updated = 0

    for fn_name in FUNCTIONS_AVAILABLE.keys():
        slug = fn_name
        name = _humanize(fn_name)
        channel = _detect_channel(fn_name)

        obj, is_created = ActionTypeConfig.objects.update_or_create(
            slug=slug,
            defaults=dict(
                name=name,
                function_name=fn_name,
                channel=channel,
                active=True,
            ),
        )

        if is_created: created += 1
        else: updated += 1

    return created, updated




# engine/services.py

class TriggerService:
    @staticmethod
    def handle_event(event):
        """
        Se llama cada vez que se crea un Event.
        """
        from engine.models import TriggerRule, MsgTemplate
        
        # 1. Si el tipo de evento no tiene reglas activas, terminamos
        rules = TriggerRule.objects.filter(event_type=event.event_type, active=True)
        if not rules.exists():
            return

        # 2. El 'ID de búsqueda' para la plantilla es el botón que se apretó
        # Si es un evento automático (no de matrix), usamos el slug del tipo.
        btn_slug = event.metadata.get('button_id') or event.event_type.slug

        for rule in rules:
            # 3. Lógica Quirúrgica de Plantillas
            template = MsgTemplate.objects.filter(
                slug=btn_slug,               # 'intent_pain_adv_money'
                segment=event.lead.website_status, 
                active=True
            ).first()

            # Fallback a la genérica del mismo botón
            if not template:
                template = MsgTemplate.objects.filter(
                    slug=btn_slug,
                    segment__isnull=True,
                    active=True
                ).first()

            # 4. Creamos la Task
            if template or rule.template:
                rule.create_task_for_lead(
                    lead=event.lead, 
                    event=event, 
                    override_template=template
                )