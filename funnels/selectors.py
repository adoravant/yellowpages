from .models import MsgTemplate, StepAction


def select_template(funnel=None, step=None, action=None):
    """
    Devuelve la MsgTemplate más específica según funnel, step o StepAction.
    """
    return MsgTemplate.objects.pick_best(funnel=funnel, step=step, action=action)


def resolve_next_step(action: StepAction):
    """
    Decide a qué Step avanzar:
      - action.next_step si está definido
      - sino, el siguiente step en orden del funnel
    """
    if action.next_step:
        return action.next_step
    return action.step.next_step()
