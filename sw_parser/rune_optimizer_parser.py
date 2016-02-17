from django.forms import ValidationError
from herders.models import RuneInstance
import json

from .rune_optimizer_mapping import *


def import_rune(rune_data):
    rune = RuneInstance()
    rune_id = rune_data.get('id', None)
    rune_type = rune_data.get('set', None)
    grade = rune_data.get('grade', None)
    level = rune_data.get('level', None)
    slot = rune_data.get('slot', None)
    main_stat = rune_data.get('m_t', None)
    main_stat_value = rune_data.get('m_v', None)
    innate_stat = rune_data.get('i_t', None)
    innate_stat_value = rune_data.get('i_v', None)
    substat_1_stat = rune_data.get('s1_t', None)
    substat_1_value = rune_data.get('s1_v', None)
    substat_2_stat = rune_data.get('s2_t', None)
    substat_2_value = rune_data.get('s2_v', None)
    substat_3_stat = rune_data.get('s3_t', None)
    substat_3_value = rune_data.get('s3_v', None)
    substat_4_stat = rune_data.get('s4_t', None)
    substat_4_value = rune_data.get('s4_v', None)

    if rune_type in type_decode_dict:
        rune.type = type_decode_dict[rune_type]
    else:
        raise ValidationError({
            'type': ValidationError(
                'Unable to decode rune type.',
                code='unknown_rune_type',
            )
        })

    rune.stars = grade
    rune.level = level
    rune.slot = slot

    if main_stat in stat_decode_dict:
        rune.main_stat = stat_decode_dict[main_stat]
        if main_stat_value > 0:
            rune.main_stat_value = main_stat_value
        else:
            raise ValidationError({
                'main_stat': ValidationError(
                    'Main stat value is 0 or lower.',
                    code='invalid_main_stat_value',
                )
            })

    else:
        raise ValidationError({
            'main_stat': ValidationError(
                'Unable to decode the main stat type.',
                code='main_stat',
            )
        })

    if innate_stat:
        if innate_stat in stat_decode_dict:
            rune.innate_stat = stat_decode_dict[innate_stat]
            if innate_stat_value > 0:
                rune.innate_stat_value = innate_stat_value
            else:
                raise ValidationError({
                    'innate_stat': ValidationError(
                        'Innate stat value is 0 or lower.',
                        code='invalid_innate_stat_value',
                    )
                })
        else:
            raise ValidationError({
                'innate_stat': ValidationError(
                    'Innate stat is present but unable to decode the stat type.',
                    code='unknown_innate_stat_type',
                )
            })

    if substat_1_stat:
        if substat_1_stat in stat_decode_dict:
            rune.substat_1 = stat_decode_dict[substat_1_stat]
            if substat_1_value > 0:
                rune.substat_1_value = substat_1_value
            else:
                raise ValidationError({
                    'substat_1_stat': ValidationError(
                        'Substat 1 value is 0 or lower.',
                        code='invalid_substat_1_value',
                    )
                })
        else:
            raise ValidationError({
                'substat_1_stat': ValidationError(
                    'Substat 1 is present but unable to decode the stat type.',
                    code='unknown_substat_1_type',
                )
            })

    if substat_2_stat:
        if substat_2_stat in stat_decode_dict:
            rune.substat_2 = stat_decode_dict[substat_2_stat]
            if substat_2_value > 0:
                rune.substat_2_value = substat_2_value
            else:
                raise ValidationError({
                    'substat_2_stat': ValidationError(
                        'Substat 2 value is 0 or lower.',
                        code='invalid_substat_2_value',
                    )
                })
        else:
            raise ValidationError({
                'substat_2_stat': ValidationError(
                    'Substat 2 is present but unable to decode the stat type.',
                    code='unknown_substat_2_type',
                )
            })

    if substat_3_stat:
        if substat_3_stat in stat_decode_dict:
            rune.substat_3 = stat_decode_dict[substat_3_stat]
            if substat_3_value > 0:
                rune.substat_3_value = substat_3_value
            else:
                raise ValidationError({
                    'substat_3_stat': ValidationError(
                        'Substat 3 value is 0 or lower.',
                        code='invalid_substat_3_value',
                    )
                })
        else:
            raise ValidationError({
                'substat_3_stat': ValidationError(
                    'Substat 3 is present but unable to decode the stat type.',
                    code='unknown_substat_3_type',
                )
            })

    if substat_4_stat:
        if substat_4_stat in stat_decode_dict:
            rune.substat_4 = stat_decode_dict[substat_4_stat]
            if substat_4_value > 0:
                rune.substat_4_value = substat_4_value
            else:
                raise ValidationError({
                    'substat_4_stat': ValidationError(
                        'Substat 4 value is 0 or lower.',
                        code='invalid_substat_4_value',
                    )
                })
        else:
            raise ValidationError({
                'substat_4_stat': ValidationError(
                    'Substat 4 is present but unable to decode the stat type.',
                    code='unknown_substat_4_type',
                )
            })

    return rune


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
        's2_t': '',
        's2_v': '',
        's3_t': '',
        's3_v': '',
        's4_t': '',
        's4_v': '',
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

    if rune.substat_2:
        exported_rune['s2_t'] = stat_encode_dict[rune.substat_2]
        exported_rune['s2_v'] = rune.substat_2_value

    if rune.substat_3:
        exported_rune['s3_t'] = stat_encode_dict[rune.substat_3]
        exported_rune['s3_v'] = rune.substat_3_value

    if rune.substat_4:
        exported_rune['s4_t'] = stat_encode_dict[rune.substat_4]
        exported_rune['s4_v'] = rune.substat_4_value

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
        'name': str(monster.monster),
        'level': monster.level,
        'b_hp': monster.base_hp,
        'b_atk': monster.base_attack,
        'b_def': monster.base_defense,
        'b_spd': monster.monster.speed,
        'b_crate': monster.monster.crit_rate,
        'b_cdmg': monster.monster.crit_damage,
        'b_res': monster.monster.resistance,
        'b_acc': monster.monster.accuracy,
    }
