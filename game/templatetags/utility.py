from django import template

register = template.Library()

@register.filter()
def slicer(value, arg):
    return value[arg]