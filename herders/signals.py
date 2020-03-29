from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import MonsterInstance, RuneInstance, RuneBuild, RuneCraftInstance


@receiver(post_save, sender=MonsterInstance)
@receiver(post_save, sender=RuneInstance)
@receiver(post_save, sender=RuneCraftInstance)
def update_profile_date(sender, instance, **kwargs):
    instance.owner.save()


@receiver(m2m_changed, sender=RuneBuild.runes.through)
def validate_rune_build_runes(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action != 'pre_add':
        return

    too_many_slots = model.objects.filter(
        pk__in=pk_set
    ).values('slot').annotate(
        slot__count=Count('slot')
    ).filter(
        slot__count__gt=1
    ).order_by('slot')

    if too_many_slots.exists():
        errors = []
        for result in too_many_slots:
            errors.append(ValidationError(
                {
                    'runes': ValidationError(
                        'Too many runes in slot %(slot)d!',
                        params={'slot': result['slot']}
                    )
                }
            ))

        raise ValidationError(errors)


@receiver(m2m_changed, sender=RuneBuild.runes.through)
def update_rune_build_stats(sender, instance, action, **kwargs):
    if action not in ['post_add', 'post_clear', 'post_remove']:
        return

    instance.update_stats()
    instance.save()
