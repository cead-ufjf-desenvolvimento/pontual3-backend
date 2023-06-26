from django.db import models
from django.contrib.auth.models import AbstractUser

from pontualApp.utils.validators import is_only_digit, validate_pis

# Create your models here.
class Usuario(AbstractUser):
    nome = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    setor = models.CharField(max_length=127)
    pis = models.CharField(max_length=12, verbose_name='PIS', validators=[is_only_digit, validate_pis], unique=True)

    def __str__(self):
        return self.nome
    
class Justificativa(models.Model):
    data = models.DateField()
    justificativa = models.TextField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuário')

    def __str__(self):
        return "Justificativa: " + self.data.strftime("%d/%m/%Y")
    
class JustificativaAdicional(models.Model):
    justificativa = models.OneToOneField(Justificativa, on_delete=models.CASCADE)
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "Justificativa Adicional: " + self.justificativa.data.strftime("%d/%m/%Y")
    
class Ponto(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    dados = models.FileField(upload_to="media/")

class Sugestao(models.Model):
    descricao = models.CharField(max_length=127)
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return "Sugestão: " + self.descricao