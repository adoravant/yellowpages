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

