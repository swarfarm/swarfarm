from django.db import models


class ArchiveAbs(models.Model):
    archived_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True
