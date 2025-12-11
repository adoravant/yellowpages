# funnels/management/commands/seed_funnels.py
from django.core.management.base import BaseCommand
from funnels.models import Funnel, Step, StepAction, MsgTemplate

class Command(BaseCommand):
    help = "Crea funnels, steps, step actions y plantillas dummy"

    def handle(self, *args, **options):
        # ---------------------------------
        # 1️⃣ Funnels
        # ---------------------------------
        funnels_data = [
            {"nombre": "SSL", "descripcion": "Errores SSL"},
            {"nombre": "DOWN", "descripcion": "Página caída"},
            {"nombre": "TIMEOUT", "descripcion": "Problemas de carga"},
            {"nombre": "WEAK", "descripcion": "Página fea"},
            {"nombre": "STRONG", "descripcion": "Página buena"},
            {"nombre": "CORES", "descripcion": "Renta página"},
            {"nombre": "NONE", "descripcion": "No tiene página"},
        ]
        funnels = []
        for f in funnels_data:
            funnel, _ = Funnel.objects.get_or_create(
                nombre=f["nombre"],
                defaults={"descripcion": f.get("descripcion")}
            )
            funnels.append(funnel)
        self.stdout.write(self.style.SUCCESS("Funnels creados"))

        # ---------------------------------
        # 2️⃣ Steps universales (funnel=None)
        # ---------------------------------
        steps_data = [
            {"order": 1, "name": "Validación"},
            {"order": 2, "name": "Diagnóstico"},
            {"order": 3, "name": "Oferta"},
            {"order": 4, "name": "Seguimiento"},
            {"order": 5, "name": "Cierre"},
        ]
        steps = []
        for s in steps_data:
            step, _ = Step.objects.get_or_create(
                order=s["order"],
                name=s["name"],
                funnel=None  # <-- Step universal
            )
            steps.append(step)
        self.stdout.write(self.style.SUCCESS("Steps universales creados"))

        # ---------------------------------
        # 3️⃣ StepActions universales
        # ---------------------------------
        step_actions_data = {
            "Validación": [
                ("avanzar", "Avanzar al siguiente Step"),
                ("presentacion", "Presentación"),
                ("not_owner", "No es responsable"),
                ("equivocado", "Número equivocado"),
                ("manual", "Manual/otros"),
            ],
            "Diagnóstico": [
                ("objection", "Objeción del prospecto"),
                ("not_interested", "No interesado"),
            ],
            "Oferta": [
                ("objection", "Objeción del prospecto"),
                ("not_interested", "No interesado"),
                ("avanzar", "Avanzar al siguiente Step"),
            ],
            "Seguimiento": [
                ("recordatorio", "Recordatorio"),
                ("presion", "Presión"),
                ("descuento", "Oferta de descuento"),
                ("llamada", "Llamada de seguimiento"),
            ],
            "Cierre": [
                ("numero_equivocado", "Número equivocado"),
                ("maybe_later", "Tal vez más tarde"),
                ("not_owner", "No es responsable"),
                ("not_interested", "No interesado"),
            ],
        }

        for step in steps:
            actions = step_actions_data.get(step.name, [])
            for prioridad, (slug, nombre) in enumerate(actions, start=1):
                StepAction.objects.get_or_create(
                    step=step,
                    slug=slug,
                    defaults={
                        "nombre": nombre,
                        "type": slug,
                        "prioridad": prioridad,
                        "avanzar": slug == "avanzar",
                        "funnel": None  # <-- acción universal
                    }
                )
        self.stdout.write(self.style.SUCCESS("StepActions universales creados"))

        # ---------------------------------
        # 4️⃣ Plantillas dummy (por step y por action)
        # ---------------------------------
        for step in steps:
            # plantilla por step
            MsgTemplate.objects.get_or_create(
                step=step,
                nombre=f"Plantilla {step.name}",
                slug=f"plantilla_{step.name.lower()}",
                contenido=f"Contenido de prueba para step {step.name}",
                funnel=None
            )
            # plantilla por action
            for action in step.actions.all():
                MsgTemplate.objects.get_or_create(
                    step=step,
                    action_slug=action.slug,
                    nombre=f"Plantilla {action.nombre}",
                    slug=f"plantilla_{step.name.lower()}_{action.slug}",
                    contenido=f"Contenido de prueba para action {action.nombre} del step {step.name}",
                    funnel=None
                )
        self.stdout.write(self.style.SUCCESS("Plantillas universales creadas"))
