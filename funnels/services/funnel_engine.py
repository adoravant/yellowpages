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
