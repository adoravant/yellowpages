# app/models.py
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------
# Step (global catalogue)
# ---------------------------------------------------------------------
class Step(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.slug

    
    def next_step(self):
        """
        Devuelve el siguiente Step según el orden global.
        Retorna None si este era el último.
        """
        return (
            Step.objects
            .filter(order__gt=self.order)
            .order_by("order")
            .first()
        )

# ---------------------------------------------------------------------
# Funnel
# ---------------------------------------------------------------------
class Funnel(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.name

    # helpers
    def first_step(self):
        first_fs = self.ordered_steps.first()
        return first_fs.step if first_fs else None

    def get_step(self, slug):
        fs = self.ordered_steps.filter(step__slug=slug).first()
        return fs.step if fs else None



# ---------------------------------------------------------------------
# StepAction
# ---------------------------------------------------------------------
class StepAction(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255)
    priority = models.PositiveIntegerField(default=0)

    # Optional closing behaviour
    produce_close = models.BooleanField(default=False)
    close_status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ["priority"]

    def __str__(self):
        return self.slug


# ---------------------------------------------------------------------
# StepActionRule  (rules per step)
# ---------------------------------------------------------------------
class StepActionRule(models.Model):
    APPEARANCE_CHOICES = [
        ("once", "Appear once"),
        ("until_used", "Until used"),
        ("always", "Always appear"),
    ]

    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    action = models.ForeignKey(StepAction, on_delete=models.CASCADE)

    appearance = models.CharField(
        max_length=20,
        choices=APPEARANCE_CHOICES,
        default="once",
    )

    class Meta:
        unique_together = ("step", "action")
        ordering = ["action__priority"]

    def __str__(self):
        return f"{self.step.slug} :: {self.action.slug} ({self.appearance})"





# ---------------------------------------------------------------------
# MsgTemplate (can be global, step-specific, funnel-specific)
# ---------------------------------------------------------------------
class MsgTemplate(models.Model):
    slug = models.SlugField(max_length=100)

    funnel = models.ForeignKey(
        Funnel, null=True, blank=True,
        on_delete=models.CASCADE, related_name="templates"
    )
    step = models.ForeignKey(
        Step, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="templates"
    )

    step_action = models.ForeignKey(
        StepAction, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="templates"
    )
    
    name = models.CharField(max_length=200)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("slug", "funnel")
        ordering = ["slug"]

    def __str__(self):
        scope = "global"
        if self.funnel:
            scope = self.funnel.slug
        if self.step:
            scope = f"{scope}/{self.step.slug}"

        return f"{self.slug} ({scope})"










# ---------------------------------------------------------------------
# LeadFunnelState (runtime state of a lead inside a funnel)
# ---------------------------------------------------------------------

class LeadFunnelState(models.Model):
    """
    Estado del lead dentro del funnel.
    Compatible 100% con tu FunnelEngine, ActionResolver,
    ActionApplier, StepNavigator y Simulator.
    """
    mock_message = models.TextField(blank=True, null=True, help_text="TEMPORAL - MOCK")
    STATUS_CHOICES = [
        ("active", "Activo"),
        ("closed", "Cerrado"),
    ]

    lead = models.ForeignKey(
        "main.LeadFull",
        related_name="funnel_states",
        on_delete=models.CASCADE,
    )

    funnel = models.ForeignKey(
        Funnel,
        related_name="lead_states",
        on_delete=models.CASCADE,
    )

    current_step = models.ForeignKey(
        Step,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lead_states",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    used_actions = models.JSONField(default=list, blank=True)
    discarded_actions = models.JSONField(default=list, blank=True)

    # pool armada por PoolBuilder
    current_pool = models.JSONField(default=list, blank=True)

    # acción elegida por ActionResolver
    suggested_action = models.ForeignKey(
        StepAction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suggested_in_states",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"LeadFunnelState #{self.pk} ({self.lead})"

    # ---------------------------------------------------------------------
    # Métodos exigidos por tu motor
    # ---------------------------------------------------------------------
    def mark_used(self, slug):
        """
        Agrega una acción al historial de usadas.
        """
        used = set(self.used_actions or [])
        if slug not in used:
            used.add(slug)
            self.used_actions = list(used)
            self.save(update_fields=["used_actions", "updated_at"])

    def clear_discarded(self):
        """
        Se usa al avanzar de step → elimina las descartadas del step anterior.
        """
        if self.discarded_actions:
            self.discarded_actions = []
            self.save(update_fields=["discarded_actions", "updated_at"])

    def set_status_and_close(self, close_status):
        """
        Usado por ActionApplier al ejecutar una acción de cierre.
        """
        self.status = close_status
        self.current_pool = []
        self.suggested_action = None
        self.save(
            update_fields=["status", "current_pool", "suggested_action", "updated_at"]
        )