from django.db.models import Sum

from bestiary.models import Monster, AwakenCost, MonsterCraftCost, Skill, LeaderSkill, Elements, GameItem, Stats
from bestiary.models.monsters import AwakenBonusType
from bestiary.parse import game_data

from .util import update_bestiary_obj


def _which_stat_increases(raw, awakens_to_id):
    awakens_raw = game_data.tables.MONSTERS[awakens_to_id]
    for stat in [
        Stats.STAT_SPD,
        Stats.STAT_CRIT_RATE_PCT,
        Stats.STAT_CRIT_DMG_PCT,
        Stats.STAT_RESIST_PCT,
        Stats.STAT_ACCURACY_PCT,
    ]:
        awakening_increase = awakens_raw[Stats.COM2US_STAT_ATTRIBUTES[stat]] - raw[Stats.COM2US_STAT_ATTRIBUTES[stat]]

        if awakening_increase > 1:
            if stat == Stats.STAT_SPD:
                # All monsters get a 1spd bonus when awakening, so reduce the supposed increase by 1
                awakening_increase = awakening_increase - 1
            return stat, awakening_increase


def _get_new_skill(raw, awakens_to_id):
    skill_ids = raw['base skill']
    awakened_skill_ids = game_data.tables.MONSTERS[awakens_to_id]['base skill']
    new_skill_id = (set(awakened_skill_ids) - set(skill_ids)).pop()
    return Skill.objects.get(com2us_id=new_skill_id)


def _get_leader_skill(master_id):
    raw = game_data.tables.MONSTERS[master_id]

    if raw['leader skill']:
        stat = LeaderSkill.COM2US_STAT_MAP[raw['leader skill'][3]]
        value = int(raw['leader skill'][4] * 100)
        if raw['leader skill'][2]:
            area_of_effect = LeaderSkill.AREA_ELEMENT
            element = Elements.COM2US_ELEMENT_MAP[raw['leader skill'][2]]
        else:
            area_of_effect = LeaderSkill.COM2US_AREA_MAP[raw['leader skill'][1]]
            element = None

        skill, _ = LeaderSkill.objects.get_or_create(
            attribute=stat,
            amount=value,
            area=area_of_effect,
            element=element,
        )
        return skill
    else:
        return None


