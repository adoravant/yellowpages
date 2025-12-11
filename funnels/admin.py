# admin.py
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    Funnel,
    Step,
    StepAction,
    StepActionRule,
    MsgTemplate,
    LeadFunnelState,
)


# ---------------------------------------------------------------------
# Inline: MsgTemplate dentro del Funnel
# ---------------------------------------------------------------------
class MsgTemplateInline(admin.TabularInline):
    model = MsgTemplate
    extra = 0
    fields = ("step", "step_action", "content")
    show_change_link = True
    ordering = ("slug",)


# ---------------------------------------------------------------------
# Funnel Admin
# ---------------------------------------------------------------------
@admin.register(Funnel)
class FunnelAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "total_steps", "updated_at")
    inlines = [MsgTemplateInline]
    search_fields = ("slug", "name")
    ordering = ("slug",)

    def total_steps(self, obj):
        return MsgTemplate.objects.filter(funnel=obj).values("step").distinct().count()
    total_steps.short_description = "Steps"


# ---------------------------------------------------------------------
# StepActionRule Inline (para Step)
# ---------------------------------------------------------------------
class StepActionRuleInline(admin.TabularInline):
    model = StepActionRule
    extra = 0
    fields = ("action", "appearance")
    ordering = ("action__priority",)


# ---------------------------------------------------------------------
# Step Admin (global)
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# Inline: MsgTemplate dentro de StepAction
# ---------------------------------------------------------------------
class StepActionTemplateInline(admin.TabularInline):
    model = MsgTemplate
    fk_name = "step_action"
    extra = 0
    fields = ("funnel", "content")
    show_change_link = True
    ordering = ("slug",)


# ---------------------------------------------------------------------
# StepAction Admin (catálogo global)
# ---------------------------------------------------------------------
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


# ---------------------------------------------------------------------
# StepActionRule Admin
# ---------------------------------------------------------------------
@admin.register(StepActionRule)
class StepActionRuleAdmin(admin.ModelAdmin):
    list_display = (
        "step",
        "action",
        "appearance",
    )
    list_filter = ("step", "action")
    search_fields = ("step__slug", "action__slug")
    ordering = ("step__order", "action__priority")


# ---------------------------------------------------------------------
# MsgTemplate Admin
# ---------------------------------------------------------------------
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

    def step_or_action(self, obj):
        if obj.step:
            return obj.step.slug
        if obj.step_action:
            return obj.step_action.slug
        return "-"
    step_or_action.short_description = "Step / Action"


# ---------------------------------------------------------------------
# LeadFunnelState Admin
# ---------------------------------------------------------------------
@admin.register(LeadFunnelState)
class LeadFunnelStateAdmin(admin.ModelAdmin):
    list_display = (
        "lead",
        "funnel",
        "current_step",
        "status",
        "suggested_action",
        "updated_at",
    )
    list_filter = ("funnel", "status", "current_step")
    search_fields = ("lead__name", "status")
    ordering = ("-updated_at",)

    readonly_fields = (
        "used_actions",
        "discarded_actions",
        "current_pool",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Lead", {"fields": ("lead", "funnel", "status")}),
        ("Current", {"fields": ("current_step", "suggested_action")}),
        ("Actions", {"fields": ("used_actions", "discarded_actions", "current_pool")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
