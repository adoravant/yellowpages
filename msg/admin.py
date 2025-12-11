from django.contrib import admin
from .models import Conversation, Message
# Register your models here.

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("lead", "paso_actual", "canal", "ultima_interaccion")
    autocomplete_fields = ("lead", "paso_actual")


@admin.register(Message)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("conversation", "tipo", "timestamp", "plantilla", "step")
    autocomplete_fields = ("plantilla", "step")
