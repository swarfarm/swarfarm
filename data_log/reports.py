from .models import Report, LevelReport, SummonLog
from datetime import timedelta
from django.utils import timezone


def _records_to_report(log_model, report_timespan=timedelta(weeks=2), minimum_count=2500):
    qs = log_model.objects.filter(
        timestamp__gte=timezone.now() - report_timespan
    )

    if qs.count() < minimum_count:
        # Return last minimum_count logs, ignoring report timespan
        return log_model.objects.all()[:minimum_count]
    else:
        return qs
