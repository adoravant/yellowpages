# services/action_resolver.py
from typing import Optional
import re
import unicodedata
from funnels.models import StepAction, LeadFunnelState


def _normalize_text(text: str) -> str:
    # lowercase, remove diacritics, collapse spaces
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return text


# default trigger map (extensible)
_DEFAULT_TRIGGERS = {
    "presentacion": [r"\bquien sos\b", r"\bquien es\b", r"\bquién sos\b", r"\bquién es\b"],
    "not_interested": [r"\bno me interesa\b", r"\bno interesa\b", r"\bno gracias\b", r"\bno\b"],
    "disculpame": [r"\bdisculp", r"\bperdon\b", r"\bperdón\b", r"\bmala mia\b"],
    "phone_dead": [r"\bno entreg", r"\bundeliver\b", r"\bnot delivered\b", r"\bfailed\b"],
}


class ActionResolver:
    """
    Resolve acción a partir de texto con heurísticas simples y fallback.
    - Normaliza acentos y mayúsculas.
    - Soporta patrones (regex) definidos en _DEFAULT_TRIGGERS.
    - Si no hay match, devuelve suggested_action.slug si existe.
    """

    @staticmethod
    def resolve(state: LeadFunnelState, incoming_text: Optional[str]) -> Optional[str]:
        if not incoming_text:
            return state.suggested_action.slug if state.suggested_action else None

        text = _normalize_text(incoming_text)

        # run triggers
        for action_slug, patterns in _DEFAULT_TRIGGERS.items():
            for p in patterns:
                if re.search(p, text):
                    # validate that action exists in DB (defensive)
                    if StepAction.objects.filter(slug=action_slug).exists():
                        return action_slug

        # fallback: only if suggested action still exists (defensive)
        if state.suggested_action and StepAction.objects.filter(pk=state.suggested_action.pk).exists():
            return state.suggested_action.slug

        return None
