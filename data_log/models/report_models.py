from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models

from bestiary.models import Level, GameItem
from data_log.models.log_models import CraftRuneLog, MagicBoxCraft


class Report(models.Model):
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The logging model used to generate this report"
    )
    generated_on = models.DateTimeField(auto_now_add=True)
    start_timestamp = models.DateTimeField(db_index=True)
    end_timestamp = models.DateTimeField(db_index=True)
    log_count = models.IntegerField()
    unique_contributors = models.IntegerField()
    report = JSONField()
    generated_by_user = models.BooleanField(default=False, db_index=True)

    class Meta:
        get_latest_by = 'generated_on'

    def __str__(self):
        return f"{self.end_timestamp} - {self.content_type}"


class LevelReport(Report):
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='logs')

    def __str__(self):
        return f"{self.level} {self.generated_on}"


class SummonReport(Report):
    item = models.ForeignKey(GameItem, on_delete=models.PROTECT)


class MagicShopRefreshReport(Report):
    pass


class MagicBoxCraftingReport(Report):
    box_type = models.IntegerField(db_index=True, choices=MagicBoxCraft.BOX_CHOICES)


class WishReport(Report):
    pass


class RuneCraftingReport(Report):
    craft_level = models.IntegerField(db_index=True, choices=CraftRuneLog.CRAFT_CHOICES)
