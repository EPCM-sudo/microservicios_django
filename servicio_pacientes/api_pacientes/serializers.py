from rest_framework import serializers
from .models import Paciente

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['id', 'nombre', 'fecha_nacimiento', 'nss', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
