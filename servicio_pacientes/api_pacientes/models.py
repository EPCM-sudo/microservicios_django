from django.db import models
from django.contrib.auth.hashers import make_password

class Paciente(models.Model):
    nombre = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    nss = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    es_doctor = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Si la contraseña no está hasheada, la hashamos (simple ejemplo)
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.nss})"
