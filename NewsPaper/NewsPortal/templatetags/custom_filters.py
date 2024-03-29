from django import template
import re

register = template.Library()

# Регистрируем наш фильтр под именем currency, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.

CURRENCIES_SYMBOLS = {
    'rub': 'Р',
    'usd': '$',
}

STOP_WORDS = [
    'Редиска',
    'редиска',
    'лопух',
    'Лопух'
]

@register.filter()
def currency(value, code='rub'):
    """
   value: значение, к которому нужно применить фильтр
   code: код валюты
   """
    postfix = CURRENCIES_SYMBOLS[code]

    return f'{value} {postfix}'

@register.filter()
def censor(data):
    for pattern in STOP_WORDS:
        try:
            data = re.sub(pattern, pattern[0] + '*'*(len(pattern)-1),  data)
        except TypeError:
            print("Фильтр применяется не к строке! Должна быть строка!")
    return f'{data}'