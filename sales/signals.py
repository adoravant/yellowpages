from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, Trigger
from .services import execute_auto_action

@receiver(post_save, sender=Event)
def event_dispatcher(sender, instance, created, **kwargs):
    # Solo reaccionamos a eventos nuevos y que NO sean de sistema/error
    if not created or instance.status != 'SUCCESS':
        return

    triggers = Trigger.objects.filter(milestone_tag=instance.type, active=True)

    for trigger in triggers:
        for auto_action in trigger.auto_actions.filter(active=True):
            execute_auto_action(auto_action, instance.lead)