
# sales/admin.py

from django.contrib import admin
from .models import Task, Alert, LeadProgress, Event, Note


# =====================================================
# BASE ADMIN
# =====================================================

class AlwaysExpandedFiltersAdmin(admin.ModelAdmin):
    """
    Base admin para mantener filtros visibles en el sidebar.
    Compatible con Django admin clásico y Jazzmin.
    """
    pass


# =====================================================
# TASK
# =====================================================

@admin.register(Task)
class TaskAdmin(AlwaysExpandedFiltersAdmin):

    list_display = (
        "title",
        "lead",
        "status",
        "mode",
        "assigned_to_name",
        "execute_at",
        
    )

    list_filter = (
        "status",
        "mode",
    )

    search_fields = (
        "title",
        "lead__name",
        "action_type__name",
    )

    def assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.username
        return "-"
    assigned_to_name.short_description = "Assigned"


# =====================================================
# ALERT
# =====================================================

@admin.register(Alert)
class AlertAdmin(AlwaysExpandedFiltersAdmin):

    list_display = (
        "title",
        "lead",
        "resolved",
        "event_type_slug",
        "created_at",
    )

    list_filter = (
        "resolved",
        
    )

    search_fields = (
        "title",
        "lead__name",
        "event_type__slug",
    )

    def event_type_slug(self, obj):
        if obj.event_type:
            return obj.event_type.slug
        return "-"
    event_type_slug.short_description = "Event"


# =====================================================
# LEAD PROGRESS
# =====================================================

@admin.register(LeadProgress)
class LeadProgressAdmin(AlwaysExpandedFiltersAdmin):

    list_display = (
        "lead",
        "status",
        "milestones",
        "updated_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "lead__name",
    )

    def milestones(self, obj):

        steps = []

        if obj.validated:
            steps.append("VAL")

        if obj.pain:
            steps.append("PAIN")

        if obj.interest:
            steps.append("INT")

        if obj.capacity:
            steps.append("CAP")

        if obj.offer:
            steps.append("OFF")

        if obj.call:
            steps.append("CALL")

        if obj.meet:
            steps.append("MEET")

        if obj.quote:
            steps.append("QUOTE")

        if obj.contract:
            steps.append("CON")

        return " | ".join(steps)

    milestones.short_description = "Progress"


# =====================================================
# EVENT
# =====================================================

@admin.register(Event)
class EventAdmin(AlwaysExpandedFiltersAdmin):

    list_display = (
        "event_slug",
        "lead",
        "channel",
        "created_at",
    )

    list_filter = (
        "event_type__category",
        "channel",
    )

    search_fields = (
        "event_type__slug",
        "lead__name",
    )

    def event_slug(self, obj):
        return obj.event_type.slug

    event_slug.short_description = "Event"


# =====================================================
# NOTE
# =====================================================

@admin.register(Note)
class NoteAdmin(AlwaysExpandedFiltersAdmin):

    list_display = (
        "lead",
        "technician_name",
        "created_at",
        "content",
    )

    list_filter = (
        "technician",
    )

    search_fields = (
        "lead__name",
        "technician__username",
        "content",
    )

    def technician_name(self, obj):
        if obj.technician:
            return obj.technician.username
        return "-"

    technician_name.short_description = "Technician"
