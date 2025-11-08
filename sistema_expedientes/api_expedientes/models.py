from django.db import models
from django.db import models

class NotaMedica(models.Model):
    nss_paciente = models.IntegerField()  
    id_doctor = models.IntegerField()
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    fecha_consulta = models.DateTimeField(auto_now_add=True)

    def __str__(self):  
        return f"Nota {self.nss} - Paciente {self.nss_paciente}"

