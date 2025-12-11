# funnels/services/action_applier.py

from funnels.services.step_navigator import StepNavigator
from funnels.services.pool_builder import PoolBuilder

class ActionApplier:

    @staticmethod
    def apply(state, action):
        """
        action: StepAction instance
        """
        # cierre
        if action.produce_close:
            state.set_status_and_close(action.close_status)
            return

        # avanzar
        if action.slug == "avanzar":
            StepNavigator.advance(state)
            state.current_pool = PoolBuilder.build_pool(state)
            state.save(update_fields=["current_pool", "updated_at"])
            return

        # acción normal
        state.mark_used(action.slug)
        state.current_pool = PoolBuilder.build_pool(state)
        state.save(update_fields=["current_pool", "updated_at"])




# funnels/services/template_resolver.py

from funnels.models import MsgTemplate

class TemplateResolver:

    @staticmethod
    def resolve(action=None, step=None, funnel=None):
        if action:
            return MsgTemplate.objects.filter(
                slug=action.slug,
                funnel=funnel,
                step=step
            ).first() or MsgTemplate.objects.filter(
                slug=action.slug,
                funnel=funnel,
                step__isnull=True
            ).first()

        if step:
            return MsgTemplate.objects.filter(
                step=step,
                funnel=funnel
            ).first()

        return None



# funnels/services/pool_builder.py

from funnels.models import StepActionRule, StepAction

class PoolBuilder:

    @staticmethod
    def build_pool(state):
        step = state.current_step
        if not step:
            return []

        # 1) reglas explícitas del step
        rules = StepActionRule.objects.filter(step=step).select_related("action")

        pool = []

        for rule in rules:
            action = rule.action

            # excluir usadas (salvo always)
            if action.slug in state.used_actions and rule.appearance != "always":
                continue

            pool.append(action.slug)

        # 2) agregar arrastre de until_used (reglas de steps anteriores)
        if state.funnel:
            previous_rules = StepActionRule.objects.filter(
                step__funnel=state.funnel,
                step__order__lt=step.order,
            ).select_related("action")

            for rule in previous_rules:
                if rule.appearance == "until_used":
                    slug = rule.action.slug

                    if slug not in state.used_actions:
                        pool.append(slug)

        # 3) agregar always del catálogo (global)
        always_actions = StepAction.objects.filter(
            stepactionrule__appearance="always"
        ).values_list("slug", flat=True).distinct()

        for slug in always_actions:
            if slug not in pool:
                pool.append(slug)

        # 4) excluir nunca_sugerir
        from funnels.services.rules_loader import GLOBAL_RULES
        block = GLOBAL_RULES.get("nunca_sugerir", [])

        pool = [slug for slug in pool if slug not in block]

        # ordenar por prioridad
        actions = StepAction.objects.in_bulk(pool, field_name="slug")
        pool.sort(key=lambda slug: actions[slug].priority)

        return pool



# funnels/services/simulator.py

from django.db import transaction
from funnels.services.pool_builder import PoolBuilder
from funnels.services.action_applier import ActionApplier
from funnels.models import StepAction


class FunnelSimulator:

    @staticmethod
    def run(state, steps=10, persist=False):
        """
        Simula sugerencias + ejecución automática.
        Se detiene cuando no haya acción sugerida o steps agotados.
        """

        logs = []

        with transaction.atomic():
            sp = transaction.savepoint()

            for i in range(steps):
                pool = PoolBuilder.build_pool(state)
                if not pool:
                    logs.append(("NO_MORE_ACTIONS", None, None))
                    break

                suggested_slug = pool[0]
                action = StepAction.objects.get(slug=suggested_slug)

                logs.append(("AUTO", suggested_slug, None))

                ActionApplier.apply(state, action)

                if state.status.startswith("closed_"):
                    logs.append(("CLOSED", suggested_slug, None))
                    break

            if not persist:
                transaction.savepoint_rollback(sp)
            else:
                transaction.savepoint_commit(sp)

        return logs



# funnels/services/funnel_engine.py

from funnels.services.pool_builder import PoolBuilder
from funnels.services.action_applier import ActionApplier
from funnels.services.template_resolver import TemplateResolver

class FunnelEngine:

    @staticmethod
    def start(state):
        state.current_pool = PoolBuilder.build_pool(state)
        state.save(update_fields=["current_pool"])
        return TemplateResolver.resolve(step=state.current_step, funnel=state.funnel)

    @staticmethod
    def handle_action(state, action):
        ActionApplier.apply(state, action)
        return TemplateResolver.resolve(
            action=action,
            step=state.current_step,
            funnel=state.funnel,
        )





