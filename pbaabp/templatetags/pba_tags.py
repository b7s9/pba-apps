from django import template

register = template.Library()


@register.filter(name="splitlines")
def splitlines_filter(value):
    return value.splitlines()
