from django.db import models
from django.db import models

class NotaMedica(models.Model):
    id_paciente = models.IntegerField()   # simplificado: solo guardamos el ID
    id_doctor = models.IntegerField()
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    fecha_consulta = models.DateTimeField(auto_now_add=True)

    def __str__(self):  
        return f"Nota {self.id} - Paciente {self.id_paciente}"

