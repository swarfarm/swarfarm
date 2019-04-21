from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models

from bestiary.models import Level, GameItem


class Report(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The logging model used to generate this report"
    )
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    log_count = models.IntegerField()
    unique_contributors = models.IntegerField()
    report = JSONField()

    class Meta:
        get_latest_by = 'end_timestamp'


class LevelReport(Report):
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='logs')


class SummonReport(Report):
    item = models.ForeignKey(GameItem, on_delete=models.PROTECT)
