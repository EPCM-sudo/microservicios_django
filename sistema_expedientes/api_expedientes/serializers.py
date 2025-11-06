from rest_framework import serializers
from .models import NotaMedica

class NotaMedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaMedica
        fields = '__all__'