from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import LeadFull, DiagnosticoTecnico


@admin.register(LeadFull)
class LeadFullAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "whatsapp_link",
        "detalle_url_link",
        "website_link",
        "website_status",
        "email",
        "logo_url"
    )
    search_fields = (
        "name",
        "phone",
        "email",
        "website",
        "website_type",
        "whatsapp_url",
    )
    list_filter = ("website_status", )

    # ---- WHATSAPP LINK ----
    def whatsapp_link(self, obj):
        """
        Muestra un link que dice 'WhatsApp' usando obj.whatsapp_url real.
        """
        if not obj.whatsapp_url:
            return "—"

        return mark_safe(
            f'<a href="{obj.whatsapp_url}" target="_blank">WhatsApp</a>'
        )

    whatsapp_link.short_description = "WhatsApp"
    whatsapp_link.admin_order_field = "whatsapp_url"

    # ---- DETALLE URL ----
    def detalle_url_link(self, obj):
        if obj.detalle_url:
            return mark_safe(f'<a href="{obj.detalle_url}" target="_blank">Ver detalle</a>')
        return "—"
    detalle_url_link.short_description = "Detalle URL"
    detalle_url_link.admin_order_field = "detalle_url"

    # ---- WEBSITE ----
    def website_link(self, obj):
        if obj.website:
            return mark_safe(f'<a href="{obj.website}" target="_blank">{obj.website}</a>')
        return "—"
    website_link.short_description = "Website"
    website_link.admin_order_field = "website"

    # ---- FUNNEL ----
    def funnel_actual(self, obj):
        state = obj.funnels_state.first()
        return state.funnel.nombre if state else "—"
    funnel_actual.short_description = "Funnel"


@admin.register(DiagnosticoTecnico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ("lead", "error_type", "domain", "created_at")
    list_filter = ("error_type",)


# services/exceptions.py
class FunnelException(Exception):
    pass

class InvalidAction(FunnelException):
    pass

class NoTemplateFound(FunnelException):
    pass

class StepNotFound(FunnelException):
    pass


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


#services/ACTIONS.py

STEP_ACTIONS = [
    ("ask_call", "Ask Call", 1),
    ("avanzar", "Avanzar", 2),
    ("descuento", "Descuento", 3),
    ("disculpame", "Disculpame", 4),
    ("equivocado", "Equivocado", 5),
    ("not_interested", "Not Interested", 6),
    ("not_owner", "Not Owner", 7),
    ("objecion_diagnostico", "Objeción Diagnóstico", 8),
    ("objecion_oferta", "Objeción Oferta", 9),
    ("objecion_seguimiento", "Objeción Seguimiento", 10),
    ("presentacion", "Presentación", 11),
    ("presion", "Presión", 12),
    ("recordatorio", "Recordatorio", 13),
]



CLOSING_ACTIONS = {
    "not_owner": "closed_not_owner",
    "equivocado": "closed_equivocado",
    "not_interested": "closed_not_interested",
    "phone_dead": "closed_phone_dead",
    "win": "closed_won",
}




# funnels/services/step_navigator.py

class StepNavigator:

    @staticmethod
    def advance(state):
        next_step = state.current_step.next_step()

        if next_step:
            state.current_step = next_step
            state.clear_discarded()  # opcional
            state.save(update_fields=["current_step", "updated_at"])
        else:
            # si no hay más steps no cerramos, simplemente no avanzamos
            state.current_step = None
            state.status = "end_of_funnel"
            state.save(update_fields=["current_step", "status", "updated_at"])


#services/STEP_RULES.py
STEP_RULES = {

    "validacion": {
        "not_owner": "once",
        "equivocado": "once",

        "presentacion": "until_used",
        "disculpame": "until_used",
        "ask_call": "until_used",
        # avanzar NO VA ACÁ → porque es always
    },

    "diagnostico": {
        "objecion_diagnostico": "once",
        "not_interested": "until_used",
        "disculpame": "until_used",   # este sí aparece en este step desde el step mismo
        # presentacion, ask_call, avanzar → se arrastran solos
    },

    "oferta": {
        "objecion_oferta": "once",
        "not_interested": "until_used",
        "disculpame": "until_used",
        # presentacion, ask_call, avanzar → se arrastran solos
    },

    "seguimiento": {
        "recordatorio": "once",
        "presion": "once",
        "descuento": "once",
        "objecion_seguimiento": "once",

        "not_interested": "until_used",
        "disculpame": "until_used",
        # presentacion, ask_call, avanzar → se arrastran solos
    },
}



GLOBAL_RULES = {
    "avanzar": "always",
}

