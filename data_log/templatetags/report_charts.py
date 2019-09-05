import json
from copy import deepcopy

from django import template

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
            chart_data['tooltip']['pointFormat'] = '<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y:.1f}%</b></td></tr>'

    if kwargs.get('percentage') == False:
        if chart_data['chart']['type'] == 'pie':
            chart_data['plotOptions']['pie']['dataLabels']['format'] = '<b>{point.name}</b>: {point.y}'

    return chart_data


_quality_choices = dict(RuneObjectBase.QUALITY_CHOICES)
QUALITY_COLORS = {
    _quality_choices[RuneObjectBase.QUALITY_NORMAL]: '#eeeeee',
    _quality_choices[RuneObjectBase.QUALITY_MAGIC]: '#04d25e',
    _quality_choices[RuneObjectBase.QUALITY_RARE]: '#3bc9fe',
    _quality_choices[RuneObjectBase.QUALITY_HERO]: '#d66ef6',
    _quality_choices[RuneObjectBase.QUALITY_LEGEND]: '#ef9f24',
}

QUALITY_SORT_ORDER = {
    v: k for k, v in _quality_choices.items()
}

RUNE_SET_SORT_ORDER = {
    v: k for k, v in dict(RuneObjectBase.TYPE_CHOICES).items()
}


def _color_rune_series(series_data):
    for series in series_data:
        if series['name'] in QUALITY_COLORS:
            series['color'] = QUALITY_COLORS[series['name']]

    return series_data


def _color_pass_fail_series(series_data):
    for series in series_data:
        if series['name'] == 'True':
            series['color'] = '#1a912e'
        else:
            series['color'] = '#911a1a'

    return series_data


_series_colors = {
    'rune': _color_rune_series,
    'pass_fail': _color_pass_fail_series,
}


# All _sort_by_x functions assume the input data is a list of tuples which are key:value pairs
def _sort_by_key(data):
    return sorted(data, key=lambda x: x[0])


def _sort_by_value(data):
    return sorted(data, key=lambda x: x[1])


def _sort_by_rune_set(data):
    # Assumes keys are rune set strings
    return sorted(data, key=lambda x: RUNE_SET_SORT_ORDER[x[0]])


def _sort_by_quality(data):
    # Assumes keys are quality strings
    return sorted(data, key=lambda x: QUALITY_SORT_ORDER[x[0]])


_sort_methods = {
    'value': _sort_by_value,
    'key': _sort_by_key,
    'rune': _sort_by_rune_set,
    'quality': _sort_by_quality,
}


def _sort_data(data, by='value', reverse=False):
    sorted_data = _sort_methods[by](data)

    if reverse:
        return list(reversed(sorted_data))

    return sorted_data


def color_series(chart_data, color_type):
    if color_type in _series_colors:
        chart_data['series'] = _series_colors[color_type](chart_data['series'])

    return chart_data


def pie(**kwargs):
    data = list(kwargs.get('data').items())
    if 'sorted' in kwargs:
        data = _sort_data(data, by=kwargs.get('sorted'), reverse=kwargs.get('reverse'))

    chart_data = _common_chart_attributes(chart_templates.pie, **kwargs)
    chart_data['series'].append({
        'name': '',
        'colorByPoint': True,
        'data': [
            {
                'name': k,
                'y': v,
            } for k, v in data
        ],
    })

    return chart_data


def bar(**kwargs):
    data = list(kwargs.get('data').items())
    if 'sorted' in kwargs:
        data = _sort_data(data, by=kwargs.get('sorted'), reverse=kwargs.get('reverse'))

    chart_data = _common_chart_attributes(chart_templates.column, **kwargs)
    if kwargs.get('percentage'):
        total = float(kwargs.get('total', 1)) / 100
    else:
        total = 1

    chart_data['plotOptions']['column']['stacking'] = kwargs.get('stacking')
    chart_data['plotOptions']['column']['groupPadding'] = 0
    chart_data['plotOptions']['column']['pointPadding'] = 0.05

    chart_data['xAxis']['categories'] = kwargs.get('categories', [v[0] for v in data])
    chart_data['series'] = [{
        'name': kwargs.get('series_name'),
        'data': [float(v[1]) / total for v in data],
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
    series = series.items()

    if 'sorted' in kwargs:
        series = _sort_data(series, by=kwargs.get('sorted'), reverse=kwargs.get('reverse'))

    chart_data['plotOptions']['column']['stacking'] = 'normal'
    chart_data['plotOptions']['column']['groupPadding'] = 0
    chart_data['plotOptions']['column']['pointPadding'] = 0.05
    chart_data['xAxis']['categories'] = categories
    chart_data['series'] = [{
        'name': k,
        'data': v,
    } for k, v in series]

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
