from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MonsterInstance, RuneInstance, RuneCraftInstance


@receiver(post_save, sender=MonsterInstance)
@receiver(post_save, sender=RuneInstance)
@receiver(post_save, sender=RuneCraftInstance)
def update_profile_date(sender, instance, **kwargs):
    instance.owner.save()
