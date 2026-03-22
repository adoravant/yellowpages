from django.db import models
from django.utils import timezone
import copy


# Import desde root del proyecto
from functions import FUNCTIONS_AVAILABLE
from constants import (
    COMMUNICATION_CHANNEL_CHOICES,
    EVENT_CATEGORY_CHOICES, TRIGGER_MODE_CHOICES, WEBSITE_STATUS_SEGMENTS
)



from django.db import models

class MatrixButtonConfig(models.Model):
    STAGE_CHOICES = [
        ('VALIDATION', 'Validation'),
        ('PAIN', 'Pain / Offer'),
        ('CALL', 'Call / Meeting'),
        ('CLOSED', 'Closed'),
    ]
    
    # --- IDENTIDAD VISUAL ---
    label = models.CharField(max_length=50)
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Slug de Lucide o FontAwesome (ej: dollar-sign, cpu)"
    )
    
    # --- LÓGICA DE DISPARO (ADN DEL EVENTO) ---
    # Vinculado a tu EventTypeConfig (intent_validation, intent_pain, etc.)
    event_type = models.ForeignKey('EventTypeConfig', on_delete=models.CASCADE)
    
    # El 'sabor' específico de la respuesta (ej: money, who, not_owner)
    flavor = models.CharField(
        max_length=50, 
        help_text="Define la variante del evento. Ej: 'not_owner' en 'intent_validation'."
    )
    
    # --- LÓGICA DE ESTADO (EL SALTO) ---
    # Determina a qué etapa se mueve el Lead tras pulsar este botón
    next_stage = models.CharField(
        max_length=20, 
        choices=STAGE_CHOICES,
        help_text="A qué etapa salta el Lead al presionar este botón."
    )
    
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Estrategia - Botón de Matrix"

    def resolve_slug(self):
        """
        Genera el slug completo de intención. 
        Este es el 'ADN' que el Scenario usará como last_intent_slug.
        Ejemplo: 'intent_validation_who' o 'intent_pain_money'
        """
        return f"{self.event_type.slug}_{self.flavor}"

    def __str__(self):
        return f"{self.label} ({self.resolve_slug()}) -> {self.next_stage}"


class MatrixScenario(models.Model):
    # En qué etapa estamos parados (Contenedor grueso)
    stage = models.CharField(
        max_length=20, 
        choices=MatrixButtonConfig.STAGE_CHOICES
    )
    
    # EL SUBSTAGE (El contexto fino)
    # Es el resolve_slug() del botón que se apretó JUSTO ANTES.
    # Si es NULL, es el escenario inicial (Home) de la etapa.
    last_intent_slug = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        db_index=True,
        help_text="El slug del botón previo que activa este tablero. Si es nulo, es el inicio de etapa."
    )

    # --- GRID DE 9 SLOTS (ORGANIZADO POR FILAS PARA EL FRONT) ---
    
    # Fila 1: AVANCE (Hooks / Validadores)
    slot_adv_1 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_adv1")
    slot_adv_2 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_adv2")
    slot_adv_3 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_adv3")

    # Fila 2: STALL (Objeciones / Dudas)
    slot_sta_1 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_sta1")
    slot_sta_2 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_sta2")
    slot_sta_3 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_sta3")

    # Fila 3: CLOSE (Salidas / Descartes)
    slot_out_1 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_out1")
    slot_out_2 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_out2")
    slot_out_3 = models.ForeignKey(MatrixButtonConfig, on_delete=models.SET_NULL, null=True, blank=True, related_name="scenario_out3")

    class Meta:
        # Solo puede existir un tablero por cada contexto de intención en una etapa.
        #unique_together = ('stage', 'last_intent_slug')
        verbose_name = "Estrategia - Escenario de Matrix"

    def get_grid(self, filter_key=None):
        base_grid = {
            "AVANCE": [self.slot_adv_1, self.slot_adv_2, self.slot_adv_3],
            "STALL": [self.slot_sta_1, self.slot_sta_2, self.slot_sta_3],
            "CLOSE": [self.slot_out_1, self.slot_out_2, self.slot_out_3],
        }

        if not filter_key:
            return base_grid

        # 🔥 hook para filtros (por ahora simple)
        if filter_key == "SET_1":
            return base_grid

        if filter_key == "SET_2":
            return {
                "AVANCE": list(reversed(base_grid["AVANCE"])),
                "STALL": base_grid["STALL"],
                "CLOSE": base_grid["CLOSE"],
            }

        if filter_key == "SET_3":
            return {
                "AVANCE": base_grid["AVANCE"],
                "STALL": list(reversed(base_grid["STALL"])),
                "CLOSE": base_grid["CLOSE"],
            }

        return base_grid


    def build_matrix(self, view="ACTIVE"):
        
        def chunk_buttons(btns):
            btns = list(btns)
            return {
                "AVANCE": btns[0:3],
                "STALL": btns[3:6],
                "CLOSE": btns[6:9],
            }

        # ===== ACTIVE (lo que ya tenías) =====
        if view == "ACTIVE":
            return {
                "AVANCE": [self.slot_adv_1, self.slot_adv_2, self.slot_adv_3],
                "STALL": [self.slot_sta_1, self.slot_sta_2, self.slot_sta_3],
                "CLOSE": [self.slot_out_1, self.slot_out_2, self.slot_out_3],
            }

        # ===== resto de botones =====
        active_ids = [
            self.slot_adv_1_id, self.slot_adv_2_id, self.slot_adv_3_id,
            self.slot_sta_1_id, self.slot_sta_2_id, self.slot_sta_3_id,
            self.slot_out_1_id, self.slot_out_2_id, self.slot_out_3_id,
        ]

        remaining = MatrixButtonConfig.objects.exclude(id__in=active_ids)

        # opcional (recomendado a futuro)
        # remaining = remaining.order_by("priority")

        if view == "POOL_A":
            return chunk_buttons(remaining[:9])

        if view == "POOL_B":
            return chunk_buttons(remaining[9:18])

        return self.build_matrix("ACTIVE")



    def __str__(self):
        contexto = self.last_intent_slug if self.last_intent_slug else "INICIO"
        return f"[{self.stage}] Anterior: {contexto}"