def monsters():
    for master_id, raw in game_data.tables.MONSTERS.items():
        raw = preprocess_errata(master_id, raw)

        # Parse basic monster information from game data
        # Awakening info
        can_awaken = raw['awaken rank'] > 0

        if can_awaken:
            is_awakened = raw['awaken'] > 0
            awaken_level = Monster.COM2US_AWAKEN_MAP[raw['awaken']]
        else:
            is_awakened = False
            awaken_level = Monster.AWAKEN_LEVEL_UNAWAKENED

        awaken_materials = {item_id: qty for item_id, qty in raw['awaken materials']}
        awakening_type = AwakenBonusType(raw['awaken type'])
        awakens_to_id = raw['awaken unit id']

        # Awaken bonus text
        if can_awaken and awakens_to_id > 0:
            if awakening_type == AwakenBonusType.STAT_BONUS:
                stat, amount = _which_stat_increases(raw, awakens_to_id)
                stat_name = Stats.STAT_DISPLAY[stat]
                pct = '%' if stat in Stats.PERCENT_STATS else ''
                awaken_bonus_desc = f'Increases {stat_name} by {amount}{pct}'
            elif awakening_type == AwakenBonusType.NEW_SKILL:
                new_skill = _get_new_skill(raw, awakens_to_id)
                awaken_bonus_desc = f'Gain new skill: {new_skill.name}'
            elif awakening_type == AwakenBonusType.LEADER_SKILL:
                awakened_leader_skill = _get_leader_skill(awakens_to_id)
                awaken_bonus_desc = f'Leader Skill: {awakened_leader_skill}'
            elif awakening_type == AwakenBonusType.STRENGTHEN_SKILL:
                new_skill = _get_new_skill(raw, awakens_to_id)
                awaken_bonus_desc = f'Strengthen Skill: {new_skill.name}'
            elif awakening_type == AwakenBonusType.SECONDARY_AWAKENING:
                awaken_bonus_desc = 'Secondary Awakening'
            elif awakening_type == AwakenBonusType.ONLY_AWAKENED:
                awaken_bonus_desc = 'Only available as awakened'
            else:
                raise ValueError(f'Unhandled Awakening Type: {awakening_type}')
        else:
            # Already awakened monsters do not store the description
            awaken_bonus_desc = ''

        skill_set = Skill.objects.filter(com2us_id__in=raw['base skill'])
        skill_max_sum = skill_set.aggregate(skill_max_sum=Sum('max_level'))['skill_max_sum']
        if skill_max_sum:
            skill_ups_to_max = skill_max_sum - skill_set.count()
        else:
            skill_ups_to_max = None

        defaults = {
            'name': game_data.strings.MONSTER_NAMES.get(master_id, raw['unit name']),
            'image_filename': 'unit_icon_{0:04d}_{1}_{2}.png'.format(*raw['thumbnail']),
            'family_id': raw['group id'],
            'archetype': Monster.COM2US_ARCHETYPE_MAP[raw['style type']],
            'element': Monster.COM2US_ELEMENT_MAP[raw['attribute']],
            'obtainable': sum(raw['collection view']) > 0,
            'homunculus': bool(raw['homunculus']),
            'base_stars': raw['base class'],
            'natural_stars': raw['natural class'],
            'raw_hp': raw['base con'],
            'raw_attack': raw['base atk'],
            'raw_defense': raw['base def'],
            'resistance': raw['resistance'],
            'accuracy': raw['accuracy'],
            'speed': raw['base speed'],
            'crit_rate': raw['critical rate'],
            'crit_damage': raw['critical damage'],
            'can_awaken': can_awaken,
            'is_awakened': is_awakened,
            'awaken_level': awaken_level,
            'awaken_bonus': awaken_bonus_desc,
            'awaken_mats_water_low': awaken_materials.get(11001, 0),
            'awaken_mats_water_mid': awaken_materials.get(12001, 0),
            'awaken_mats_water_high': awaken_materials.get(13001, 0),
            'awaken_mats_fire_low': awaken_materials.get(11002, 0),
            'awaken_mats_fire_mid': awaken_materials.get(12002, 0),
            'awaken_mats_fire_high': awaken_materials.get(13002, 0),
            'awaken_mats_wind_low': awaken_materials.get(11003, 0),
            'awaken_mats_wind_mid': awaken_materials.get(12003, 0),
            'awaken_mats_wind_high': awaken_materials.get(13003, 0),
            'awaken_mats_light_low': awaken_materials.get(11004, 0),
            'awaken_mats_light_mid': awaken_materials.get(12004, 0),
            'awaken_mats_light_high': awaken_materials.get(13004, 0),
            'awaken_mats_dark_low': awaken_materials.get(11005, 0),
            'awaken_mats_dark_mid': awaken_materials.get(12005, 0),
            'awaken_mats_dark_high': awaken_materials.get(13005, 0),
            'awaken_mats_magic_low': awaken_materials.get(11006, 0),
            'awaken_mats_magic_mid': awaken_materials.get(12006, 0),
            'awaken_mats_magic_high': awaken_materials.get(13006, 0),
            'leader_skill': _get_leader_skill(master_id),
            'skill_ups_to_max': skill_ups_to_max,
        }

        monster = update_bestiary_obj(Monster, master_id, defaults)

        # Update related fields
        monster.skills.set(skill_set)

        # Awaken cost
        awaken_obj_ids = []
        for item_id, qty in awaken_materials.items():
            obj, _ = AwakenCost.objects.update_or_create(
                monster=monster,
                item=GameItem.objects.get(
                    category=GameItem.CATEGORY_ESSENCE,
                    com2us_id=item_id,
                ),
                defaults={
                    'quantity': qty,
                }
            )
            awaken_obj_ids.append(obj.pk)

        AwakenCost.objects.filter(monster=monster).exclude(pk__in=awaken_obj_ids).delete()

        postprocess_errata(master_id, monster, raw)


def definitely_obtainable(obj, raw):
    obj.obtainable = True
    return obj


def replace_monster_image(raw):
    MONSTER_IMAGES_MAP = {
        210106: [8, 0, 3], # crystal water
        210206: [8, 1, 3], # crystal fire
        210306: [8, 2, 3], # crystal wind
        210406: [8, 3, 3], # crystal light
        210506: [8, 4, 3], # crystal dark
        210606: [8, 0, 3], # crystal water
        210706: [8, 1, 3], # crystal fire
        210806: [8, 2, 3], # crystal wind
        210906: [8, 3, 3], # crystal light
        211006: [8, 4, 3], # crystal dark

        200103: [8, 2, 3], # crystal eye wind
        200113: [8, 2, 3], # crystal eye wind
        200204: [8, 3, 3], # crystal eye light
        200214: [8, 3, 3], # crystal eye light
        112023: [8, 2, 3], # crystal tower eye wind
        112033: [8, 2, 3], # crystal tower eye wind
        112124: [8, 3, 3], # crystal tower eye light
        112134: [8, 3, 3], # crystal tower eye light
    }

    if raw['unit master id'] in MONSTER_IMAGES_MAP:
        raw['thumbnail'] = MONSTER_IMAGES_MAP[raw['unit master id']]

    return raw


