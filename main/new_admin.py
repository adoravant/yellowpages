@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    ordering = ("orden",)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(StepAction)
class StepActionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "step_origen", "step_destino", "tipo", "advance")
    list_filter = ("tipo", "step_origen")
    search_fields = ("nombre",)



class BaseStepLeadAdmin(admin.ModelAdmin):
    actions = []

    step_number = None  # asignar en subclasses

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(step__orden=self.step_number)

    def get_actions(self, request):
        actions = super().get_actions(request)

        # limpiar todas las acciones no locales
        allowed = [a.nombre for a in StepAction.objects.filter(step_origen__orden=self.step_number)]
        return {
            name: action
            for name, action in actions.items()
            if name in allowed
        }



def build_step_admin(step_number, paso_nombre):
    class StepAdmin(BaseStepLeadAdmin):
        step_number = step_number
        list_display = ("id", "name", "phone", "website", "updated_at")
        search_fields = ("name", "phone", "website")

    StepAdmin.__name__ = f"Step{step_number}Admin"
    admin.site.register(LeadFull, StepAdmin)

for step in Step.objects.all():
    build_step_admin(step.orden, step.nombre)

