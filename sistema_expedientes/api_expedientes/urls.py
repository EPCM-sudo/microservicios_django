from django.urls import path
from . import views

urlpatterns = [
    # Web UI
    path('', views.index, name='expedientes_index'),
    path('crear/', views.crear_nota_page, name='crear_nota_page'),
    path('buscar/', views.buscar_notas_page, name='buscar_notas_page'),

    # API endpoints
    path('inseguro/buscar/', views.buscar_inseguro),
    path('seguro/buscar/', views.buscar_seguro),
    path('seguro/crear/', views.crear_nota),
]
