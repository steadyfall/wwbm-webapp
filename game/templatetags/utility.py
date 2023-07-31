from django import template

register = template.Library()

@register.filter()
def slicer(value, arg):
    return value[arg]

@register.filter()
def titLe(value):
    return value.title()

@register.filter()
def getListFromQueryDict(querydict, itemToGet):
    return querydict.getlist(itemToGet)

@register.filter()
def querysetToPrimaryKey(queryset):
    return list(map(lambda x: x.pk, queryset))