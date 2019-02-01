from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .log_exporter import export_all
from .models import SummonLog, RunLog, RiftDungeonLog, RuneCraftLog, ShopRefreshLog, WorldBossLog, RiftRaidLog, WishLog


@shared_task
def export_log_data():
    export_all()


@shared_task
def prune_old_data():
    six_months_ago = timezone.now() - timedelta(weeks=4 * 6)

    log_models = [
        SummonLog, RunLog, RiftDungeonLog, RuneCraftLog, ShopRefreshLog, WorldBossLog, RiftRaidLog, WishLog
    ]

    num_deleted = 0
    for log in log_models:
        count, _ = log.objects.filter(timestamp__lte=six_months_ago).delete()
        print('Deleted {} entries from {}'.format(count, log.__name__))
        num_deleted += count

    print('Deleted {} objects total'.format(num_deleted))

