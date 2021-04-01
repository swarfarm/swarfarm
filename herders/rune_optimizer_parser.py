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

    # Build the artifact list
    artifact_list = []
    for a in ArtifactInstance.objects.filter(owner=summoner):
        artifact_list.append(_convert_artifact_to_win10_json(a))

    # Build the artifact craft list
    artifact_craft_list = []
    for c in ArtifactCraftInstance.objects.filter(owner=summoner):
        artifact_craft_list.append(_convert_artifact_craft_to_win10_json(c))

    # Build the decoration list
    deco_list = []
    for d in BuildingInstance.objects.filter(owner=summoner):
        deco_list.append(_convert_deco_to_win10(d))

    return json.dumps({
        'building_list': buildings,
        'unit_list': unit_list,
        'runes': runes,
        'rune_craft_item_list': rune_craft_item_list,
        'artifacts': artifact_list,
        'artifact_crafts': artifact_craft_list,
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
        'extra': quality_map.get(rune.original_quality, 0),
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
        'artifacts': [],
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

    # Fill in runes and artifacts
    for rune in monster.runes.all():
        mon_json['runes'].append(_convert_rune_to_win10_json(rune))

    for artifact in monster.artifacts.all():
        mon_json['artifacts'].append(_convert_artifact_to_win10_json(artifact))

    return mon_json


def _convert_rune_craft_to_win10_json(craft):
    quality = quality_map[craft.quality]
    stat = rune_stat_type_map[craft.stat]
    rune_set = rune_set_map.get(craft.rune, 99)

    return {
        'craft_type_id': int('{:d}{:02d}{:02d}'.format(rune_set, stat, quality)),
        'craft_type': craft_type_map[craft.type],
        'craft_item_id': craft.com2us_id if craft.com2us_id else random.randint(1, 999999999),
        'amount': craft.quantity,
    }


def _convert_artifact_to_win10_json(artifact):
    effects_data = zip(
        [artifact_effect_map[eff] for eff in artifact.effects],
        artifact.effects,
        artifact.effects_value,
        artifact.effects_upgrade_count,
        [0] * len(artifact.effects),
        artifact.effects_reroll_count,
    )

    sec_eff = []
    for effect in effects_data:
        sec_eff.append(list(effect))

    return {
        'rid': artifact.com2us_id,
        'occupied_id': artifact.assigned_to.com2us_id if artifact.assigned_to else 0,
        'slot': 0,
        'type': artifact_type_map[artifact.slot],
        'attribute': element_map[artifact.element] if artifact.element else 0,
        'unit_style': archetype_map[artifact.archetype] if artifact.archetype else 0,
        'natural_rank': quality_map[artifact.original_quality],
        'rank': quality_map[artifact.quality],
        'level': artifact.level,
        'pri_effect': [
            artifact_main_stat_map[artifact.main_stat],
            artifact.main_stat_value,
            artifact.level,
            0,
            0,
        ],
        'sec_effects': sec_eff,
    }


def _convert_artifact_craft_to_win10_json(craft):
    craft_type = artifact_type_map[craft.slot]
    element = element_map[craft.element] if craft.element else 0
    archetype = archetype_map[craft.archetype] if craft.archetype else 0
    quality = quality_map[craft.quality]
    effect = artifact_effect_map[craft.effect]

    return {
        'master_id': int(f'1{craft_type:02d}{element:02d}{archetype:02d}{quality:02d}{effect:03d}'),
        'type': craft_type,
        'quantity': craft.quantity,
    }


def _convert_deco_to_win10(decoration):
    return {
        'master_id': decoration.building.com2us_id,
        'level': decoration.level,
    }