def rename_monster_tower(raw):
    raw['unit name'] = "Tower"
    return raw


def rename_monster_crystal_small(raw):
    raw['unit name'] = "Small Crystal"
    return raw


def rename_monster_crystal_medium(raw):
    raw['unit name'] = "Medium Crystal"
    return raw


def rename_monster_midboss(raw):
    raw['unit name'] = "Ancient Intercessor"
    return raw


_preprocess_erratum = {
    # region Caiross Crystals [21xxxx]
    # Missing name and image
    # xx01xx ... xx05xx - small, number says which attribute dungeon (i.e. xx01xx - water)
    # xx06xx ... xx10xx - medium, number + 5 says which attribute dungeon (i.e. xx06xx - water)
    # xxxx06 - pure element
    210106: [rename_monster_crystal_small, replace_monster_image],
    210206: [rename_monster_crystal_small, replace_monster_image],
    210306: [rename_monster_crystal_small, replace_monster_image],
    210406: [rename_monster_crystal_small, replace_monster_image],
    210506: [rename_monster_crystal_small, replace_monster_image],
    210606: [rename_monster_crystal_medium, replace_monster_image],
    210706: [rename_monster_crystal_medium, replace_monster_image],
    210806: [rename_monster_crystal_medium, replace_monster_image],
    210906: [rename_monster_crystal_medium, replace_monster_image],
    211006: [rename_monster_crystal_medium, replace_monster_image],
    # endregion
    
    # region Caiross Towers [10xxxx]
    # Missing name
    # 10008xx, 1011xx, 1014xx, 1015xx, ... - family
    # xxxx1x, xxxx2x - number says which attribute dungeon (i.e. xxxx1x - water, giants)
    # xxxxx6 - pure element
    100116: [rename_monster_tower],
    100126: [rename_monster_tower],
    100136: [rename_monster_tower],
    100146: [rename_monster_tower],
    100156: [rename_monster_tower],

    100216: [rename_monster_tower],
    100226: [rename_monster_tower],
    100236: [rename_monster_tower],
    100246: [rename_monster_tower],
    100256: [rename_monster_tower],

    100316: [rename_monster_tower],
    100326: [rename_monster_tower],
    100336: [rename_monster_tower],
    100346: [rename_monster_tower],
    100356: [rename_monster_tower],

    100416: [rename_monster_tower],
    100426: [rename_monster_tower],
    100436: [rename_monster_tower],
    100446: [rename_monster_tower],
    100456: [rename_monster_tower],

    100516: [rename_monster_tower],
    100526: [rename_monster_tower],
    100536: [rename_monster_tower],
    100546: [rename_monster_tower],
    100556: [rename_monster_tower],

    100616: [rename_monster_tower],
    100626: [rename_monster_tower],
    100636: [rename_monster_tower],
    100646: [rename_monster_tower],
    100656: [rename_monster_tower],
    
    100716: [rename_monster_tower],
    100726: [rename_monster_tower],
    100736: [rename_monster_tower],
    100746: [rename_monster_tower],
    100756: [rename_monster_tower],

    100816: [rename_monster_tower],
    100826: [rename_monster_tower],
    100836: [rename_monster_tower],
    100846: [rename_monster_tower],
    100856: [rename_monster_tower],

    100916: [rename_monster_tower],
    100926: [rename_monster_tower],
    100936: [rename_monster_tower],
    100946: [rename_monster_tower],
    100956: [rename_monster_tower],

    101016: [rename_monster_tower],
    101026: [rename_monster_tower],
    101036: [rename_monster_tower],
    101046: [rename_monster_tower],
    101056: [rename_monster_tower],

    101116: [rename_monster_tower],
    101126: [rename_monster_tower],
    101136: [rename_monster_tower],
    101146: [rename_monster_tower],
    101156: [rename_monster_tower],

    101216: [rename_monster_tower],
    101226: [rename_monster_tower],
    101236: [rename_monster_tower],
    101246: [rename_monster_tower],
    101256: [rename_monster_tower],

    101316: [rename_monster_tower],
    101326: [rename_monster_tower],
    101336: [rename_monster_tower],
    101346: [rename_monster_tower],
    101356: [rename_monster_tower],

    101416: [rename_monster_tower],
    101426: [rename_monster_tower],
    101436: [rename_monster_tower],
    101446: [rename_monster_tower],
    101456: [rename_monster_tower],

    101516: [rename_monster_tower],
    101526: [rename_monster_tower],
    101536: [rename_monster_tower],
    101546: [rename_monster_tower],
    101556: [rename_monster_tower],
    # endregion
    
    # region Caiross Crystal Eyes [200xxx]
    # Missing name
    # 2001xx, 2002xx - family
    # xxxx03, xxxx04 - small, number says which attribute dungeon (i.e. 03 - wind, steel fortress)
    # xxxx13, xxxx14 - medium, number % 10 says which attribute dungeon (i.e. 3 - wind, steel fortress)
    200103: [rename_monster_crystal_small],
    200113: [rename_monster_crystal_medium],
    200204: [rename_monster_crystal_small],
    200214: [rename_monster_crystal_medium],
    # endregion
    
    # region Caiross Mid Bosses [62xxx]
    # Missing name
    # 623xx, 625xx - family
    # xxx03, xxx04 - attribute (i.e. 03 - wind, steel fortress)
    62303: [rename_monster_midboss],
    62504: [rename_monster_midboss],
    # endregion

    # region Caiross Tower Eyes [112xxx]
    # Missing name, boss wave
    # 1120xx, 1121xx - family
    # xxxx2x, xxxx3x - order (2 - left, 3 - right)
    # xxxxx3, xxxxx4 - attribute (i.e. 3 - wind, steel fortress)
    112023: [rename_monster_tower, replace_monster_image],
    112033: [rename_monster_tower, replace_monster_image],
    112124: [rename_monster_tower, replace_monster_image],
    112134: [rename_monster_tower, replace_monster_image],
    # endregion
}

