"""
Tipado y schema dinámico para DSL.
- infer_type → categorías de operadores
- build_variable_schema → navegación (dot notation)
"""

from django.db.models import Model, QuerySet
from engine.models import EventTypeConfig, ActionTypeConfig, TriggerRule
from main.models import LeadFull
from sales.models import LeadProgress

# -----------------------------
# OPERADORES (flat types)
# -----------------------------

def infer_type(value):
    """
    Devuelve categoría usable en frontend:
    text, number, logic, list, queryset o None
    """

    if value is None:
        return "text"

    if isinstance(value, bool):
        return "logic"

    if isinstance(value, (int, float)):
        return "number"

    if isinstance(value, str):
        return "text"

    if isinstance(value, list):
        return "list"

    if isinstance(value, QuerySet):
        return "queryset"

    if isinstance(value, dict):
        return "text"

    if isinstance(value, Model):
        return None  # objetos no operables directamente

    return "text"


# -----------------------------
# SCHEMA (dot notation)
# -----------------------------

def build_schema_from_model(model):
    schema = {}

    for field in model._meta.get_fields():
        name = field.name

        if field.is_relation:
            continue

        field_type = field.get_internal_type()

        if field_type in ["CharField", "TextField", "EmailField", "URLField"]:
            schema[name] = "text"
        elif field_type in ["IntegerField", "FloatField", "DecimalField",
                            "AutoField", "BigAutoField",
                            "PositiveIntegerField", "PositiveSmallIntegerField",
                            "SmallIntegerField"]:
            schema[name] = "number"
        elif field_type in ["BooleanField"]:
            schema[name] = "logic"
        elif field_type in ["DateField", "DateTimeField"]:
            schema[name] = "number"
        else:
            schema[name] = "text"

    return schema


def build_variable_schema():
    """
    Schema completo accesible desde frontend
    """

    return {
        "lead": build_schema_from_model(LeadFull),
        "status": build_schema_from_model(LeadProgress),
        "event_type": build_schema_from_model(EventTypeConfig),
        "action_type": build_schema_from_model(ActionTypeConfig),
        "trigger": build_schema_from_model(TriggerRule),
    }


# Operadores permitidos según tipo de variable
TYPE_OPERATORS = {
    "text": [
        "equals", "not_equals", "contains", "not_contains",
        "starts_with", "ends_with", "in", "not_in",
        "is_null", "not_null",
    ],
    "number": [
        "equals", "not_equals", "gt", "gte", "lt", "lte",
        "between", "is_null", "not_null",
    ],
    "logic": [
        "is", "is_not"
    ],
    "list": [
        "contains", "not_contains", "in", "not_in",
        "is_empty", "not_empty", "count_eq", "count_gt", "count_lt",
    ],
    "queryset": [
        "exists", "not_exists", "count_eq", "count_gt", "count_lt",
    ],
    "unknown": []
}