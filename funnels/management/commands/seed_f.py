# management/commands/seed_funnels.py
from django.core.management.base import BaseCommand
from funnels.models import Step, StepAction, StepActionRule, Funnel, MsgTemplate
from funnels.services.STEP_RULES import STEP_RULES, GLOBAL_RULES
from funnels.services.ACTIONS import STEP_ACTIONS, CLOSING_ACTIONS
from funnels.services.FUNNELS import FUNNELS


def resolve_appearance(action_slug, step_slug):
    """Determina la aparición: once, until_used, always"""
    if action_slug in GLOBAL_RULES and GLOBAL_RULES[action_slug] == "always":
        return "always"
    step_rules = STEP_RULES.get(step_slug, {})
    return step_rules.get(action_slug, "once")


class Command(BaseCommand):
    help = "Seed Steps, StepActions, StepActionRules, Funnels y Templates completos"

    def handle(self, *args, **kwargs):
        self.stdout.write("=== Seed START ===")

        # -----------------------------
        # 1) Crear Steps globales
        # -----------------------------
        steps_map = {}
        for idx, step_slug in enumerate(STEP_RULES.keys(), start=1):
            step, _ = Step.objects.update_or_create(
                slug=step_slug,
                defaults={"name": step_slug.capitalize(), "order": idx}
            )
            steps_map[step_slug] = step
            self.stdout.write(f"Step upsert: {step_slug}")

        # -----------------------------
        # 2) Crear StepActions globales
        # -----------------------------
        actions_map = {}
        for slug, name, prio in STEP_ACTIONS:
            action, _ = StepAction.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "priority": prio,
                    "produce_close": slug in CLOSING_ACTIONS,
                    "close_status": CLOSING_ACTIONS.get(slug),
                },
            )
            actions_map[slug] = action
            self.stdout.write(f"StepAction upsert: {slug}")

        # -----------------------------
        # 3) Crear StepActionRules
        # -----------------------------
        StepActionRule.objects.all().delete()
        for step_slug, rules in STEP_RULES.items():
            step = steps_map.get(step_slug)
            if not step:
                self.stdout.write(self.style.WARNING(f"Step not found for rules: {step_slug}"))
                continue

            for action_slug in rules.keys():
                action = actions_map.get(action_slug)
                if not action:
                    self.stdout.write(self.style.WARNING(f"Missing action {action_slug} for step {step_slug}"))
                    continue

                appearance = resolve_appearance(action_slug, step_slug)
                StepActionRule.objects.update_or_create(
                    step=step,
                    action=action,
                    defaults={"appearance": appearance},
                )
            self.stdout.write(self.style.SUCCESS(f"Seeded StepActionRules for {step_slug}"))

        # -----------------------------
        # 4) Crear Funnels y Templates de Step
        # -----------------------------
        for funnel_def in FUNNELS:
            funnel, _ = Funnel.objects.update_or_create(
                slug=funnel_def["slug"],
                defaults={"name": funnel_def["name"], "description": funnel_def.get("description", "")},
            )
            self.stdout.write(f"Funnel upsert: {funnel.slug}")

            # Crear plantilla por cada Step global
            for step_slug, step in steps_map.items():
                MsgTemplate.objects.update_or_create(
                    slug=f"{funnel.slug}_{step.slug}_template",
                    funnel=funnel,
                    step=step,
                    step_action=None,
                    defaults={
                        "name": f"Template {funnel.slug}/{step.slug}",
                        "content": f"Contenido de ejemplo para {funnel.slug} -> {step.slug}"
                    }
                )
            self.stdout.write(self.style.SUCCESS(f"Templates created for funnel {funnel.slug}"))

        # -----------------------------
        # 5) Crear plantillas para StepActions (global / default funnel)
        # -----------------------------
        default_funnel = Funnel.objects.get(slug="default")

        for action_slug, action in actions_map.items():
            MsgTemplate.objects.update_or_create(
                slug=f"{default_funnel.slug}_{action_slug}_template",
                funnel=default_funnel,
                step=None,
                step_action=action,  # FK explícita
                defaults={
                    "name": f"Template {default_funnel.slug}/{action_slug}",
                    "content": f"Contenido de ejemplo para Action {action_slug} en funnel default"
                }
            )

        self.stdout.write(self.style.SUCCESS("StepAction templates created for default funnel"))

        self.stdout.write(self.style.SUCCESS("=== Seed COMPLETE ==="))
