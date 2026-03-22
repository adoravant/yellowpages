"""
engine.dsl.evaluator.py
Evalúa expresiones del DSL usando el contexto de manera segura y dinámica.
"""

from typing import Any
from engine.dsl.context_registry import CONTEXT_MAP
from engine.dsl.context_types import build_variable_types


class ContextEvaluator:
    """
    Ejecuta expresiones dentro del contexto seguro.
    Permite obtener valores de variables del contexto y evaluar expresiones simples.
    """

    def __init__(self, ctx: Any):
        self.ctx = ctx
        # Variables raíz calculadas a partir del CONTEXT_MAP
        self.vars = {k: v(ctx) for k, v in CONTEXT_MAP.items()}

    def get(self, var_name: str):
        """
        Devuelve el valor de la variable del contexto.
        Permite subacceso con punto: e.g., 'last_event.event_type.slug'
        """
        parts = var_name.split(".")
        val = self.vars.get(parts[0])
        try:
            for p in parts[1:]:
                if val is None:
                    return None
                val = getattr(val, p, None)
        except Exception:
            return None
        return val

    def eval_expr(self, expr: str):
        """
        Evalúa expresiones simples usando variables del contexto.
        Seguridad: eval limitado a vars y operadores básicos.
        """
        safe_globals = {}
        safe_locals = self.vars.copy()
        try:
            return eval(expr, safe_globals, safe_locals)
        except Exception:
            return None

    def variable_types(self):
        """
        Devuelve dict de tipos para cada variable disponible en el contexto.
        """
        return build_variable_types(self.ctx)