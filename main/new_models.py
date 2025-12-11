class LeadFull(models.Model):
    # -------------------------
    # Datos del lead
    # -------------------------
    name = models.CharField(max_length=200, null=True, blank=True)
    owner = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    street_address = models.CharField(max_length=500, null=True, blank=True)
    opening_hours = models.CharField(max_length=500, null=True, blank=True)
    email = models.CharField(unique=True, max_length=200, null=True, blank=True)
    phone = models.CharField(unique=True, max_length=200, null=True, blank=True)
    phone_type = models.CharField(max_length=200, null=True, blank=True)
    website = models.CharField(max_length=250, null=True, blank=True)
    whatsapp_url = models.CharField(max_length=500, null=True, blank=True)
    redes_sociales = models.JSONField(null=True, blank=True)
    detalle_url = models.CharField(max_length=500, null=True, blank=True)
    logo_url = models.CharField(max_length=500, null=True, blank=True)
    website_type = models.CharField(max_length=200, null=True, blank=True)
    website_status = models.CharField(max_length=200, null=True, blank=True)
    rubros = models.JSONField(null=True, blank=True)
    tiendas = models.JSONField(null=True, blank=True)
    intents = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -------------------------
    # Estado del funnel
    # -------------------------
    step = models.ForeignKey(
        Step, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Step actual en el funnel"
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return str(self.name)



class Template(models.Model):
    nombre = models.CharField(max_length=200)
    contenido = models.TextField()

    def __str__(self):
        return self.nombre


class Step(models.Model):
    orden = models.PositiveSmallIntegerField(unique=True)
    nombre = models.CharField(max_length=200)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.orden}. {self.nombre}"


class StepAction(models.Model):
    TIPOS = [
        ("transition", "Transición"),
        ("detour", "Desvío / Mensaje intermedio"),
    ]

    step_origen = models.ForeignKey(
        Step, related_name="actions", on_delete=models.CASCADE
    )

    step_destino = models.ForeignKey(
        Step, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="A dónde va después (si corresponde)"
    )

    nombre = models.CharField(max_length=200)

    plantilla = models.ForeignKey(
        Template, null=True, blank=True, on_delete=models.SET_NULL
    )

    tipo = models.CharField(max_length=20, choices=TIPOS)

    advance = models.BooleanField(
        default=False,
        help_text="Si es detour y advance=True, después avanza al destino"
    )

    class Meta:
        ordering = ["step_origen__orden", "nombre"]

    def __str__(self):
        return f"{self.step_origen} → {self.nombre}"

