from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import LeadFull, DiagnosticoTecnico

from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import LeadFull, DiagnosticoTecnico
from sales.models import Event


@admin.register(LeadFull)
class LeadFullAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone_link",
        "name",
        "phone",
        "whatsapp_link",
        "detalle_url_link",
        "website_link",
        "website_status",
        "email",
        
    )
    class EventInline(admin.TabularInline):
        model = Event
        extra = 0
        readonly_fields = ("tag", "channel", "metadata", "created_at")  # canal readonly
        can_delete = False
        ordering = ("-created_at",)
        search_fields = (
        "name",
        "phone",
        "email",
        "website",
        "website_type",
        "whatsapp_url",
    )
    #readonly_fields = ("tag", "channel", "metadata", "created_at")
    list_filter = ("website_status",)

    # ---- TELÉFONO ----
    def phone_link(self, obj):
        if not obj.phone:
            return "—"

        phone = (
            obj.phone
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )

        return mark_safe(
            f'<a style="font-size:15px" href="tel:{phone}">📞</a>'
        )

    phone_link.short_description = "llamar"
    phone_link.admin_order_field = "phone"

    # ---- WHATSAPP ----
    def whatsapp_link(self, obj):
        if not obj.whatsapp_url:
            return "—"

        return mark_safe(
            f'<a href="{obj.whatsapp_url}" target="_blank">wsapp</a>'
        )

    whatsapp_link.short_description = "Whats"
    whatsapp_link.admin_order_field = "whatsapp_url"

    # ---- DETALLE URL ----
    def detalle_url_link(self, obj):
        if not obj.detalle_url:
            return "—"

        return mark_safe(
            f'<a href="{obj.detalle_url}" target="_blank">cores</a>'
        )

    detalle_url_link.short_description = "Detalle"
    detalle_url_link.admin_order_field = "detalle_url"

    # ---- WEBSITE ----
    def website_link(self, obj):
        if not obj.website:
            return "—"

        return mark_safe(
            f'<a href="{obj.website}" target="_blank">visitar</a>'
        )

    website_link.short_description = "Website"
    website_link.admin_order_field = "website"


@admin.register(DiagnosticoTecnico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ("lead", "error_type", "domain", "created_at")
    list_filter = ("error_type",)

