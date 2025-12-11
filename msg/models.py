from django.db import models
from django.utils import timezone
from funnels.models import MsgTemplate, Step, StepAction, LeadFunnelState
from main.models import LeadFull



class Conversation(models.Model):
    lead = models.OneToOneField(LeadFull, on_delete=models.CASCADE, related_name="conversation")
    canal = models.CharField(max_length=50, blank=True, null=True)
    ultima_interaccion = models.DateTimeField(blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    def touch(self):
        self.ultima_interaccion = timezone.now()
        self.save(update_fields=["ultima_interaccion"])

    def __str__(self):
        return f"Conv {self.lead_id} - {self.paso_actual}"


class Message(models.Model):
    TIPOS = [("IN", "Entrada"), ("OUT", "Salida")]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="mensajes")
    tipo = models.CharField(max_length=3, choices=TIPOS)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    plantilla = models.ForeignKey(MsgTemplate, null=True, blank=True, on_delete=models.SET_NULL)
    action_slug = models.CharField(max_length=150, blank=True, null=True)
    step = models.ForeignKey(Step, null=True, blank=True, on_delete=models.SET_NULL)
    raw_meta = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.contenido[:40]}"




class ProviderConfig(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)  # whatsapp, email, sms
    api_key = models.CharField(max_length=500)
    base_url = models.CharField(max_length=500)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class DeliveryLog(models.Model):
    lead = models.ForeignKey("main.LeadFull", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)  # whatsapp / email
    destino = models.CharField(max_length=200)
    contenido = models.TextField()

    status = models.CharField(max_length=50)  # sent, delivered, read, failed
    proveedor = models.ForeignKey(ProviderConfig, null=True, on_delete=models.SET_NULL)
    raw_response = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} → {self.destino} [{self.status}]"


class MessageQueue(models.Model):
    lead = models.ForeignKey("main.LeadFull", on_delete=models.CASCADE)

    # YA NO APUNTAMOS A funnels.Template
    # Solo guardamos el texto final renderizado.
    contenido = models.TextField()

    tipo = models.CharField(max_length=50)  # whatsapp / email
    scheduled_for = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tipo} queued for {self.lead}"
