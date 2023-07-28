from django import template

register = template.Library()

@register.filter()
def slicer(value, arg):
    return value[arg]

@register.filter()
def titLe(value):
    return value.title()