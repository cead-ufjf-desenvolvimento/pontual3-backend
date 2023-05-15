import json
from pontualApp.models import Sugestao, Usuario

def create_default_suggestions():
    suggestions = [
        'Atraso na entrada (1º turno)',
        'Atraso na entrada (2º turno)',
        'Atraso na saída (1° turno)',
        'Atraso na saída (2° turno)',
        'Ausência de registro de entrada (1° turno)',
        'Ausência de registro de entrada (2° turno)',
        'Ausência de registro de saída (1° turno)',
        'Ausência de registro de saída (2° turno)',
        'Ausência de registro no intrajornada',
        'Autorização de <N> horas de crédito',
        'Autorização para compensação de <N> horas do banco de horas',
        'Saída antecipada (1° turno)',
        'Saída antecipada (2° turno)',
    ]

    for s in suggestions:
        new_s = Sugestao(descricao=s, criado_por=Usuario.objects.get(username="000000000000"))
        new_s.save()

def create_superuser(superuser_password):
    user = Usuario.objects.create_superuser(username="000000000000", nome="admin")
    user.set_password(superuser_password)
    user.save()


with open('scripts/config.json', 'r') as f:
    CONFIG = json.load(f)

create_superuser(CONFIG['SUPERUSER_PASSWORD'])
create_default_suggestions()