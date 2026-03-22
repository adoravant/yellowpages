"""
Context Registry: define qué objetos y variables están disponibles en el contexto
y cómo acceder a ellos dinámicamente. Soporta acceso a subcampos y relaciones.
"""

from typing import Any
from django.db.models import Model, QuerySet
from engine.models import TriggerRule, EventTypeConfig, ActionTypeConfig, MsgTemplate
from sales.models import Event, Alert, Task, LeadProgress
from main.models import LeadFull

# --- Helpers para variables calculadas --- #

def get_last_event(ctx):
    """Devuelve el último evento del lead concreto."""
    lead = ctx.lead
    if hasattr(lead, "events"):
        return lead.events.order_by("-created_at").first()
    return None

def get_executed_actions(ctx):
    """Devuelve slugs de acciones ejecutadas del lead concreto."""
    lead = ctx.lead
    if hasattr(lead, "tasks"):
        return [t.action_type.slug for t in lead.tasks.filter(status="success")]
    return []

# --- Context map base --- #
CONTEXT_MAP = {
    "lead": lambda ctx: ctx.lead,
    "status": lambda ctx: getattr(ctx.lead, "leadprogress", None),  # alias para LeadProgress
    "event": lambda ctx: getattr(ctx, "event", None),
    "event_type": lambda ctx: getattr(ctx.event, "event_type", None) if getattr(ctx, "event", None) else None,
    "action": lambda ctx: getattr(ctx, "action", None),
    "action_type": lambda ctx: getattr(ctx.action, "action_type", None) if getattr(ctx, "action", None) else None,
    "trigger": lambda ctx: getattr(ctx, "trigger", None),

    "last_event": get_last_event,
    "executed_actions": get_executed_actions,
    "time": lambda ctx: {"no_reply_24h": 24},
}

# --- Función utilitaria para debug --- #
def list_context_vars(ctx):
    """Devuelve un dict {var_name: type} con las variables disponibles en contexto."""
    result = {}
    for k, v in CONTEXT_MAP.items():
        try:
            val = v(ctx) if callable(v) else v
            if isinstance(val, Model):
                result[k] = val.__class__.__name__
            elif isinstance(val, QuerySet):
                result[k] = f"QuerySet[{val.model.__name__}]"
            else:
                result[k] = type(val).__name__
        except Exception:
            result[k] = "unknown"
    return result


class QueryWrapper:
    """Wrap a QuerySet to expose only safe methods for DSL evaluation."""

    def __init__(self, qs):
        self.qs = qs

    def exists(self):
        return self.qs.exists()

    def count(self):
        return self.qs.count()

    def first(self):
        return self.qs.first()

    def last(self):
        return self.qs.last()

    def all(self):
        return self.qs

    def values_list(self, field):
        return list(self.qs.values_list(field, flat=True))
    
    
    

class ContextResolver:
    """Permite evaluar strings como 'status.validated' o 'event_type.slug' dinámicamente,
    con soporte para QuerySets intermedios y callables sin argumentos.
    """

    def __init__(self, lead):
        self.lead = lead

    def resolve(self, path: str):
        if not path:
            return None

        parts = path.split(".")
        root_name = parts[0]

        # Obtener objeto raíz
        entry = CONTEXT_MAP.get(root_name)
        if entry:
            obj = entry(self) if callable(entry) else entry
        else:
            obj = getattr(self, root_name, None)

        for part in parts[1:]:
            if obj is None:
                return None

            # Atributo normal
            if hasattr(obj, part):
                obj = getattr(obj, part)
                if callable(obj):
                    try:
                        obj = obj()
                    except TypeError:
                        return None
                if isinstance(obj, QuerySet):
                    obj = QueryWrapper(obj)
                continue

            # Si obj es QueryWrapper y tiene filter/all
            if isinstance(obj, QueryWrapper):
                continue

            # Si obj es dict o lista
            if isinstance(obj, dict):
                obj = obj.get(part, None)
                continue
            if isinstance(obj, list):
                try:
                    index = int(part)
                    obj = obj[index]
                except (ValueError, IndexError):
                    return None
                continue

            return None

        return obj