_postprocess_erratum = {
    19305: [definitely_obtainable],  # Dark Cowgirl
    19315: [definitely_obtainable],
    23005: [definitely_obtainable],  # Dark Vampire Lord
    23015: [definitely_obtainable],
}


def preprocess_errata(master_id, raw):
    if master_id in _preprocess_erratum:
        print(f'Preprocessing raw data for {master_id}.')
        for processing_func in _preprocess_erratum[master_id]:
            raw = processing_func(raw)
    return raw


def postprocess_errata(master_id, monster, raw):
    if master_id in _postprocess_erratum:
        print(f'Postprocessing erratum for {master_id}.')
        for processing_func in _postprocess_erratum[master_id]:
            monster = processing_func(monster, raw)
        monster.save()


def monster_relationships():
    for master_id, raw in game_data.tables.MONSTERS.items():
        raw = preprocess_errata(master_id, raw)
        monster = Monster.objects.get(com2us_id=master_id)

        # Awakening
        awakens_to_id = raw['awaken unit id']

        if monster.obtainable and awakens_to_id > 0:
            awakens_to = Monster.objects.get(com2us_id=awakens_to_id)
        else:
            awakens_to = None

        # Transformation
        transforms_to_id = raw['change']

        if transforms_to_id > 0:
            transforms_to = Monster.objects.get(com2us_id=transforms_to_id)
        else:
            transforms_to = None

        defaults = {
            'awakens_to': awakens_to,
            'transforms_to': transforms_to,
        }

        update_bestiary_obj(Monster, master_id, defaults)

        # Ensure awakens_to monster has the correct awakens_from. Many entries awaken to
        # same monster, particularly when transformations are involved, so this is explicitly
        # set instead of using a reverse relationship.
        if awakens_to:
            update_bestiary_obj(Monster, awakens_to.com2us_id, {'awakens_from': monster})


def monster_crafting():
    for master_id, raw in game_data.tables.HOMUNCULUS_CRAFT_COSTS.items():
        for monster_id in raw['unit master id']:
            monster = Monster.objects.get(com2us_id=monster_id)

            # Upgrade cost items
            craft_cost_ids = []
            all_materials = [raw['craft cost']] + raw['craft stuff']

            for item_category, item_id, qty in all_materials:
                obj, _ = MonsterCraftCost.objects.update_or_create(
                    monster=monster,
                    item=GameItem.objects.get(category=item_category, com2us_id=item_id),
                    defaults={
                        'quantity': qty,
                    }
                )
                craft_cost_ids.append(obj.pk)

            # Delete any no longer used
            MonsterCraftCost.objects.filter(monster=monster).exclude(pk__in=craft_cost_ids).delete()
