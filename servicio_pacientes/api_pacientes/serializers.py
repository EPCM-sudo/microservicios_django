from rest_framework import serializers
from .models import Paciente
import re

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['id', 'nombre', 'fecha_nacimiento', 'nss', 'email', 'password', 'es_doctor']
        extra_kwargs = {
            'password': {'write_only': True},
            'es_doctor':{'read_only':True}
        }

        def validate_nss(self, value):
            # regla: 4-30 characters, solo dígitos, letras y guion
            if not re.fullmatch(r'^[0-9]{4,30}$', value):
                raise serializers.ValidationError(
                    'NSS inválido: use sólo letras, números y guiones (4-30 caracteres).'
                )

            # Rechazar caracteres típicos de inyección
            forbidden = ["'", "\"", ";", "--", "/*", "*/"]
            for token in forbidden:
                if token in value:
                    raise serializers.ValidationError('NSS contiene caracteres inválidos.')

            return value
