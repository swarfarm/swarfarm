from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .log_exporter import export_all


@shared_task
def export_log_data():
    export_all()
