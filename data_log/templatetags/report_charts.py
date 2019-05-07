from django import template
from copy import deepcopy
import json

from data_log.reports import chart_templates

register = template.Library()


@register.filter
def drop_summary(summary_data):
    # Transform level drop summary to highcharts expected format
    chart = deepcopy(chart_templates.pie)
    chart['title'] = 'Overall drop distribution'
    chart['series'].append({
        'name': 'Drop Types',
        'colorByPoint': True,
        'data': [
            {
                'name': drop['name'],
                'y': drop['count']
            } for drop in summary_data
        ],
    })

    return json.dumps(chart)
