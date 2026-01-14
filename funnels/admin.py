# admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone

from .models import (
    Funnel,
    Step,
    StepAction,
    StepActionRule,
    MsgTemplate,
    LeadFunnelState,
)


# =====================================================================
# INLINE: Templates dentro de Funnel
# =====================================================================
class MsgTemplateInline(admin.TabularInline):
    model = MsgTemplate
    extra = 0
    fields = ("step", "step_action", "content")
    show_change_link = True
    ordering = ("slug",)


# =====================================================================
# Funnel Admin
# =====================================================================
@admin.register(Funnel)
class FunnelAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "total_steps", "updated_at")
    inlines = [MsgTemplateInline]
    search_fields = ("slug", "name")
    ordering = ("slug",)

    def total_steps(self, obj):
        return MsgTemplate.objects.filter(funnel=obj).values("step").distinct().count()
    total_steps.short_description = "Steps"


# =====================================================================
# StepActionRule Inline para Step
# =====================================================================
class StepActionRuleInline(admin.TabularInline):
    model = StepActionRule
    extra = 0
    fields = ("action", "appearance")
    ordering = ("action__priority",)


# =====================================================================
# Step Admin
# =====================================================================
@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "order", "used_in_funnels", "rules_count")
    search_fields = ("slug", "name")
    ordering = ("order",)
    inlines = [StepActionRuleInline]

    def used_in_funnels(self, obj):
        funnels = MsgTemplate.objects.filter(step=obj).values_list("funnel__slug", flat=True).distinct()
        return ", ".join(funnels) if funnels else "-"
    used_in_funnels.short_description = "Funnels"

    def rules_count(self, obj):
        return obj.stepactionrule_set.count()
    rules_count.short_description = "Rules"


# =====================================================================
# StepAction Templates Inline
# =====================================================================
class StepActionTemplateInline(admin.TabularInline):
    model = MsgTemplate
    fk_name = "step_action"
    extra = 0
    fields = ("funnel", "content")
    show_change_link = True
    ordering = ("slug",)


# =====================================================================
# StepAction Admin
# =====================================================================
@admin.register(StepAction)
class StepActionAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "name",
        "priority",
        "produce_close",
        "close_status",
        "used_in_steps",
    )
    search_fields = ("slug", "name")
    list_filter = ("produce_close",)
    ordering = ("priority",)
    inlines = [StepActionTemplateInline]

    def used_in_steps(self, obj):
        steps = StepActionRule.objects.filter(action=obj).values_list("step__slug", flat=True)
        return ", ".join(steps) if steps else "-"
    used_in_steps.short_description = "Used in Steps"


# =====================================================================
# StepActionRule Admin
# =====================================================================
@admin.register(StepActionRule)
class StepActionRuleAdmin(admin.ModelAdmin):
    list_display = ("step", "action", "appearance")
    list_filter = ("step", "action")
    search_fields = ("step__slug", "action__slug")
    ordering = ("step__order", "action__priority")


# =====================================================================
# MsgTemplate Admin
# =====================================================================
class StepActionFilter(admin.SimpleListFilter):
    title = 'Step Action'
    parameter_name = 'step_action'

    def lookups(self, request, model_admin):
        actions = StepAction.objects.all()
        return [(a.id, a.name) for a in actions]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(step_action_id=self.value())
        return queryset


@admin.register(MsgTemplate)
class MsgTemplateAdmin(admin.ModelAdmin):
    list_display = ("slug", "content", "funnel")
    search_fields = ("slug", "name", "content")
    list_filter = ("funnel", "step", StepActionFilter)
    ordering = ("slug",)


# =====================================================================
# LEADFUNNELSTATE — LIST VIEW OPERATIVO CON BOTONES
# =====================================================================
@admin.register(LeadFunnelState)
class LeadFunnelStateAdmin(admin.ModelAdmin):

    # ------------------------------
    # LIST VIEW con botones
    # ------------------------------
    list_display = (
        "id",
        "mock_message",
        "actions_inline",
        "funnel_slug",
        "step_order",
        
    )

    list_display_links = ("id",)  # NO romper botones

    search_fields = ("lead__name",)
    list_filter = ("funnel", "current_step", "status")
    ordering = ("-updated_at",)

    readonly_fields = (
        "used_actions",
        "discarded_actions",
        "current_pool",
        "created_at",
        "updated_at",
    )

    # ===============================
    # CAMPOS AUXILIARES
    # ===============================

    
    def actualizado(self, obj):
        if not obj.updated_at:
            return "-"
        dt = timezone.localtime(obj.updated_at)
        return dt.strftime("%d/%m/%y %I:%M %p").lower().replace("am", "a.m.").replace("pm", "p.m.")

        actualizado.short_description = "Updated"
    
    
    @admin.display(description="Lead")
    def lead_name(self, obj):
        return obj.lead.name if obj.lead else "-"

    @admin.display(description="Funnel")
    def funnel_slug(self, obj):
        return obj.funnel.slug

    @admin.display(description="Step")
    def step_order(self, obj):
        return obj.current_step.order if obj.current_step else "-"

    @admin.display(description="Mensaje")
    def incoming_message(self, obj):
        msg = getattr(obj.lead, "last_message", None)
        if not msg:
            return "-"
        msg = msg.replace("\n", " ")
        return (msg[:60] + "...") if len(msg) > 60 else msg

    # ===============================
    # ACCIONES BOTONES INLINE
    # ===============================
    @admin.display(description="Acciones")
    def actions_inline(self, obj):
        if not obj.current_step:
            return "-"

        rules = StepActionRule.objects.filter(
            step=obj.current_step
        ).select_related("action")

        html = '<div class="button-grid">'
        for rule in rules:
            action = rule.action
            url = reverse("admin:run_funnel_action", args=[obj.pk, action.pk])
            html += (
                f'<a href="{url}" '
                f'style="flex: 1 1 calc(25% - 4px); '  # 4 botones por fila
                f'padding:2px 6px; border-radius:4px; '
                f'margin:2px; background-color:#28a745; color:white; '
                f'text-decoration:none; display:inline-block; text-align:center; '
                f'font-size:11px;">'
                f'{action.slug}'
                '</a>'
            )
        html += "</div>"

        return mark_safe(html)


    # ===============================
    # LÓGICA DE EJECUCIÓN DE ACCIÓN
    # ===============================
    def run_action(self, request, state_id, action_id):
        state = get_object_or_404(LeadFunnelState, pk=state_id)
        action = get_object_or_404(StepAction, pk=action_id)

        # tu motor real:
        # ActionApplier.apply(state, action)

        # por ahora:
        state.mark_used(action.slug)

        self.message_user(request, f"Acción '{action.slug}' ejecutada.")
        return redirect(reverse("admin:funnels_leadfunnelstate_changelist"))

    
    
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                "run-action/<int:state_id>/<int:action_id>/",
                self.admin_site.admin_view(self.run_action),
                name="run_funnel_action",
            ),
        ]
        return custom_urls + urls