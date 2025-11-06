from django.contrib import admin
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'nss', 'email', 'es_doctor')
    readonly_fields = ('id',)
