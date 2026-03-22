# engine/views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .matrix import MatrixResolver
from sales.models import LeadProgress # O donde tengas el progreso

def matrix_click_view(request, lead_id, button_id):
    if request.method == "POST":
        # 1. Buscamos el progreso del lead
        progress = get_object_or_404(LeadProgress, lead_id=lead_id)
        
        # 2. Instanciamos el Resolver
        resolver = MatrixResolver(progress)
        
        # 3. Ejecutamos el clic (Esto crea el evento y cambia el stage si hace falta)
        result = resolver.execute_click(button_id, technician=request.user)
        
        # 4. Respondemos con éxito
        return JsonResponse({
            "status": "success",
            "next_stage": result['next_stage'],
            "event": str(result['event'])
        })
    
    return JsonResponse({"status": "error"}, status=400)