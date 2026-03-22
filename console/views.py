# =====================================================
# console/views.py
# =====================================================
import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_POST, require_GET

# Models de Engine
from engine.models import (
    EventTypeConfig, TriggerRule, MsgTemplate, 
    ActionTypeConfig, MatrixScenario, MatrixButtonConfig
)
from main.models import LeadFull

# DSL Imports
from engine.dsl.context_registry import ContextResolver, CONTEXT_MAP
from engine.dsl.context_types import build_variable_schema, infer_type, TYPE_OPERATORS

from engine.matrix import MatrixResolver
from sales.models import LeadProgress



# =====================================================
# console/views.py
# =====================================================
import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST, require_GET
from engine.models import MatrixScenario, MatrixButtonConfig, EventTypeConfig
from main.models import LeadFull
from sales.models import LeadProgress
from engine.matrix import MatrixResolver, sync_matrix_from_config

# -----------------------------------------------------
# FILTER MATRIX (htmx/ajax)
# -----------------------------------------------------




def console_view(request, lead_id=None):
    """
    Consola de Mando Principal: Maneja la visualización de la Matrix táctica
    y la progresión de estados del Lead.
    """
    # 1. Obtención del Lead (Default al primero si no hay ID)
    if lead_id is None:
        lead = LeadFull.objects.first()
        if not lead:
            return render(request, 'error.html', {'msg': 'No hay leads en la base de datos'})
    else:
        lead = get_object_or_404(LeadFull, id=lead_id)

    # 2. Inicialización del Progreso
    # Si no existe, lo creamos. Forzamos un stage inicial si es un lead nuevo.
    progress, created = LeadProgress.objects.get_or_create(lead=lead)
    if created:
        progress.current_stage = "VALIDATION"
        progress.save()

    # 3. Sincronización Maestra
    # Mantenemos la base de datos alineada con tu STAGES_CONFIG de Python
    #sync_matrix_from_config()

    # 4. Recolección de Escenarios para Isotope
    # Queremos que el Front tenga las 3 matrices "base" (sin last_intent_slug)
    # para que el usuario pueda navegar entre ellas con los filtros.
    scenarios = MatrixScenario.objects.all()
    # 5. Determinación del Escenario Activo (Contextual)
    # Usamos el resolver para saber cuál es el tablero que "debería" estar viendo
    # según el último evento (ej: si hubo un reply_validation).
    resolver = MatrixResolver(progress)
    active_scenario = resolver.get_scenario()

    # 6. Debugging en Consola (Opcional, muy útil para trackear el flujo)
    print(f"--- DEBUG CONSOLE ---")
    print(f"Lead: {lead.name} | Stage Actual: {progress.current_stage}")
    print(f"Escenario Activo: {active_scenario}")
    if active_scenario:
        grid = active_scenario.get_grid()
        print(f"Botones AVANCE: {[b.label for b in grid['AVANCE'] if b]}")

    context = {
        'lead': lead,
        'progress': progress,
        'scenarios': scenarios,        # Para renderizar los 3 contenedores de Isotope
        'active_scenario': active_scenario, # Para marcar la clase .filter-active inicial
        'stage_display': dict(MatrixButtonConfig.STAGE_CHOICES).get(progress.current_stage)
    }

    return render(request, 'console/main/index.html', context)






@require_GET
def matrix_filter(request, filter_key):
    lead_id = request.GET.get("lead_id")
    if not lead_id:
        return HttpResponseBadRequest("Missing lead_id")

    try:
        lead = LeadFull.objects.get(id=lead_id)
    except LeadFull.DoesNotExist:
        return HttpResponseNotFound("Lead not found")

    progress = getattr(lead, "progress", None)
    if progress is None:
        return HttpResponseServerError("Lead has no progress data")

    resolver = MatrixResolver(progress)
    scenario = resolver.get_scenario()

    if not scenario:
        # fallback a escenario base
        scenario = MatrixScenario.objects.filter(stage=progress.current_stage, last_intent_slug__isnull=True).first()
    if not scenario:
        return HttpResponseServerError("No scenario found for this stage")

    # inicializa la grilla según filtro
    scenario.build_matrix(view=filter_key)

    return render(request, "console/partials/matrix_rows.html", {
        "scenario": scenario,
        "lead": lead
    })


# -----------------------------------------------------
# CLICK / ACTION MATRIX
# -----------------------------------------------------
@require_POST
def matrix_action(request):
    lead_id = request.POST.get("lead_id")
    action_id = request.POST.get("action_id")

    if not lead_id or not action_id:
        return HttpResponseBadRequest("Missing parameters")

    try:
        lead = LeadFull.objects.get(id=lead_id)
    except LeadFull.DoesNotExist:
        return HttpResponseNotFound("Lead not found")

    progress = getattr(lead, "progress", None)
    if progress is None:
        return HttpResponseServerError("Lead has no progress data")

    resolver = MatrixResolver(progress)
    result = resolver.execute_click(action_id)

    scenario = result.get("scenario")
    if not scenario:
        # fallback a escenario base
        scenario = MatrixScenario.objects.filter(stage=progress.current_stage, last_intent_slug__isnull=True).first()
    if not scenario:
        return HttpResponseServerError("Scenario missing after action")

    scenario.build_matrix(view="ACTIVE")

    return render(request, "console/partials/matrix_rows.html", {
        "scenario": scenario,
        "lead": lead
    })