class EventTypeConfig(models.Model):
    # Identificación
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(
        max_length=20,
        choices=EVENT_CATEGORY_CHOICES,
        default="OTHER",
        help_text="Categoría del evento para filtros y dashboard"
    )

    # Control de alertas
    should_alert = models.BooleanField(default=False)
    alert_priority = models.IntegerField(default=5)
    alert_title_template = models.CharField(max_length=200, blank=True, null=True)
    metadata_template = models.JSONField(blank=True, null=True)

    # Control de consumo y ciclo de vida
    active = models.BooleanField(default=True, help_text="Si el evento está habilitado")
    allowed_auto = models.BooleanField(default=True, help_text="Puede ser disparado automáticamente")
    unique_per_lead = models.BooleanField(default=True, help_text="Solo puede existir una vez por lead")
    max_consumes = models.IntegerField(default=1, help_text="Cantidad máxima de consumos permitidos por lead")
    ttl_hours = models.IntegerField(blank=True, null=True, help_text="Tiempo en horas que el evento es válido")

    def __str__(self):
        return f"EventTypeConfig: {self.slug}"

    def is_consumable(self, lead):
        """
        Verifica si el evento se puede consumir para un lead.
        Considera active, unique_per_lead, max_consumes y TTL.
        """
        if not self.active:
            return False
        if self.unique_per_lead and self.event_set.filter(lead=lead).exists():
            return False
        if self.max_consumes is not None:
            count = self.event_set.filter(lead=lead).count()
            if count >= self.max_consumes:
                return False
        if self.ttl_hours:
            from django.utils import timezone
            from datetime import timedelta
            threshold = timezone.now() - timedelta(hours=self.ttl_hours)
            if self.event_set.filter(lead=lead, created_at__gte=threshold).exists():
                return False
        return True

    class Meta:
        verbose_name = "Config - Tipo de Evento"
        verbose_name_plural = "EventTypes"


# =====================================================
# ACTION TYPES
# =====================================================

class ActionTypeConfig(models.Model):

    slug = models.SlugField(max_length=100, unique=True)

    name = models.CharField(max_length=100)

    function_name = models.CharField(
        max_length=100,
        choices=[(fn, fn) for fn in FUNCTIONS_AVAILABLE.keys()],
        help_text="Función registrada en functions.py"
    )

    channel = models.CharField(
        max_length=20,
        choices=COMMUNICATION_CHANNEL_CHOICES,
        null=True,
        blank=True,
        help_text="Canal asociado a la acción"
    )

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"ActionConfig: {self.slug} ({self.function_name})"

    class Meta:
        verbose_name = "Config - Tipo de Acción"
        verbose_name_plural = "ActionTypes"


