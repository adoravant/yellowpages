# engine/urls.py

from django.urls import path
from .views import matrix_click_view

    
    



urlpatterns = [

    path('matrix-click/<int:lead_id>/<int:button_id>/', matrix_click_view, name='matrix_click'),
]