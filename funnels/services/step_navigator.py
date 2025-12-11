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