# =====================================================
# MESSAGE TEMPLATES
# =====================================================
# =====================================================
# MESSAGE TEMPLATES
# =====================================================

class MsgTemplate(models.Model):
    
    # Tus segmentos específicos extraídos del website_status
   

    # El slug debe coincidir con el event_type.slug (ej: 'intent_pain_money')
    slug = models.SlugField(
        max_length=100, 
        db_index=True,
        help_text="Debe coincidir con el slug del EventTypeConfig"
    ) 

    channel = models.CharField(
        max_length=20,
        choices=COMMUNICATION_CHANNEL_CHOICES
    )

    # El campo clave para el despacho quirúrgico
    segment = models.CharField(
        max_length=20,
        choices=WEBSITE_STATUS_SEGMENTS,
        blank=True,
        null=True,
        help_text="Debe coincidir con el website_status del Lead"
    )

    subject = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Asunto (opcional, para Email)"
    )
    
    content = models.TextField(
        help_text="Contenido del mensaje. Soporta tags: {name}, {company}, etc."
    )
    
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Config - Plantilla"
        verbose_name_plural = "Templates"
        # Importante: permite tener la misma intención (slug) para distintos problemas (segments)
        unique_together = ('slug', 'segment', 'channel')

    def __str__(self):
        segment_display = self.get_segment_display() if self.segment else "GENERICO"
        return f"Template: {self.slug} | Segment: {segment_display} ({self.channel})"

# =====================================================
# TRIGGER RULE
# =====================================================

class TriggerRule(models.Model):

    name = models.SlugField(max_length=100, unique=True)

    # MODE
    mode = models.CharField(
        max_length=10,
        choices=TRIGGER_MODE_CHOICES,
        default="AUTO"
    )

    # WHEN
    event_type = models.ForeignKey(
        EventTypeConfig,
        on_delete=models.CASCADE,
        related_name="trigger_rules",
        null=True,
        blank=True
    )

    # IF
    conditions = models.JSONField(blank=True, null=True)

    # THEN
    action_to_trigger = models.ForeignKey(
        ActionTypeConfig,
        on_delete=models.CASCADE,
        related_name="trigger_rules"
    )

    template = models.ForeignKey(
        MsgTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trigger_rules"
    )

    payload_template = models.JSONField(blank=True, null=True)

    # CONTROL
    priority = models.IntegerField(default=1)
    max_runs = models.IntegerField(
        null=True,
        blank=True
    )

    cooldown_minutes = models.IntegerField(
        null=True,
        blank=True
    )

    should_alert = models.BooleanField(default=False)

    stop_processing = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Trigger: {self.name} ({self.event_type.slug if self.event_type else 'Manual'})"

    class Meta:
        verbose_name = "Config - Regla de Trigger"
        verbose_name_plural = "Triggers"
        ordering = ["-priority"]

    # =====================================================
    # CREATE TASK
    # =====================================================

    # Dentro de TriggerRule.create_task_for_lead
    def create_task_for_lead(self, lead, **kwargs):
        from sales.models import Task
        # 1. Intentamos buscar la plantilla exacta para el problema del lead
        template = MsgTemplate.objects.filter(
            slug=self.event_type.slug,      # 'intent_pain_money'
            segment=lead.website_status,   # 'web_caida'
            active=True
        ).first()

        # 2. Si no existe (fallback), buscamos una genérica (segment=None o null)
        if not template:
            template = MsgTemplate.objects.filter(
                slug=self.event_type.slug,
                segment__isnull=True,
                active=True
            ).first()

        # 3. Si sigue sin existir, usamos la que tiene el Trigger por defecto
        if not template:
            template = self.template

        # 4. Creamos la tarea con la mejor plantilla encontrada
        return Task.objects.create(
            lead=lead,
            template=template,
            # ... resto de campos
        )

    # =====================================================
    # CREATE ALERT
    # =====================================================

    def create_alert_for_lead(self, lead):

        from sales.models import Alert

        if self.event_type and self.event_type.should_alert:

            title_template = (
                self.event_type.alert_title_template
                or f"Alerta: {self.event_type.name}"
            )

            company_name = getattr(lead, "name", "Lead")

            Alert.objects.create(
                lead=lead,
                event_type=self.event_type,
                title=title_template.format(company=company_name),
                priority=self.event_type.alert_priority
            )