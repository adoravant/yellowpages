from django.db import models

# ---------------------------------------------------------
# StepAction Manager + QuerySet
# ---------------------------------------------------------
class StepActionQuerySet(models.QuerySet):
    def ordered(self):
        return self.order_by("prioridad", "pk")

    def for_step(self, step):
        return self.filter(step=step).ordered()

    def next_after(self, action):
        # alternativa más robusta usando pk y prioridad
        return self.filter(step=action.step, prioridad__gte=action.prioridad).exclude(pk=action.pk).ordered().first()


class StepActionManager(models.Manager):
    def get_queryset(self):
        return StepActionQuerySet(self.model, using=self._db)

    def next_for(self, action):
        return self.get_queryset().next_after(action)

    def first_for_step(self, step):
        return self.get_queryset().for_step(step).first()


# ---------------------------------------------------------
# MsgTemplate Manager + QuerySet
# ---------------------------------------------------------
class MsgTemplateQuerySet(models.QuerySet):
    def for_action_and_funnel(self, action, funnel):
        return self.filter(action_slug=action.slug, funnel=funnel)

    def for_action(self, action):
        return self.filter(action_slug=action.slug, funnel__isnull=True)

    def for_step_and_funnel(self, step, funnel):
        return self.filter(step=step, funnel=funnel, action_slug__isnull=True)

    def for_step(self, step):
        return self.filter(step=step, funnel__isnull=True, action_slug__isnull=True)

    def for_funnel(self, funnel):
        return self.filter(funnel=funnel, step__isnull=True, action_slug__isnull=True)

    def global_templates(self):
        return self.filter(funnel__isnull=True, step__isnull=True, action_slug__isnull=True)


class MsgTemplateManager(models.Manager):
    def get_queryset(self):
        return MsgTemplateQuerySet(self.model, using=self._db)

    def pick_best(self, funnel=None, step=None, action=None):
        qs = self.get_queryset()
        if action and funnel:
            t = qs.for_action_and_funnel(action, funnel).first()
            if t: return t
        if action:
            t = qs.for_action(action).first()
            if t: return t
        if step and funnel:
            t = qs.for_step_and_funnel(step, funnel).first()
            if t: return t
        if step:
            t = qs.for_step(step).first()
            if t: return t
        if funnel:
            t = qs.for_funnel(funnel).first()
            if t: return t
        return qs.global_templates().first()
