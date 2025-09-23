from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtém um item de um dicionário usando uma chave"""
    return dictionary.get(key, '')
