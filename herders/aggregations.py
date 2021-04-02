from django.db.models import Aggregate, FloatField


class Median(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'median'
    output_field = FloatField()
    template = '%(function)s(0.5) WITHIN GROUP (ORDER BY %(expressions)s)'


class Perc25(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'perc25'
    output_field = FloatField()
    template = '%(function)s(0.25) WITHIN GROUP (ORDER BY %(expressions)s)'


class Perc75(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'perc75'
    output_field = FloatField()
    template = '%(function)s(0.75) WITHIN GROUP (ORDER BY %(expressions)s)'
