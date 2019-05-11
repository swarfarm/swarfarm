from django import template
from copy import deepcopy
import json

from data_log.reports import chart_templates

register = template.Library()


@register.filter
def drop_summary(summary_data):
    # Transform level drop summary to highcharts expected format
    chart_data = deepcopy(chart_templates.pie)
    chart_data['title']['text'] = 'Overall drop distribution'
    chart_data['series'].append({
        'name': 'Drop Types',
        'colorByPoint': True,
        'data': [
            {
                'name': drop['name'],
                'y': drop['count']
            } for drop in summary_data
        ],
    })

    return json.dumps(chart_data)


def pie(data, *args, **kwargs):
    chart_data = deepcopy(chart_templates.pie)
    chart_data['title']['text'] = kwargs.get('title')
    chart_data['series'].append({
        'name': '',
        'colorByPoint': True,
        'data': [
            {
                'name': k,
                'y': v,
            } for k, v in data.items()
        ],
    })
    return chart_data


def bar(data, *args, **kwargs):
    # Construct series
    series = {

    }

    chart_data = deepcopy(chart_templates.column)
    chart_data['title']['text'] = kwargs.get('title')
    # chart_data['plotOptions']['column']['stacking'] = 'normal'
    chart_data['plotOptions']['column']['groupPadding'] = 0
    chart_data['plotOptions']['column']['pointPadding'] = 0.05
    chart_data['xAxis']['categories'] = kwargs.get('categories')
    chart_data['series'] = [{
        'name': k,
        'data': v,
    } for k, v in series.items()]
    chart_data['legend'] = {
        'useHTML': True,
        'align': 'right',
        'x': 0,
        'verticalAlign': 'top',
        'y': 25,
        'floating': True,
        'backgroundColor': 'white',
        'borderColor': '#CCC',
        'borderWidth': 1,
        'shadow': False,
    }

    return chart_data


def histogram(data, *args, **kwargs):
    categories = [
        i['bin'] for i in data
    ]

    # Construct series
    series = {}
    for hist_bin in data:
        for k, v in hist_bin.items():
            if k == 'bin':
                continue

            if k not in series:
                series[k] = []

            series[k] += [v]

    chart_data = deepcopy(chart_templates.column)
    chart_data['title']['text'] = kwargs.get('title')
    chart_data['plotOptions']['column']['stacking'] = 'normal'
    chart_data['plotOptions']['column']['groupPadding'] = 0
    chart_data['plotOptions']['column']['pointPadding'] = 0.05
    chart_data['xAxis']['categories'] = categories
    chart_data['series'] = [{
        'name': k,
        'data': v,
    } for k, v in series.items()]
    chart_data['legend'] = {
        'useHTML': True,
        'align': 'right',
        'x': 0,
        'verticalAlign': 'top',
        'y': 25,
        'floating': True,
        'backgroundColor': 'white',
        'borderColor': '#CCC',
        'borderWidth': 1,
        'shadow': False,
    }

    return chart_data


chart_types = {
    'histogram': histogram,
    'occurrences': bar,
    'pie': pie,
}


@register.simple_tag
def chart(data, *args, **kwargs):
    chart_type = kwargs.get('type', data['type'])
    chart_data = chart_types[chart_type](data['data'], *args, **kwargs)
    return json.dumps(chart_data)