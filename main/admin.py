from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import LeadFull, DiagnosticoTecnico


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
        "logo_url"
    )
    search_fields = (
        "name",
        "phone",
        "email",
        "website",
        "website_type",
        "whatsapp_url",
    )
    list_filter = ("website_status", )

    # ---- WHATSAPP LINK ----
    def whatsapp_link(self, obj):
        """
        Muestra un link que dice 'WhatsApp' usando obj.whatsapp_url real.
        """
        if not obj.whatsapp_url:
            return "—"

        return mark_safe(
            f'<a href="{obj.whatsapp_url}" target="_blank">WhatsApp</a>'
        )

    whatsapp_link.short_description = "WhatsApp"
    whatsapp_link.admin_order_field = "whatsapp_url"

    # ---- DETALLE URL ----
    def detalle_url_link(self, obj):
        if obj.detalle_url:
            return mark_safe(f'<a href="{obj.detalle_url}" target="_blank">Ver detalle</a>')
        return "—"
    detalle_url_link.short_description = "Detalle URL"
    detalle_url_link.admin_order_field = "detalle_url"

    # ---- WEBSITE ----
    def website_link(self, obj):
        if obj.website:
            return mark_safe(f'<a href="{obj.website}" target="_blank">{obj.website}</a>')
        return "—"
    website_link.short_description = "Website"
    website_link.admin_order_field = "website"

    # ---- FUNNEL ----
    def funnel_actual(self, obj):
        state = obj.funnels_state.first()
        return state.funnel.nombre if state else "—"
    funnel_actual.short_description = "Funnel"

    def phone_link(self, obj):
        if obj.phone:
            return mark_safe(
                f'<a href="/call-phone/?number={obj.phone}" target="_blank">Llamar</a>'
            )
        return "—"
    
    # main/admin.py
from django.utils.safestring import mark_safe

class LeadFullAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_link", ...)

    def phone_link(self, obj):
        if obj.phone:
            return mark_safe(
                f'<a href="/call-phone/?number={obj.phone}" target="_blank">Llamar</a>'
            )
        return "—"

    phone_link.short_description = "Teléfono"

    
    
    
@admin.register(DiagnosticoTecnico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ("lead", "error_type", "domain", "created_at")
    list_filter = ("error_type",)
