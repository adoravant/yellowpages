# console/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import EventTypeConfig, ActionTypeConfig, MsgTemplate, TriggerRule
from .models import MatrixScenario, MatrixButtonConfig
@admin.register(MatrixButtonConfig)
class MatrixButtonConfigAdmin(admin.ModelAdmin):
    # Quitamos 'event_type' de la lista si el 'slug' ya nos dice qué es
    list_display = ('label', 'display_slug', 'flavor', 'next_stage', 'active')
    list_filter = ('next_stage', 'event_type__slug', 'active', "flavor")
    search_fields = ('label', 'flavor', 'event_type__slug')
    list_editable = ('active',)

    @admin.display(description="Slug / Tipo")
    def display_slug(self, obj):
        # Mostramos solo el slug del tipo de evento, sin el nombre de la clase
        return obj.event_type.slug

    @admin.display(description="Icono")
    def display_icon(self, obj):
        return format_html('<code>{}</code>', obj.icon) if obj.icon else "-"

@admin.register(MatrixScenario)
class MatrixScenarioAdmin(admin.ModelAdmin):
    list_display = ('stage', 'display_matrix_status')
    list_filter = ('stage',)
    
    # Agrupamos por filas pero con etiquetas limpias
    fieldsets = (
        (None, {
            'fields': ('stage', )
        }),
        ('FILA 1: AVANCE', {
            'fields': ('slot_adv_1', 'slot_adv_2', 'slot_adv_3'),
        }),
        ('FILA 2: STALL (OBJECIONES)', {
            'fields': ('slot_sta_1', 'slot_sta_2', 'slot_sta_3'),
        }),
        ('FILA 3: CLOSE (SALIDAS)', {
            'fields': ('slot_out_1', 'slot_out_2', 'slot_out_3'),
        }),
    )

    @admin.display(description="Estado")
    def display_matrix_status(self, obj):
        slots = [
            obj.slot_adv_1, obj.slot_adv_2, obj.slot_adv_3,
            obj.slot_sta_1, obj.slot_sta_2, obj.slot_sta_3,
            obj.slot_out_1, obj.slot_out_2, obj.slot_out_3
        ]
        filled = len([s for s in slots if s is not None])
        color = "#00ff88" if filled == 9 else "#ffcc00"
        return format_html('<b style="color: {};">{} / 9</b>', color, filled)

# =====================================================
# EVENT TYPE CONFIG
# =====================================================
@admin.register(EventTypeConfig)
class EventTypeConfigAdmin(admin.ModelAdmin):
    list_display = (
        "get_status_icon",
        "slug",
        "category",
        "should_alert",
        "alert_priority",
        "allowed_auto",
        "max_consumes",
        "active",
    )
    list_editable = (
        "should_alert",
        "alert_priority",
        "allowed_auto",
        "max_consumes",
        "active",
    )
    list_filter = ("category", "should_alert", "allowed_auto", "active")
    search_fields = ("slug", "name")
    ordering = ("category", "-alert_priority")
    list_per_page = 100

    @admin.display(description="Mode")
    def get_status_icon(self, obj):
        color = "#22c55e" if obj.should_alert else "#475569"
        return format_html(
            '<span style="height:10px; width:10px; background-color:{}; border-radius:50%; display:inline-block; border: 1px solid rgba(255,255,255,0.2);"></span>',
            color
        )

# =====================================================
# ACTION TYPE CONFIG
# =====================================================
@admin.register(ActionTypeConfig)
class ActionTypeConfigAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "function_name", "channel", "active")
    list_filter = ("active", "channel")
    search_fields = ("slug", "name", "function_name")
    list_editable = ("active",)

# =====================================================
# MESSAGE TEMPLATES
# =====================================================
@admin.register(MsgTemplate)
class MsgTemplateAdmin(admin.ModelAdmin):
    list_display = ("slug", "channel", "subject", "active")
    list_filter = ("channel", "active")
    search_fields = ("slug", "subject")
    list_editable = ("active",)

# =====================================================
# TRIGGER RULE
# =====================================================
@admin.register(TriggerRule)
class TriggerRuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "mode",
        "event_type",
        "action_to_trigger",
        "template",
        "priority",
        "active",
    )
    list_filter = ("mode", "active", "event_type")
    search_fields = ("name", "event_type__slug", "action_to_trigger__slug")
    list_editable = ("priority", "active")
    ordering = ("-priority",)

    # Personalización visual opcional para triggers activos
    @admin.display(description="Active")
    def is_active_icon(self, obj):
        color = "#22c55e" if obj.active else "#f43f5e"
        return format_html(
            '<span style="height:10px; width:10px; background-color:{}; border-radius:50%; display:inline-block; border: 1px solid rgba(0,0,0,0.2);"></span>',
            color
        )