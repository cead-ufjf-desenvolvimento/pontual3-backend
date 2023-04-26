from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import status

def is_only_digit(value: str) -> bool:
    value = ''.join(val for val in value if val.isdigit())
    if len(value) != 12:
        raise ValidationError(_('Esse campo aceita apenas números'), code=status.HTTP_400_BAD_REQUEST)
    
def validate_pis(value):
    pis = value[1:]
    # Remove any non-digit characters
    pis = ''.join(filter(str.isdigit, pis))
    
    # Check if the length is correct
    if len(pis) != 11:
        return False
    
    # Calculate the check digit
    total = 0
    for i in range(0, 10):
        total += int(pis[i]) * (10 - i)
    check_digit = 11 - (total % 11)
    if check_digit == 10 or check_digit == 11:
        check_digit = 0
    
    # Compare the calculated check digit with the last digit of the PIS
    if check_digit != int(pis[10]):
        raise ValidationError(_('PIS inválido'), code=status.HTTP_400_BAD_REQUEST)