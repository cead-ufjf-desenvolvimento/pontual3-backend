from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from validate_docbr import PIS

def is_only_digit(value: str) -> bool:
    value = ''.join(val for val in value if val.isdigit())
    if len(value) != 12:
        raise ValidationError(_('Esse campo é composto por 12 dígitos e aceita somente números'), code=status.HTTP_400_BAD_REQUEST)


def validate_pis(value):
    doc_pis = PIS()
    pis = value[1:]
    
    if not doc_pis.validate(pis):
        raise ValidationError(_('PIS inválido'), code=status.HTTP_400_BAD_REQUEST)