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

