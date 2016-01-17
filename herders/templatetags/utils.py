from django import template

register = template.Library()


@register.filter
def get_range(value):
    if value:
        return range(value)
    else:
        return 0


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
    return string.replace('.png', '').replace("'", "").replace('(', '_').replace(')', '_')


@register.filter
# Get dictionary key by string
def key(d, key_name):
    return d[key_name]
key = register.filter('key', key)