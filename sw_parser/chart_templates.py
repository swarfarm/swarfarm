column = {
    'chart': {'type': 'column'},
    'legend': {
        'enabled': False
    },
    'title': {
        'text': None,
        'useHTML': True,
    },
    'xAxis': {
        'categories': [],
        'crosshair': True,
        'labels': {
            'useHTML': True,
        },
    },
    'yAxis': {
        'min': 0,
        'title': {'text': ''}
    },
    'tooltip': {
        'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
        'pointFormat': '<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y}</b></td></tr>',
        'footerFormat': '</table>',
        'shared': True,
        'useHTML': True
    },
    'plotOptions': {
        'column': {
            'animation': False,
            'pointPadding': 0.2,
            'borderWidth': 0
        }
    },
    'series': [],
    'credits': False,
}

pie = {
    'chart': {
        'plotBackgroundColor': None,
        'plotBorderWidth': None,
        'plotShadow': False,
        'type': 'pie'
    },
    'title': {
        'text': None,
        'useHTML': True,
    },
    'tooltip': {
        'shared': True,
        'useHTML': True,
        'headerFormat': '',
        'pointFormat': '<b>{point.name}: {point.percentage:.1f}%</b>'
    },
    'plotOptions': {
        'pie': {
            'animation': False,
            'allowPointSelect': False,
            'cursor': 'pointer',
            'dataLabels': {
                'enabled': True,
                'useHTML': True,
                'format': '<b>{point.name}</b>: {point.percentage:.1f} %',
                'style': {
                    'color': "(Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'"
                }
            }
        }
    },
    'series': [],
    'credits': False,
}

boxplot = {
    'chart': {
        'type': 'boxplot',
    },
    'title': {
        'text': None,
        'useHTML': True,
    },
    'tooltip': {
        'headerFormat': '<span style="font-size:10px">{point.key}</span><table>',
        'pointFormat': '<tr><td style="color:{series.color};padding:0">{series.name}: </td><td style="padding:0"><b>{point.y}</b></td></tr>',
        'footerFormat': '</table>',
        'shared': True,
        'useHTML': True
    },
    'xAxis': {
        'categories': [],
        'crosshair': True
    },
    'yAxis': {
        'min': 0,
        'title': {'text': ''}
    },
    'series': [],
    'credits': False,
}

no_data = {
    'chart': {
        'plotBackgroundColor': None,
        'plotBorderWidth': None,
        'plotShadow': False,
        'type': 'pie'
    },
    'title': {
        'text': 'No Data Available',
        'useHTML': True,
    },
    'credits': False,
}
