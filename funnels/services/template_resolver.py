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
