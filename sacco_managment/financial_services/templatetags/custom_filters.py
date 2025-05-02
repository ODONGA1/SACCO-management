from django import template

register = template.Library()

@register.filter
def length_is(value, arg):
    """Custom filter to check if length equals a given value"""
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return False