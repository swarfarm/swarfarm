from herders.models import Monster, MonsterSource


def set_sources():
    unknown_scroll = MonsterSource.objects.get(name='Unknown Scroll or Social Summon')
    mystical_scroll = MonsterSource.objects.get(name='Mystical Scroll or Crystal Summon')
    legendary_scroll = MonsterSource.objects.get(name='Legendary Scroll')
    fire_scroll = MonsterSource.objects.get(name='Fire Scroll')
    water_scroll = MonsterSource.objects.get(name='Water Scroll')
    wind_scroll = MonsterSource.objects.get(name='Wind Scroll')
    light_dark_scroll = MonsterSource.objects.get(name='Scroll of Light and Darkness')
    unsummonable_monsters = ['Ifrit', 'Cow Girl', 'Magical Archer (Fami)', 'Fairy Queen']

    for monster in Monster.objects.filter(obtainable=True, is_awakened=False):
        print monster.name

        # Unknown Scroll/Social Summon
        if monster.base_stars <= 3 and monster.element in [Monster.ELEMENT_FIRE, monster.ELEMENT_WIND, monster.ELEMENT_WATER] and monster.name not in unsummonable_monsters:
            monster.source.add(unknown_scroll)

        # Mystical Scroll/Crystal Summon
        if monster.base_stars >= 3 and monster.element in [Monster.ELEMENT_FIRE, monster.ELEMENT_WIND, monster.ELEMENT_WATER] and monster.name not in unsummonable_monsters:
            monster.source.add(mystical_scroll)

        # Legendary scroll
        if monster.base_stars >= 4 and monster.element in [Monster.ELEMENT_FIRE, monster.ELEMENT_WIND, monster.ELEMENT_WATER] and monster.name not in unsummonable_monsters:
            monster.source.add(legendary_scroll)

        # Elemental scrolls
        if monster.base_stars >= 3 and monster.element == Monster.ELEMENT_FIRE and monster.name not in unsummonable_monsters:
            monster.source.add(fire_scroll)

        if monster.base_stars >= 3 and monster.element == Monster.ELEMENT_WATER and monster.name not in unsummonable_monsters:
            monster.source.add(water_scroll)

        if monster.base_stars >= 3 and monster.element == Monster.ELEMENT_WIND and monster.name not in unsummonable_monsters:
            monster.source.add(wind_scroll)

        # Scroll of Light and Darkness
        if monster.base_stars >= 3 and monster.element in [Monster.ELEMENT_DARK, Monster.ELEMENT_LIGHT] and monster.name not in unsummonable_monsters:
            monster.source.add(light_dark_scroll)

    # Now re-save all awakened monsters so they pull the sources from the unawakened versions
    for monster in Monster.objects.filter(obtainable=True, is_awakened=True):
        print monster
        monster.save(skip_url_gen=True)

    print 'Done!'
