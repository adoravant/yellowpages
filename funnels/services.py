from django.db import transaction
from .selectors import select_template, resolve_next_step
from .utils import render_template
from .models import StepAction, LeadFunnelState


def select_template_for_action(action: StepAction, step, funnel):
    """
    Devuelve la plantilla que se debe usar para esta acción:
      1) Primero la plantilla específica de la StepAction
      2) Luego plantilla por StepAction
      3) Luego plantilla por Step
      4) Luego plantilla global
    """
    if action.plantilla:
        return action.plantilla
    return select_template(funnel=funnel, step=step, action=action)


def execute_step_action(state: LeadFunnelState, send_func, require_response=False):
    """
    Ejecuta la action_actual del LeadFunnelState:
      - envía plantilla del action (si existe)
      - si avanzar: resuelve next_step, actualiza state, envía plantilla del step destino (si existe)
      - si require_response=True, no avanza hasta confirmación
    """
    action = state.action_actual
    if not action:
        raise ValueError("No hay action_actual para ejecutar")

    lead = state.lead
    funnel = state.funnel
    step = state.step_actual

    # Step 1: opcionalmente esperar respuesta antes de avanzar
    if require_response and step.order == 1 and action.avanzar:
        return  # no avanzar hasta que confirmes respuesta

    # 1) enviar plantilla de la action
    tpl = select_template_for_action(action, step, funnel)
    if tpl:
        txt = render_template(tpl, lead)
        if txt:
            send_func(lead, txt, {"type": "step_action", "action": getattr(action, "slug", "")})

    # 2) avanzar
    if action.avanzar:
        next_step = resolve_next_step(action)
        if next_step is None:
            state.action_actual = None
            state.save(update_fields=["action_actual", "updated_at"])
            return

        state.step_actual = next_step
        state.action_actual = None
        state.save(update_fields=["step_actual", "action_actual", "updated_at"])

        # 3) enviar plantilla del siguiente step
        step_tpl = select_template(funnel=funnel, step=next_step, action=None)
        if step_tpl:
            txt2 = render_template(step_tpl, lead)
            if txt2:
                send_func(lead, txt2, {"type": "step", "step": next_step.order})
    else:
        state.save(update_fields=["updated_at"])


@transaction.atomic
def batch_execute(qs, selected_ids, send_func, fallback_type="manual"):
    """
    Procesa un queryset de LeadFunnelState filtrado por funnel+step+action.
    selected_ids: PKs de leads seleccionados.
    """
    for state in qs.select_for_update():
        if state.pk in selected_ids:
            execute_step_action(state, send_func)
            continue

        current = state.action_actual

        if not current:
            first = StepAction.objects.filter(step=state.step_actual, type="default").first()
            state.action_actual = first
            state.save(update_fields=["action_actual", "updated_at"])
            continue

        nxt = StepAction.objects.next_for(current)
        if nxt:
            state.action_actual = nxt
            state.save(update_fields=["action_actual", "updated_at"])
        else:
            manual = StepAction.objects.filter(step=state.step_actual, type=fallback_type).first()
            state.action_actual = manual
            state.save(update_fields=["action_actual", "updated_at"])
