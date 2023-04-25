import os
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.utils import timezone

from pontualApp.models import Justificativa, JustificativaAdicional, Ponto, Sugestao, Usuario

class UsuarioSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ['url', 'nome', 'email', 'cargo', 'setor', 'pis', 'password']

    def create(self, validated_data):
        user = Usuario.objects.create(
            nome=validated_data['nome'],
            email=validated_data['email'],
            cargo=validated_data['cargo'],
            setor=validated_data['setor'],
            pis=validated_data['pis'],
        )
        user.username = validated_data['pis']
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def get_url(self, obj):
        request = self.context['request']
        url_kwargs = {'pk': obj.pk}
        return reverse('user-detail', kwargs=url_kwargs, request=request)
    
class JustificativaSerializer(serializers.HyperlinkedModelSerializer):
    usuario = serializers.HyperlinkedRelatedField(view_name='usuario-detail', read_only=True)
    
    class Meta:
        model = Justificativa
        fields = ['url', 'data', 'justificativa', 'usuario']

class JustificativaAdicionalSerializer(serializers.HyperlinkedModelSerializer):
    criado_por = serializers.HyperlinkedRelatedField(view_name='usuario-detail', read_only=True)
    justificativa = serializers.HyperlinkedRelatedField(view_name='justificativa-detail', read_only=True)
    descricao = serializers.CharField(write_only=True)
    data = serializers.DateField(write_only=True)

    class Meta:
        model = JustificativaAdicional
        fields = ['url', 'justificativa', 'criado_por', 'descricao', 'data']

    def create(self, validated_data):
        request = self.context.get('request')
        justificativa = Justificativa(
            justificativa=validated_data['descricao'],
            data=validated_data['data'],
            usuario=request.user
        )
        justificativa.save()
        justificativa_adicional = JustificativaAdicional(
            justificativa=justificativa,
            criado_por=request.user
        )
        justificativa_adicional.save()
        return justificativa_adicional

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class PontoSerializer(serializers.HyperlinkedModelSerializer):
    dados = serializers.FileField(write_only=True)
    
    class Meta:
        model = Ponto
        fields = ['url', 'dados', 'data']

    def create(self, validated_data):
        # substitui sempre o último arquivo de ponto pelo atual
        os.system('rm -rf ./media')
        if Ponto.objects.all():
            Ponto.objects.last().delete()
        ponto = Ponto(
            dados = validated_data['dados']
        )
        ponto.save()
        return ponto


class SugestaoSerializer(serializers.HyperlinkedModelSerializer):
    criado_por = serializers.ReadOnlyField(source='criado_por.username')
    
    class Meta:
        model = Sugestao
        fields = ['url', 'descricao', 'criado_por']