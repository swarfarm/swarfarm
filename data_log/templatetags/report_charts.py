from django import template
from copy import deepcopy
import json
from bestiary.models import RuneObjectBase
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


def _common_chart_attributes(chart_template, **kwargs):
    chart_data = deepcopy(chart_template)
    chart_data['title']['text'] = kwargs.get('title')

    if kwargs.get('legend'):
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

    if kwargs.get('percentage'):
        # chart_data['yAxis']['max'] = 100
        chart_data['yAxis']['labels'] = {
            'format': '{value}%'
        }
        if chart_data['chart']['type'] == 'column':
            chart_data['tooltip']['pointFormat'] = '<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y}%</b></td></tr>'

    return chart_data


_quality_choices = dict(RuneObjectBase.QUALITY_CHOICES)
QUALITY_COLORS = {
    _quality_choices[RuneObjectBase.QUALITY_NORMAL]: '#eeeeee',
    _quality_choices[RuneObjectBase.QUALITY_MAGIC]: '#04d25e',
    _quality_choices[RuneObjectBase.QUALITY_RARE]: '#3bc9fe',
    _quality_choices[RuneObjectBase.QUALITY_HERO]: '#d66ef6',
    _quality_choices[RuneObjectBase.QUALITY_LEGEND]: '#ef9f24',
}


def _color_rune_series(series_data):
    for series in series_data:
        if series['name'] in QUALITY_COLORS:
            series['color'] = QUALITY_COLORS[series['name']]

    return series_data


_series_colors = {
    'rune': _color_rune_series,
}


def color_series(chart_data, color_type):
    if color_type in _series_colors:
        chart_data['series'] = _series_colors[color_type](chart_data['series'])

    return chart_data


def pie(**kwargs):
    data = kwargs.get('data')
    chart_data = _common_chart_attributes(chart_templates.pie, **kwargs)
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


def bar(**kwargs):
    data = kwargs.get('data')
    chart_data = _common_chart_attributes(chart_templates.column, **kwargs)
    if kwargs.get('percentage'):
        total = float(kwargs.get('total', 1)) / 100
    else:
        total = 1

    chart_data['plotOptions']['column']['stacking'] = kwargs.get('stacking')
    chart_data['plotOptions']['column']['groupPadding'] = 0
    chart_data['plotOptions']['column']['pointPadding'] = 0.05
    chart_data['xAxis']['categories'] = kwargs.get('categories', [k for k in data.keys()])
    chart_data['series'] = [{
        'name': 'Main Stats',
        'data': [float(v) / total for v in data.values()],
    }]

    chart_data = color_series(chart_data, kwargs.get('colors'))

    return chart_data


def histogram(**kwargs):
    data = kwargs.get('data')
    chart_data = _common_chart_attributes(chart_templates.column, **kwargs)

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

    chart_data['plotOptions']['column']['stacking'] = 'normal'
    chart_data['plotOptions']['column']['groupPadding'] = 0
    chart_data['plotOptions']['column']['pointPadding'] = 0.05
    chart_data['xAxis']['categories'] = categories
    chart_data['series'] = [{
        'name': k,
        'data': v,
    } for k, v in series.items()]

    chart_data = color_series(chart_data, kwargs.get('colors'))

    return chart_data


chart_types = {
    'histogram': histogram,
    'occurrences': bar,
    'pie': pie,
}


@register.simple_tag
def chart(data, **kwargs):
    # Merge chart data and kwargs such that kwargs overrides existing keys in data
    chart_parameters = {**data, **kwargs}
    chart_type = chart_parameters['type']
    chart_data = chart_types[chart_type](**chart_parameters)
    return json.dumps(chart_data)
