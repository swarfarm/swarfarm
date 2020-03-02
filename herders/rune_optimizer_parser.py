import json
import random

from herders.models import MonsterInstance, BuildingInstance
from .rune_optimizer_mapping import *


def export_win10(summoner):
    # Fake storage building
    storage_bldg_id = 1234567890
    buildings = [
        {
            'building_master_id': 25,
            'building_id': storage_bldg_id,
        }
    ]

    # Build the unit list
    unit_list = []
    for m in MonsterInstance.objects.filter(owner=summoner):
        unit_list.append(_convert_monster_to_win10_json(m))

    # Build the rune list
    runes = []
    for r in RuneInstance.objects.filter(owner=summoner, assigned_to=None):
        runes.append(_convert_rune_to_win10_json(r))

    # Build the rune craft list
    rune_craft_item_list = []
    for c in RuneCraftInstance.objects.filter(owner=summoner):
        rune_craft_item_list.append(_convert_rune_craft_to_win10_json(c))

    # Build the decoration list
    deco_list = []
    for d in BuildingInstance.objects.filter(owner=summoner):
        deco_list.append(_convert_deco_to_win10(d))

    return json.dumps({
        'building_list': buildings,
        'unit_list': unit_list,
        'runes': runes,
        'rune_craft_item_list': rune_craft_item_list,
        'deco_list': deco_list,
        'wizard_id': summoner.com2us_id if summoner.com2us_id else 0,
    })


def _convert_rune_to_win10_json(rune):
    exported_rune = {
        'occupied_type': 1,
        'occupied_id': rune.assigned_to.com2us_id if rune.assigned_to else 0,
        'sell_value': rune.value,
        'pri_eff': [rune_stat_type_map[rune.main_stat], rune.main_stat_value],
        'prefix_eff': [rune_stat_type_map[rune.innate_stat], rune.innate_stat_value] if rune.innate_stat else [0, 0],
        'slot_no': rune.slot,
        'rank': 0,
        'sec_eff': [],
        'upgrade_curr': rune.level,
        'class': rune.stars,
        'set_id': rune_set_map[rune.type],
        'upgrade_limit': 15,
        'rune_id': rune.com2us_id if rune.com2us_id else random.randint(1, 999999999),
        'extra': rune_quality_map.get(rune.original_quality, 0),
    }

    if rune.ancient:
        exported_rune['class'] += 10
        exported_rune['extra'] += 10

    for substat, value, enchanted, grind_value in zip(rune.substats, rune.substat_values, rune.substats_enchanted, rune.substats_grind_value):
        exported_rune['sec_eff'].append([
            rune_stat_type_map[substat],
            value,
            1 if enchanted else 0,
            grind_value,
        ])

    return exported_rune


def _convert_monster_to_win10_json(monster):
    mon_json = {
        'unit_id': monster.com2us_id if monster.com2us_id else random.randint(1, 999999999),
        'unit_master_id': monster.monster.com2us_id,
        'building_id': 1234567890 if monster.in_storage else 0,
        'island_id': 0,
        'homunculus': 1 if monster.monster.homunculus else 0,
        'attribute': element_map[monster.monster.element],
        'unit_level': monster.level,
        'class': monster.stars,
        'con': monster.base_hp / 15,
        'def': monster.base_defense,
        'atk': monster.base_attack,
        'spd': monster.base_speed,
        'critical_rate': monster.base_crit_rate,
        'critical_damage': monster.base_crit_damage,
        'accuracy': monster.base_accuracy,
        'resist': monster.base_resistance,
        'skills': [],
        'runes': [],
    }

    # Fill in skills
    skill_levels = [
        monster.skill_1_level,
        monster.skill_2_level,
        monster.skill_3_level,
        monster.skill_4_level,
    ]
    for idx, skill in enumerate(monster.monster.skills.all().order_by('slot')):
        mon_json['skills'].append([
            skill.com2us_id,
            skill_levels[idx]
        ])

    # Fill in runes
    for rune in monster.runeinstance_set.all():
        mon_json['runes'].append(_convert_rune_to_win10_json(rune))

    return mon_json


def _convert_rune_craft_to_win10_json(craft):
    quality = craft_quality_map[craft.quality]
    stat = rune_stat_type_map[craft.stat]
    rune_set = rune_set_map.get(craft.rune, 99)

    return {
        'craft_type_id': int('{:d}{:02d}{:02d}'.format(rune_set, stat, quality)),
        'craft_type': craft_type_map[craft.type],
        'craft_item_id': craft.com2us_id if craft.com2us_id else random.randint(1, 999999999),
        'amount': craft.quantity,
    }


def _convert_deco_to_win10(decoration):
    return {
        'master_id': decoration.building.com2us_id,
        'level': decoration.level,
    }
