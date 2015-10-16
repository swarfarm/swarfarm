from django import template

register = template.Library()


@register.filter
def get_range(value):
    return range(value)


@register.filter
def absolute(value):
    return abs(value)


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def remove_extension(string):
    return string.replace('.png', '').replace("'", "")
