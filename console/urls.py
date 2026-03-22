from django.urls import path
from .views import (
    console_view,
    event_dna_configurator,
    LogicBuilderView,
    trigger_detail,
    trigger_new,
    matrix_action,
    matrix_filter
    
    )

app_name = "console"

urlpatterns = [
    
    #matrix
    path("matrix/action/", matrix_action, name="matrix_action"),
    path("matrix/filter/<str:filter_key>/", matrix_filter, name="matrix_filter"),
    
    #console
    path("console/", console_view, name="console"),
    path('console/<int:lead_id>/', console_view, name='console_detail'),
    
    
    path("config/", event_dna_configurator, name="event_dna_configurator"),
    path("engine/configurator/", event_dna_configurator, name="event_dna_configurator"),
    path("builder/", LogicBuilderView.as_view(), name="save_logic_dna"),
    

    # Trigger detalle
    path("trigger/new/", trigger_new, name="trigger_detail_new"),
    path("trigger/<int:trigger_id>/", trigger_detail, name="trigger_detail"),
]