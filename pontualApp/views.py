import math
from django.contrib.auth import authenticate
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils import timezone

from pontualApp.models import Justificativa, JustificativaAdicional, Ponto, Sugestao, Usuario
from pontualApp.serializers import JustificativaAdicionalSerializer, JustificativaSerializer, LoginSerializer, PontoSerializer, SugestaoSerializer, UsuarioSerializer


def checkTotal(item):
    if timezone.datetime(int(item['data'][6:]), int(item['data'][3:5]), int(item['data'][:2])).weekday() == 4:
        hours_of_the_day = 8
    else:
        hours_of_the_day = 9
    
    min_minutes = hours_of_the_day*60 - 10
    max_minutes = hours_of_the_day*60 + 10
    
    try:
        minutes1 = int(item['entrada'][3:]) + int(item['entrada'][:2])*60
        minutes2 = int(item['almoco1'][3:]) + int(item['almoco1'][:2])*60
        minutes3 = int(item['almoco2'][3:]) + int(item['almoco2'][:2])*60
        minutes4 = int(item['saida'][3:]) + int(item['saida'][:2])*60

        total = (minutes2 - minutes1) + (minutes4 - minutes3)
        
        difference = math.fabs(total - hours_of_the_day*60)

        sign = '+' if total - hours_of_the_day*60 >= 0 else '-'

        hour = str(int(difference/60))
        minute = str(int(difference%60)) if difference%60 >= 10 else '0' + str(int(difference%60))

        output = [hour + ':' + str(minute), sign, total >= min_minutes and total <= max_minutes]

    except:
        output = ['--:--', '', False]

    return output

# Create your views here.
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Permite que apenas administradores vejam a lista de usuários
    def list(self, request, *args, **kwargs):
        if(request.user.is_staff):
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.filter_queryset(self.get_queryset()).filter(pis=request.user.username)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # Permite que apenas proprietários e administradores vejam detalhes de usuários
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user == instance or request.user.is_staff):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
    
    # Permite que apenas proprietários e administradores vejam justificativas
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user == instance.usuario or request.user.is_staff):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
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

    # Retorna apenas as sugestões criadas pelo usuário e pelo administrador
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (queryset.filter(criado_por=self.request.user) | queryset.filter(criado_por__username='admin')).order_by('descricao')
        return queryset
    
    # vincula o usuário atual à sugestão criada
    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user)
        return super().perform_create(serializer)
    
    # Permite que apenas proprietários e administradores vejam sugestões
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user == instance.criado_por or request.user.is_staff):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
class JustificativaAdicionalViewSet(viewsets.ModelViewSet):
    queryset = JustificativaAdicional.objects.all()
    serializer_class = JustificativaAdicionalSerializer

    # retorna apenas as justificativas adicionais do usuário em questão
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(criado_por=self.request.user)
        return queryset
    
    # Passa o context para o serializer
    def post(self, request):
        serializer = JustificativaAdicionalSerializer(data=request.data, context={'request': request})

class AFDViewSet(viewsets.ViewSet):
    """
    GET: "/?mes=mm&?ano=yyyy" to retrieve data
    """

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        if not Usuario.objects.filter(pis=request.user.username):
            error_message = {'user_error': 'Usuário não corresponde a nenhum cadastrado no AFD'}
            return Response(error_message, status=status.HTTP_403_FORBIDDEN)
        
        current_user = Usuario.objects.get(pis=request.user.username)
        results = []
        
        if request.GET.get('ano') and request.GET.get('mes') and Ponto.objects.all():
            # armazena as variáveis de mês e ano
            year = int(request.GET.get('ano'))
            month = int(request.GET.get('mes'))

            # armazena os dados do ponto mais recente
            data = Ponto.objects.last().dados

            # lê as linhas do conjunto de dados
            lines = data.readlines()
            
            # inicialização de variáveis de controle
            previous_day = 0
            current_result = {}

            # percorre cada linha do conjunto de dados
            for line in lines:
                # decodificação dos caracteres especiais
                line = line.decode('utf-8')

                # linhas de tamanho 39 ou 40 contêm as informações de interesse
                # também verifica se a linha pertence ao mês, ano e usuário de interesse
                if (len(line) == 40 or len(line) == 39) and int(line[12:14]) == month and int(line[14:18]) == year and line[22:34] == current_user.pis:
                    current_day = int(line[10:12])

                    # verifica se houve alteração de dia
                    if(current_day != previous_day):
                        # verifica se não é o primeiro dia armazenado
                        if previous_day != 0:
                            # Verifica se há dados o suficiente para encerrar o dia
                            if(     'entrada' in current_result.keys() and
                                    'almoco1' in current_result.keys() and
                                    'almoco2' in current_result.keys() and
                                    'saida' in current_result.keys()):
                                output = checkTotal(current_result)
                                # armazena dados do banco de horas daquele dia
                                current_result['horas'] = output[0]
                                # informa se o banco é positivo ou negativo
                                current_result['sinal'] = output[1]

                            # atualiza a lista de saída
                            results.append(current_result)
                            # apaga a lista do dia
                            current_result = {}

                        # armazena a data atual
                        current_result['data'] = line[10:12] + '/' + line[12:14] + '/' + line[14:18]
                        
                        # armazena a hora atual
                        current_result['entrada'] = line[18:20] + ':' + line[20:22]
                        
                        # atualiza as variáveis de dia atual
                        current_year = int(line[14:18])
                        current_month = int(line[12:14])

                        # armazena a justificativa do dia, caso haja no banco
                        current_date = timezone.datetime(current_year, current_month, current_day)
                        current_justification_query = Justificativa.objects.filter(data=current_date).filter(usuario=current_user)
                        if current_justification_query:
                            current_result['justificativa'] = current_justification_query[0].justificativa

                        # atualiza o dia anterior
                        previous_day = current_day
                    
                    else:
                        # caso não haja alteração de dia armazena novo registro de hora
                        if 'entrada' in current_result.keys() and not 'almoco1' in current_result.keys(): current_result['almoco1'] = line[18:20] + ':' + line[20:22]
                        elif 'almoco1' in current_result.keys() and not 'almoco2' in current_result.keys(): current_result['almoco2'] = line[18:20] + ':' + line[20:22]
                        elif 'almoco2' in current_result.keys() and not 'saida' in current_result.keys(): current_result['saida'] = line[18:20] + ':' + line[20:22]

            # adiciona o último dado para fechar o vetor
            if previous_day != 0:
                # Verifica se há dados o suficiente para encerrar o dia
                if(     'entrada' in current_result.keys() and
                        'almoco1' in current_result.keys() and
                        'almoco2' in current_result.keys() and
                        'saida' in current_result.keys()):
                    output = checkTotal(current_result)
                    # armazena dados do banco de horas daquele dia
                    current_result['horas'] = output[0]
                    # informa se o banco é positivo ou negativo
                    current_result['sinal'] = output[1]
                # armazena a justificativa do dia, caso haja no banco
                current_date = timezone.datetime(current_year, current_month, current_day)
                current_justification_query = Justificativa.objects.filter(data=current_date).filter(usuario=current_user)
                if current_justification_query:
                    current_result['justificativa'] = current_justification_query[0].justificativa

                # atualiza a lista de saída
                results.append(current_result)
                # apaga a lista do dia
                current_result = {}

        # vetor de dias para justificar
        days_to_justify = []

        for item in results:
            # vetor informando os dias a serem justificados
            if not checkTotal(item)[2]:
                days_to_justify.append(item['data'])

        context = {
            'results': results,
            'days_to_justify': days_to_justify,
        }

        return Response(context)