# -----------------------------------------------------
# MAIN CONSOLE VIEW
# -----------------------------------------------------
# def console_view(request, lead_id=None):
#     if lead_id is None:
#         first_lead = LeadFull.objects.first()
#         if not first_lead:
#             return render(request, 'error.html', {'msg': 'No hay leads en la base de datos'})
#         lead_id = first_lead.id

#     lead = LeadFull.objects.get(id=lead_id)
#     progress, _ = LeadProgress.objects.get_or_create(lead=lead)
#     progress.current_stage = "VALIDATION"
#     progress.save()

#     # 🔹 sincroniza escenarios desde la configuración maestra
#     sync_matrix_from_config()

#     resolver = MatrixResolver(progress)
#     scenario = resolver.get_scenario()
#     print(scenario.stage, scenario.last_intent_slug)
#     print(scenario.slot_adv_1, scenario.slot_sta_1, scenario.slot_out_1)    

#     if not scenario:
#         # fallback a escenario base
#         scenario = MatrixScenario.objects.filter(stage=progress.current_stage, last_intent_slug__isnull=True).first()
#     if not scenario:
#         # último fallback: crea un escenario vacío en memoria solo para render
#         scenario = MatrixScenario(stage=progress.current_stage)

#     # 🔹 imprime debug si quieres
#     print("SCENARIO:", scenario)
#     print("GRID:", scenario.get_grid() if scenario else "None")

#     context = {
#         'lead': lead,
#         'progress': progress,
#         'scenario': scenario,  # siempre no-None con slots llenos o vacíos
#     }
#     for sc in MatrixScenario.objects.all():
#         print(sc, sc.slot_adv_1, sc.slot_sta_1, sc.slot_out_1)
#     return render(request, 'console/main/index.html', context)


def lead_detail_view(request, lead_id):
    # 1. Obtenemos el progreso del lead
    progress = get_object_or_404(LeadProgress, lead_id=lead_id)
    
    # 2. El Resolver analiza el historial y decide qué Matrix mostrar
    resolver = MatrixResolver(progress)
    current_scenario = resolver.get_scenario()
    
    # 3. Pasamos el escenario al HTML
    context = {
        'lead': progress.lead,
        'progress': progress,
        'scenario': current_scenario, # ESTO ES LO QUE TE FALTA
    }
    return render(request, 'sales/lead_detail.html', context)



