import time
import traceback
from .models import Event

def log_event(lead, milestone, channel, status="SUCCESS", error_log=None, metadata=None):
    """Helper para crear eventos de manera consistente"""
    Event.objects.create(
        lead=lead,
        type=milestone,
        channel=channel,
        status=status,
        error_log=error_log,
        metadata=metadata
    )


def execute_auto_action(auto_action, lead):
    """Motor de ejecución centralizado para AutoActions"""

    # 1️⃣ Requiere aprobación manual
    if auto_action.require_manual_approval:
        log_event(
            lead,
            auto_action.trigger.milestone_tag,
            channel="INTERNAL",
            status="PENDING_APPROVAL",
            metadata={"action_id": auto_action.id, "info": "Aprobación pendiente"}
        )
        return

    # 2️⃣ Delay humanizado
    if auto_action.delay_seconds > 0:
        time.sleep(auto_action.delay_seconds)  # Considerar usar Celery para no bloquear

    action_type = auto_action.action_type

    try:
        if action_type == "MESSAGE":
            for tmpl in auto_action.templates.all():
                if tmpl.channel == "WHATSAPP" and getattr(lead, "phone", None):
                    # _send_ws(lead.phone, tmpl.content)
                    log_event(lead, auto_action.trigger.milestone_tag, channel="WHATSAPP")

                elif tmpl.channel == "EMAIL" and getattr(lead, "email", None):
                    # _send_email(lead.email, tmpl.subject, tmpl.content)
                    log_event(lead, auto_action.trigger.milestone_tag, channel="EMAIL")

        elif action_type == "FUNCTION" and auto_action.internal_logic_code:
            # Ejecutar función interna
            print(f"Ejecutando función: {auto_action.internal_logic_code}")
            log_event(lead, auto_action.trigger.milestone_tag, channel="SYSTEM")

        elif action_type == "TASK":
            # Crear notificación interna
            log_event(lead, auto_action.trigger.milestone_tag, channel="INTERNAL")

    except Exception as e:
        log_event(
            lead,
            auto_action.trigger.milestone_tag,
            channel="SYSTEM",
            status="ERROR",
            error_log=traceback.format_exc()
        )