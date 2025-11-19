from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

def user_directory_path(instance, filename):
    # Este archivo se guardará en MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    apellido = models.CharField(max_length=50,verbose_name='Apellido')
    identificacion = models.CharField(max_length=50, unique= True,verbose_name='Identificación')
    edad = models.IntegerField( default = 0,verbose_name='Edad')
    email = models.EmailField(max_length=50)
    telefono = models.CharField(max_length=10)
    direccion = models.CharField(max_length=50)
    foto = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    def _str_(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        db_table = 'empleado'
        ordering = ['id']

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    email = models.EmailField(max_length=100)
    comentario = models.TextField(verbose_name='Comentario')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')

    def __str__(self):
        return f"Comentario de {self.user.username} el {self.fecha_creacion}"

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        db_table = 'comentario'
        ordering = ['-fecha_creacion']

class ImageAnalysis(models.Model):
    image = models.ImageField(upload_to='image', null=False, blank=False)
