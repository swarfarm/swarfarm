from django.forms import ValidationError
import json
import random

from herders.models import MonsterInstance, RuneCraftInstance, BuildingInstance
from .rune_optimizer_mapping import *
from .com2us_mapping import building_id_map


def export_runes(monsters, unassigned_runes):
    rune_id = 1
    monster_id = 1
    exported_runes = []
    exported_monsters = []

    runed_monsters = monsters.filter(runeinstance__isnull=False).distinct()
    unruned_monsters = monsters.filter(runeinstance=None)

    # First export runes which are assigned to monsters so we can keep the association
    for monster in runed_monsters:
        json_monster = _convert_monster_to_json(monster)
        json_monster['id'] = monster_id

        assigned_runes = monster.runeinstance_set.all()

        for rune in assigned_runes:
            json_rune = _convert_rune_to_json(rune)
            json_rune['id'] = rune_id
            json_rune['monster'] = json_monster['id']
            json_rune['monster_n'] = json_monster['name']

            exported_runes.append(json_rune)
            rune_id += 1

        exported_monsters.append(json_monster)
        monster_id += 1

    # Second export all unruned monsters
    for monster in unruned_monsters:
        json_monster = _convert_monster_to_json(monster)
        json_monster['id'] = monster_id

        exported_monsters.append(json_monster)
        monster_id += 1

    # Now export all unassigned runes
    for rune in unassigned_runes:
        json_rune = _convert_rune_to_json(rune)
        json_rune['id'] = rune_id

        exported_runes.append(json_rune)
        rune_id += 1

    return json.dumps({'runes': exported_runes, 'mons': exported_monsters, 'savedBuilds': []}, indent=4)


def _convert_rune_to_json(rune):
    exported_rune = {
        'id': 0,
        'item_id': rune.com2us_id,
        'monster': 0,
        'monster_n': 'Inventory',
        'set': type_encode_dict[rune.type],
        'slot': rune.slot,
        'grade': rune.stars,
        'level': rune.level,
        'm_t': stat_encode_dict[rune.main_stat],
        'm_v': rune.main_stat_value,
        'i_t': '',
        'i_v': '',
        's1_t': '',
        's1_v': '',
        's1_data': {'gvalue': 0, 'enchanted': False},
        's2_t': '',
        's2_v': '',
        's2_data': {'gvalue': 0, 'enchanted': False},
        's3_t': '',
        's3_v': '',
        's3_data': {'gvalue': 0, 'enchanted': False},
        's4_t': '',
        's4_v': '',
        's4_data': {'gvalue': 0, 'enchanted': False},
        'locked': 0,
        'sub_hpp': '-',
        'sub_hpf': '-',
        'sub_atkp': '-',
        'sub_atkf': '-',
        'sub_defp': '-',
        'sub_deff': '-',
        'sub_crate': '-',
        'sub_cdmg': '-',
        'sub_spd': '-',
        'sub_acc': '-',
        'sub_res': '-',
    }

    if rune.innate_stat:
        exported_rune['i_t'] = stat_encode_dict[rune.innate_stat]
        exported_rune['i_v'] = rune.innate_stat_value

    if rune.substat_1:
        exported_rune['s1_t'] = stat_encode_dict[rune.substat_1]
        exported_rune['s1_v'] = rune.substat_1_value
        if rune.substat_1_craft == RuneInstance.CRAFT_ENCHANT_GEM:
            exported_rune['s1_data']['enchanted'] = True
    else:
        exported_rune['s1_data'] = {}

    if rune.substat_2:
        exported_rune['s2_t'] = stat_encode_dict[rune.substat_2]
        exported_rune['s2_v'] = rune.substat_2_value
        if rune.substat_2_craft == RuneInstance.CRAFT_ENCHANT_GEM:
            exported_rune['s2_data']['enchanted'] = True
    else:
        exported_rune['s2_data'] = {}

    if rune.substat_3:
        exported_rune['s3_t'] = stat_encode_dict[rune.substat_3]
        exported_rune['s3_v'] = rune.substat_3_value
        if rune.substat_3_craft == RuneInstance.CRAFT_ENCHANT_GEM:
            exported_rune['s3_data']['enchanted'] = True
    else:
        exported_rune['s3_data'] = {}

    if rune.substat_4:
        exported_rune['s4_t'] = stat_encode_dict[rune.substat_4]
        exported_rune['s4_v'] = rune.substat_4_value
        if rune.substat_4_craft == RuneInstance.CRAFT_ENCHANT_GEM:
            exported_rune['s4_data']['enchanted'] = True
    else:
        exported_rune['s4_data'] = {}
    # Stat summary values
    sub_hpp = rune.get_stat(RuneInstance.STAT_HP_PCT, True)
    sub_hpf = rune.get_stat(RuneInstance.STAT_HP, True)
    sub_atkp = rune.get_stat(RuneInstance.STAT_ATK_PCT, True)
    sub_atkf = rune.get_stat(RuneInstance.STAT_ATK, True)
    sub_defp = rune.get_stat(RuneInstance.STAT_DEF_PCT, True)
    sub_deff = rune.get_stat(RuneInstance.STAT_DEF, True)
    sub_crate = rune.get_stat(RuneInstance.STAT_CRIT_RATE_PCT, True)
    sub_cdmg = rune.get_stat(RuneInstance.STAT_CRIT_DMG_PCT, True)
    sub_spd = rune.get_stat(RuneInstance.STAT_SPD, True)
    sub_acc = rune.get_stat(RuneInstance.STAT_ACCURACY_PCT, True)
    sub_res = rune.get_stat(RuneInstance.STAT_RESIST_PCT, True)

    if sub_hpp:
        exported_rune['sub_hpp'] = sub_hpp
    if sub_hpf:
        exported_rune['sub_hpf'] = sub_hpf
    if sub_atkp:
        exported_rune['sub_atkp'] = sub_atkp
    if sub_atkf:
        exported_rune['sub_atkf'] = sub_atkf
    if sub_defp:
        exported_rune['sub_defp'] = sub_defp
    if sub_deff:
        exported_rune['sub_deff'] = sub_deff
    if sub_crate:
        exported_rune['sub_crate'] = sub_crate
    if sub_cdmg:
        exported_rune['sub_cdmg'] = sub_cdmg
    if sub_spd:
        exported_rune['sub_spd'] = sub_spd
    if sub_acc:
        exported_rune['sub_acc'] = sub_acc
    if sub_res:
        exported_rune['sub_res'] = sub_res

    return exported_rune


