from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import Monster, MonsterSource


@receiver(m2m_changed, sender=Monster.source.through)
def monster_source_changed(sender, **kwargs):
    action = kwargs.pop('action', None)
    reverse = kwargs.pop('reverse', None)
    monster = kwargs.pop('instance', None)

    if action in ['pre_add', 'pre_remove', 'post_clear'] and not reverse:
        # Ensure that sources matching specific rules are in the monster sources
        required_sources = set([])
        existing_sources = set(monster.source.values_list('pk', flat=True))
        pk_set = kwargs.pop('pk_set')

        if monster.obtainable and monster.archetype != Monster.TYPE_MATERIAL:
            if monster.is_awakened and monster.base_stars > 1:
                base_stars = monster.base_stars - 1
            else:
                base_stars = monster.base_stars

            # Unknown Scroll/Social Summon
            if base_stars <= 3 and monster.element in [Monster.ELEMENT_FIRE, monster.ELEMENT_WIND, monster.ELEMENT_WATER]:
                required_sources.update([MonsterSource.objects.values_list('pk', flat=True).get(name='Unknown Scroll or Social Summon')])

            # Mystical Scroll/Crystal Summon
            if base_stars >= 3 and monster.element in [Monster.ELEMENT_FIRE, monster.ELEMENT_WIND, monster.ELEMENT_WATER]:
                required_sources.update([MonsterSource.objects.values_list('pk', flat=True).get(name='Mystical Scroll or Crystal Summon')])

            # Legendary scroll
            if base_stars >= 4 and monster.element in [Monster.ELEMENT_FIRE, monster.ELEMENT_WIND, monster.ELEMENT_WATER]:
                required_sources.update([MonsterSource.objects.values_list('pk', flat=True).get(name='Legendary Scroll')])

            # Elemental scrolls
            if base_stars >= 3 and monster.element == Monster.ELEMENT_FIRE:
                required_sources.update([MonsterSource.objects.values_list('pk', flat=True).get(name='Fire Scroll')])

            if base_stars >= 3 and monster.element == Monster.ELEMENT_WATER:
                required_sources.update([MonsterSource.objects.values_list('pk', flat=True).get(name='Water Scroll')])

            if base_stars >= 3 and monster.element == Monster.ELEMENT_WIND:
                required_sources.update([MonsterSource.objects.values_list('pk', flat=True).get(name='Wind Scroll')])

            # Scroll of Light and Darkness
            if base_stars >= 3 and monster.element in [Monster.ELEMENT_DARK, Monster.ELEMENT_LIGHT]:
                required_sources.update([MonsterSource.objects.values_list('pk', flat=True).get(name='Scroll of Light and Darkness')])

        if action == 'pre_add':
            pk_set.update(required_sources)
            pk_set.difference_update(existing_sources)
        elif action == 'pre_remove':
            pk_set.difference_update(required_sources)
        elif action == 'post_clear':
            # Add that shit back
            monster.source.add(*required_sources)

    if action in ['post_add', 'post_clear'] and not reverse:
        # Update farmable status
        monster.farmable = monster.source.filter(farmable_source=True).count() > 0
        monster.save(skip_url_gen=True)