@staff_member_required
@csrf_exempt
def save_matrix_config(request):
    """
    Recibe el estado completo de un 3x3 para un Stage e Iteración específicos.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        stage = data.get('stage')
        iteration = data.get('iteration', 0)
        grid_data = data.get('grid') # Un dict con { 'slot_adv_1': id_del_boton, ... }

        # 1. Buscamos o creamos el escenario (El Tablero)
        scenario, _ = MatrixScenario.objects.get_or_create(
            stage=stage, 
            iteration=iteration
        )

        # 2. Mapeamos los botones a los slots
        for slot_name, button_id in grid_data.items():
            if hasattr(scenario, slot_name):
                # Si el ID es null o 0, vaciamos el slot
                button = MatrixButtonConfig.objects.filter(id=button_id).first() if button_id else None
                setattr(scenario, slot_name, button)
        
        scenario.save()
        return JsonResponse({"status": "success", "message": f"Tablero {stage} v{iteration} actualizado."})



@staff_member_required
def manage_matrix_buttons(request):
    """
    GET: Lista botones para el 'Mazo' del configurador.
    POST: Crea un nuevo botón (una nueva carta para el mazo).
    """
    if request.method == "POST":
        data = json.loads(request.body)
        # Buscamos el EventType (ADN)
        event_type = get_object_or_404(EventTypeConfig, slug=data['event_slug'])
        
        btn = MatrixButtonConfig.objects.create(
            label=data['label'],
            event_type=event_type,
            flavor=data['flavor'],
            icon=data.get('icon', 'command'),
            next_stage=data['next_stage']
        )
        return JsonResponse({"status": "created", "id": btn.id})

    # GET: Devolvemos todos los botones activos para la biblioteca
    buttons = MatrixButtonConfig.objects.filter(active=True).values(
        'id', 'label', 'event_type__slug', 'flavor', 'next_stage', 'icon'
    )
    return JsonResponse(list(buttons), safe=False)

# --- AUXILIARES ---
def serialize_button(btn):
    if not btn: return None
    return {
        "id": btn.id,
        "label": btn.label,
        "icon": btn.icon,
        "slug": btn.resolve_slug(),
        "next_stage": btn.next_stage
    }

# --- VISTAS DE NAVEGACIÓN PRINCIPAL ---




# ICON_MAP debe ser algo como {'status': 'list-checks', 'intent': 'target', ...}
ICON_MAP = {
    'status': 'list-checks',
    'intent': 'target',
    'reply': 'message-circle',
    'communication': 'radio',
    'lifecycle': 'refresh-cw',
    'context': 'eye',
    'strategy': 'trending-up',
    'time': 'clock',
    'misc': 'box'
}

@staff_member_required
def event_dna_configurator(request):
    if request.method == "POST":
        # procesar payload y guardar todo
        data = json.loads(request.body)
        for item in data:
            try:
                event = EventTypeConfig.objects.get(slug=item["slug"])
                event.should_alert = item["should_alert"]
                event.alert_priority = item["alert_priority"]
                event.allowed_auto = item["allowed_auto"]
                event.max_consumes = item["max_consumes"]
                event.active = item["active"]
                event.save()
            except EventTypeConfig.DoesNotExist:
                continue
        return JsonResponse({"ok": True})

    # GET original
    configs = EventTypeConfig.objects.all()
    categories = list(configs.values_list('category', flat=True).distinct())
    categories = [c if c else 'other' for c in categories]

    matrix_data = {}
    for cat in categories:
        events_in_cat = configs.filter(category=cat)
        cat_key = cat.lower()
        matrix_data[cat_key] = {
            e.slug: {
                'slug': e.slug,
                'name': e.name,
                'alert': e.should_alert,
                'priority': e.alert_priority,
                'auto': e.allowed_auto,
                'consumes': e.max_consumes,
                'active': e.active,
                'icon': getattr(e, 'icon', ICON_MAP.get(cat_key, 'list-checks'))
            } for e in events_in_cat
        }

    tabs = []
    for cat in categories:
        cat_key = (cat or 'other').lower()
        tabs.append({
            'key': cat_key,
            'name': cat.capitalize(),
            'icon': ICON_MAP.get(cat_key, 'list-checks')
        })

    return render(request, 'console/partials/config.html', {
        'matrix_data_json': json.dumps(matrix_data),
        'tabs': tabs,
    })
# --- ESTRATEGIA Y MATRIX (LO NUEVO) ---

@staff_member_required
def matrix_strategy_configurator(request):
    """
    Pestaña 'STRATEGY': Configura los 9 slots por escenario.
    """
    scenarios = MatrixScenario.objects.all().order_by('stage', 'iteration')
    data = []
    for sc in scenarios:
        grid = sc.get_grid()
        data.append({
            "id": sc.id, "stage": sc.stage, "iteration": sc.iteration,
            "grid": {row: [serialize_button(b) for b in btns] for row, btns in grid.items()}
        })
    
    all_buttons = MatrixButtonConfig.objects.filter(active=True).values('id', 'label', 'flavor')
    return render(request, 'console/strategy.html', {
        'matrix_data_json': json.dumps(data, cls=DjangoJSONEncoder),
        'available_buttons': json.dumps(list(all_buttons))
    })

# --- TRIGGER BUILDER (DSL) ---

def trigger_new(request):
    variables = list(CONTEXT_MAP.keys())
    # Inferencia de tipos para el constructor visual
    lead_dummy = LeadFull.objects.first() or LeadFull.objects.create(name="Dummy")
    dummy_ctx = ContextResolver(lead=lead_dummy)
    
    variable_types = {}
    for v in variables:
        try: variable_types[v] = infer_type(dummy_ctx.resolve(v))
        except: variable_types[v] = "text"

    context = {
        "variables": json.dumps(variables),
        "variable_types": json.dumps(variable_types),
        "operator_categories": json.dumps(TYPE_OPERATORS),
        "actions": ActionTypeConfig.objects.filter(active=True),
        "templates": MsgTemplate.objects.filter(active=True),
        "event_types": EventTypeConfig.objects.filter(active=True),
        "variable_schema": json.dumps(build_variable_schema()),
    }
    return render(request, "console/main/trigger_detail.html", context)

def trigger_detail(request, trigger_id=None):
    trigger = get_object_or_404(TriggerRule, pk=trigger_id) if trigger_id else None
    return render(request, "console/main/trigger_detail.html", {"trigger": trigger})

class LogicBuilderView(TemplateView):
    template_name = "console/partials/triggers.html"
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        rule = get_object_or_404(TriggerRule, id=data.get('rule_id'))
        rule.conditions = data.get('logic')
        rule.save()
        return JsonResponse({"status": "success"})

# --- ENDPOINTS API (PARA EL FRONTEND DEL LEAD) ---

def get_lead_panel(request, lead_id):
    """API que consume el front para dibujar los botones del lead"""
    lead = get_object_or_404(LeadFull, id=lead_id)
    progress = lead.progress
    iteration = lead.events.filter(event_type__slug__icontains=f"reply_{progress.current_stage.lower()}").count()
    
    scenario = MatrixScenario.objects.filter(stage=progress.current_stage, iteration=iteration).first() or \
               MatrixScenario.objects.filter(stage=progress.current_stage, iteration=0).first()
    
    if not scenario: return JsonResponse({"error": "No config"}, status=404)
    
    grid = scenario.get_grid()
    return JsonResponse({
        "current_stage": progress.current_stage,
        "matrix": {row: [serialize_button(b) for b in btns if b] for row, btns in grid.items()}
    })