def _convert_monster_to_json(monster):

    return {
        'id': 0,
        'unit_id': monster.com2us_id,
        'master_id': monster.monster.com2us_id,
        'name': str(monster.monster) if not monster.in_storage else str(monster.monster) + '*',
        'attribute': monster.monster.get_element_display(),
        'stars': monster.stars,
        'level': monster.level,
        'location': 'storage' if monster.in_storage else 'inventory',
        'b_hp': monster.base_hp,
        'b_atk': monster.base_attack,
        'b_def': monster.base_defense,
        'b_spd': monster.monster.speed,
        'b_crate': monster.monster.crit_rate,
        'b_cdmg': monster.monster.crit_damage,
        'b_res': monster.monster.resistance,
        'b_acc': monster.monster.accuracy,
    }


def export_win10(summoner):
    # Fake storage building
    storage_bldg_id = 1234567890
    buildings = [
        {
            'building_master_id': building_id_map['monster_storage'],
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
    }

    if rune.substat_1:
        exported_rune['sec_eff'].append([
            rune_stat_type_map[rune.substat_1],
            rune.substat_1_value,
            0,
            0,
        ])

    if rune.substat_2:
        exported_rune['sec_eff'].append([
            rune_stat_type_map[rune.substat_2],
            rune.substat_2_value,
            0,
            0,
        ])

    if rune.substat_3:
        exported_rune['sec_eff'].append([
            rune_stat_type_map[rune.substat_3],
            rune.substat_3_value,
            0,
            0,
        ])

    if rune.substat_4:
        exported_rune['sec_eff'].append([
            rune_stat_type_map[rune.substat_4],
            rune.substat_4_value,
            0,
            0,
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
    rune_set = rune_set_map.get(craft.rune)

    return {
        'craft_type_id': int('{:d}{:02d}{:02d}'.format(rune_set, stat, quality)),
        'craft_type': craft_type_map[craft.type],
        'craft_item_id': craft.com2us_id if craft.com2us_id else random.randint(1, 999999999),
    }


def _convert_deco_to_win10(decoration):
    return {
        'master_id': decoration.building.com2us_id,
        'level': decoration.level,
    }
