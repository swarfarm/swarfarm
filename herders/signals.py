from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Monster


@receiver(m2m_changed, sender=Monster.source.through)
def monster_source_changed(sender, **kwargs):

    pass

