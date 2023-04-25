from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import status

def is_only_digit(value: str) -> bool:
    value = ''.join(val for val in value if val.isdigit())
    if len(value) != 12:
        raise ValidationError(_('Esse campo aceita apenas números'), code=status.HTTP_400)
    
def validate_pis(value: str) -> bool:
    weight_array = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    acc = 0
    value = value[1:]
    for i in range(len(weight_array)):
        acc += int(value[i]) * weight_array[i]
    remainder = acc % 11
    result = 11 - remainder
    if result != int(value[-1]):
        raise ValidationError(_('PIS inválido'), code=status.HTTP_400)