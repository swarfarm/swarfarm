from django import template

register = template.Library()


@register.filter
def get_range(value):
    return range(value)

@register.filter
def absolute(value):
    return abs(value)