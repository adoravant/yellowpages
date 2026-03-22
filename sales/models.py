from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


# Importamos los modelos de configuración del otro archivo
from engine.models import EventTypeConfig, ActionTypeConfig, MsgTemplate, TriggerRule

from functions import FUNCTIONS_AVAILABLE
from constants import (
    LEAD_STATUS_CHOICES,
    TASK_STATUS_CHOICES,
    TASK_EXECUTION_MODE_CHOICES,
    COMMUNICATION_CHANNEL_CHOICES,
)

class LeadProgress(models.Model):
    lead = models.OneToOneField(
        'main.LeadFull', # Asegura que el path sea correcto según tu app
        related_name="progress",
        on_delete=models.CASCADE
    )

    # --- HITOS (Columnas Vertebrales) ---
    validated = models.BooleanField(default=False)
    pain      = models.BooleanField(default=False)
    interest  = models.BooleanField(default=False)
    capacity  = models.BooleanField(default=False)
    offer     = models.BooleanField(default=False)
    call      = models.BooleanField(default=False)
    meet      = models.BooleanField(default=False)
    quote     = models.BooleanField(default=False)
    contract  = models.BooleanField(default=False)

    # --- MEMORIA DE SABOR (JSON) ---
    milestones_context = models.JSONField(default=dict, blank=True)

    # --- MOTOR DE LA MATRIX ---
    last_event = models.ForeignKey(
        'Event', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="current_progress"
    )

    current_stage = models.CharField(
        max_length=50, 
        default="VALIDATION",
        db_index=True
    )

    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default="NEW")
    next_followup_at = models.DateTimeField(null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # En sales/models.py -> LeadProgress

    def _record(self, milestone_name, event):
        if not milestone_name: return
        
        # Prioridad al ID del botón (slug largo), si no, al slug del tipo
        full_slug = event.metadata.get('button_id') or event.event_type.slug
        flavor = full_slug.split('_')[-1] # Extrae 'money', 'tech', etc.
        
        self.milestones_context[milestone_name] = {
            "flavor": flavor,
            "full_slug": full_slug,
            "at": timezone.now().isoformat()
        }
        setattr(self, milestone_name, True)

    def get_current_iteration(self):
        """
        Cuenta cuántas veces el usuario respondió (REPLY) 
        estando en el stage actual.
        """
        return self.lead.events.filter(
            event_type__slug__icontains=f"reply_{self.current_stage.lower()}"
        ).count()

    def sync_from_event(self, event):
        """
        Lógica de cascada: Si el evento es un 'intent_pain', 
        sabemos que la validación ya ocurrió.
        """
        slug = event.event_type.slug
        
        if "intent_pain" in slug:
            self.validated = True
        elif "intent_call" in slug:
            self.validated = True
            self.pain = True
        
        # Guardamos el hito en el JSON context
        self._record(slug, event)
        self.save()

    @property
    def is_waiting_for_user(self):
        if not self.last_event: return True
        return self.last_event.event_type.slug.startswith("intent_")

    def __str__(self):
        return f"Progress: {self.lead.name} - {self.current_stage}"

class Event(models.Model):
    lead = models.ForeignKey('main.LeadFull', related_name="events", on_delete=models.CASCADE)
    event_type = models.ForeignKey(EventTypeConfig, on_delete=models.PROTECT)
    channel = models.CharField(max_length=50, choices=COMMUNICATION_CHANNEL_CHOICES, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Event {self.event_type.slug} for {self.lead.name}"

class Task(models.Model):
    lead = models.ForeignKey('main.LeadFull', related_name="tasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    action_type = models.ForeignKey(ActionTypeConfig, on_delete=models.PROTECT)
    template = models.ForeignKey(MsgTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Campo real para persistencia, se puede autopoblar del template
    task_channel = models.CharField(max_length=20, choices=COMMUNICATION_CHANNEL_CHOICES, null=True)

    mode = models.CharField(max_length=10, choices=TASK_EXECUTION_MODE_CHOICES, default="AUTO")
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default="pending", db_index=True)
    execute_at = models.DateTimeField(db_index=True)
    payload = models.JSONField(blank=True, null=True)
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    trigger_rule = models.ForeignKey("engine.TriggerRule", null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")

    class Meta:
        ordering = ["execute_at"]

    def execute(self):
        fn = FUNCTIONS_AVAILABLE.get(self.action_type.function_name)
        if not fn:
            self.status = "failed"
            self.save()
            return
        try:
            fn(lead=self.lead, task=self, **(self.payload or {}))
            self.status = "success"
        except Exception as e:
            self.status = "failed"
        self.save()

# Modelos simples de soporte
class Alert(models.Model):
    lead = models.ForeignKey('main.LeadFull', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Note(models.Model):
    lead = models.ForeignKey('main.LeadFull', related_name="notes", on_delete=models.CASCADE)
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)