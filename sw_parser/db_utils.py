from django.db.models import Aggregate


class Percentile(Aggregate):
    # Implements the built in postgresql percentile_cont and percentile_disc functions
    function = None
    name = "percentile"
    template = "%(function)s(%(percentiles)s) WITHIN GROUP (ORDER BY %(" \
               "expressions)s)"

    def __init__(self, expression, percentiles, continuous=True, **extra):
        if isinstance(percentiles, (list, tuple)):
            percentiles = "array%(percentiles)s" % {'percentiles': percentiles}

        if continuous:
            extra['function'] = 'PERCENTILE_CONT'
        else:
            extra['function'] = 'PERCENTILE_DISC'

        super(Percentile, self).__init__(expression, percentiles=percentiles, **extra)



class Width_Bucket(Aggregate):
    # Implements the built in postgresql width_bucket function
    # https://www.postgresql.org/docs/9.3/static/functions-math.html

    function = 'width_bucket'
    template = '%(function)s( %(expressions)s, %(min)s, %(max)s, %(num_buckets)s )'

    def __init__(self, expression, min, max, num_buckets, **extra):
        super(Width_Bucket, self).__init__(expression, min=min, max=max, num_buckets=num_buckets, **extra)