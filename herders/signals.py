from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import Monster


#@receiver(m2m_changed, sender=Monster.source.through) # TODO: Reenable this after saving all sources.
def monster_source_changed(sender, **kwargs):
    action = kwargs.pop('action', None)
    reverse = kwargs.pop('reverse', None)
    instance = kwargs.pop('instance', None)

    if action in ['post_add', 'post_clear'] and not reverse:
        # Update farmable status
        instance.farmable = instance.source.filter(farmable_source=True).count() > 0
        instance.save(skip_url_gen=True)
