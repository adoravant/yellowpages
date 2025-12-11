from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator




# -------------------------------------------------------------------
# #DATOS LEGACY A BORRAR
# -------------------------------------------------------------------
class Dato(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    phone_type = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    contacted = models.IntegerField(default=0)
    website = models.CharField(max_length=250, null=True, blank=True)
    website_status = models.CharField(max_length=200, null=True, blank=True)
    website_type = models.CharField(max_length=200, null=True, blank=True)
    search_tag = models.CharField(max_length=200, null=True, blank=True)


# -------------------------------------------------------------------
# LEADS LEGACY A BORRAR
# -------------------------------------------------------------------
class Lead(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(unique=True, max_length=200, null=True, blank=True)
    phone_type = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    contacted = models.IntegerField(default=0)
    website = models.CharField(max_length=250, null=True, blank=True)
    website_type = models.CharField(max_length=200, null=True, blank=True)
    website_status = models.CharField(max_length=200, null=True, blank=True)
    search_tag = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.name)




class LeadFull(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    owner = models.CharField(max_length=200, null=True, blank=True)

    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    street_address = models.CharField(max_length=500, null=True, blank=True)

    email = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    alt_phone = models.CharField(max_length=50, blank=True, null=True)
    phone_type = models.CharField(max_length=200, null=True, blank=True)

    website = models.CharField(max_length=250, null=True, blank=True, validators=[URLValidator()])
    whatsapp_url = models.CharField(max_length=500, null=True, blank=True)

    website_type = models.CharField(max_length=200, null=True, blank=True)
    website_status = models.CharField(max_length=200, null=True, blank=True)

    redes_sociales = models.JSONField(null=True, blank=True)
    detalle_url = models.CharField(max_length=500, null=True, blank=True)
    logo_url = models.CharField(max_length=500, null=True, blank=True)
    rubros = models.JSONField(null=True, blank=True)
    tiendas = models.JSONField(null=True, blank=True)

    intents = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name or f"LeadFull #{self.pk}"
        




class DiagnosticoTecnico(models.Model):
    lead = models.ForeignKey(LeadFull, on_delete=models.CASCADE, related_name="diagnosticos")
    ERROR_TYPES = [("SSL", "SSL"), ("DOWN", "Down / Caída"), ("TIMEOUT", "Timeout")]
    error_type = models.CharField(max_length=20, choices=ERROR_TYPES, default="DOWN")

    domain = models.CharField(max_length=255, null=True, blank=True)
    report_date = models.DateTimeField(default=timezone.now)
    screenshot_path = models.CharField(max_length=500, null=True, blank=True)

    # SSL extras
    ssl_estado = models.CharField(max_length=100, null=True, blank=True)
    ssl_issue_type = models.CharField(max_length=200, null=True, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    days_left = models.IntegerField(null=True, blank=True)
    final_url = models.CharField(max_length=500, null=True, blank=True)

    # DOWN
    down_detected_at = models.DateTimeField(null=True, blank=True)
    down_duration_seconds = models.IntegerField(null=True, blank=True)
    response_code = models.IntegerField(null=True, blank=True)

    # TIMEOUT
    timeout_seconds = models.FloatField(null=True, blank=True)
    timeout_url = models.CharField(max_length=500, null=True, blank=True)

    stack_detectado = models.JSONField(null=True, blank=True)
    notas = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.error_type} - {self.domain}"

