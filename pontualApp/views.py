from django.contrib.auth import authenticate
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from pontualApp.models import Justificativa, JustificativaAdicional, Ponto, Sugestao, Usuario
from pontualApp.serializers import JustificativaAdicionalSerializer, JustificativaSerializer, LoginSerializer, PontoSerializer, SugestaoSerializer, UsuarioSerializer

# Create your views here.
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class JustificativaViewSet(viewsets.ModelViewSet):
    queryset = Justificativa.objects.all()
    serializer_class = JustificativaSerializer
    permission_classes = [permissions.IsAuthenticated]

    # vincula o usuário atual à criação da justificativa
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
        return super().perform_create(serializer)
    
    # Garante que apenas justificativas do usuário em questão sejam retornadas
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(usuario=self.request.user)
        return queryset
    
class PontoViewSet(viewsets.ModelViewSet):
    queryset = Ponto.objects.all()
    serializer_class = PontoSerializer
    permission_classes = [permissions.IsAdminUser]
    
class LoginViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class SugestaoViewSet(viewsets.ModelViewSet):
    queryset = Sugestao.objects.all()
    serializer_class = SugestaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (queryset.filter(criado_por=self.request.user) | queryset.filter(criado_por__username='admin')).order_by('descricao')
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user)
        return super().perform_create(serializer)
    
class JustificativaAdicionalViewSet(viewsets.ModelViewSet):
    queryset = JustificativaAdicional.objects.all()
    serializer_class = JustificativaAdicionalSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(criado_por=self.request.user)
        return queryset
    
    def post(self, request):
        serializer = JustificativaAdicionalSerializer(data=request.data, context={'request': request})