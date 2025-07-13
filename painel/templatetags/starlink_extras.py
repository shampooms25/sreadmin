from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Custom template filter to get dictionary item by key
    Usage: {{ dictionary|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def dict_get(dictionary, key):
    """
    Alternative template filter to get dictionary item by key
    Usage: {{ dictionary|dict_get:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
