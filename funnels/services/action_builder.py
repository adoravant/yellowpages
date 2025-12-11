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

