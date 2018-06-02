from django import template

register = template.Library()


@register.filter
def timedelta(delta):
    total_seconds = delta.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds - minutes * 60
    return f'{minutes:02d}:{seconds:2.3f}'
