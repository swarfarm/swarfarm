from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models

from archive.models.log_models import CraftRuneLogArchive, MagicBoxCraftArchive
from archive.models.abstracts import ArchiveAbs
from bestiary.models import Level, GameItem


class ReportArchive(ArchiveAbs):
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The logging model used to generate this report"
    )
    generated_on = models.DateTimeField()
    start_timestamp = models.DateTimeField(db_index=True)
    end_timestamp = models.DateTimeField(db_index=True)
    log_count = models.IntegerField()
    unique_contributors = models.IntegerField()
    report = JSONField()
    generated_by_user = models.BooleanField(default=False, db_index=True)

    class Meta:
        get_latest_by = 'generated_on'
        abstract = True

    def __str__(self):
        return f"{self.end_timestamp} - {self.content_type}"


class LevelReportArchive(ReportArchive):
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='archived_logs')

    def __str__(self):
        return f"{self.level} {self.generated_on}"


class SummonReportArchive(ReportArchive):
    item = models.ForeignKey(GameItem, on_delete=models.PROTECT)


class MagicShopRefreshReportArchive(ReportArchive):
    pass


class MagicBoxCraftingReportArchive(ReportArchive):
    box_type = models.IntegerField(db_index=True, choices=MagicBoxCraftArchive.BOX_CHOICES)


class WishReportArchive(ReportArchive):
    pass


class RuneCraftingReportArchive(ReportArchive):
    craft_level = models.IntegerField(db_index=True, choices=CraftRuneLogArchive.CRAFT_CHOICES)
