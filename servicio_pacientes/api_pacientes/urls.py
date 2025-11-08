from django.urls import path
from . import views


urlpatterns = [
    # API endpoints ya definidos...
    path('', views.index, name='index'),
    path('registro/', views.registro_page, name='registro_page'),
    path('perfil/<int:pk>/', views.perfil_page, name='perfil_page'),
    
    path('inseguro/registro/', views.registro_inseguro, name='registro_inseguro'),
    path('seguro/registro/', views.registro_seguro, name='registro_seguro'),
    path('seguro/perfil/<int:pk>/', views.perfil, name='perfil'),
    path('inseguro/perfil/', views.perfil_inseguro, name='perfil_inseguro'),
    path('inseguro/perfil/actualizar/<int:id>/', views.actualizar_perfil_inseguro, name='actualizar_perfil_inseguro'),
    path('seguro/perfil/actualizar/<int:id>/', views.actualizar_perfil_seguro, name='actualizar_perfil_seguro')
]
