from django.forms import ValidationError
from herders.models import RuneInstance
import json

type_encode_dict = {
    RuneInstance.TYPE_ENERGY: 'Energy',
    RuneInstance.TYPE_FATAL: 'Fatal',
    RuneInstance.TYPE_BLADE: 'Blade',
    RuneInstance.TYPE_RAGE: 'Rage',
    RuneInstance.TYPE_SWIFT: 'Swift',
    RuneInstance.TYPE_FOCUS: 'Focus',
    RuneInstance.TYPE_GUARD: 'Guard',
    RuneInstance.TYPE_ENDURE: 'Endure',
    RuneInstance.TYPE_VIOLENT: 'Violent',
    RuneInstance.TYPE_WILL: 'Will',
    RuneInstance.TYPE_NEMESIS: 'Nemesis',
    RuneInstance.TYPE_SHIELD: 'Shield',
    RuneInstance.TYPE_REVENGE: 'Revenge',
    RuneInstance.TYPE_DESPAIR: 'Despair',
    RuneInstance.TYPE_VAMPIRE: 'Vampire',
    RuneInstance.TYPE_DESTROY: 'Destroy',
}

stat_encode_dict = {
    RuneInstance.STAT_HP: 'HP flat',
    RuneInstance.STAT_HP_PCT: 'HP%',
    RuneInstance.STAT_DEF: 'DEF flat',
    RuneInstance.STAT_DEF_PCT: 'DEF%',
    RuneInstance.STAT_ATK: 'ATK flat',
    RuneInstance.STAT_ATK_PCT: 'ATK%',
    RuneInstance.STAT_SPD: 'SPD',
    RuneInstance.STAT_CRIT_RATE_PCT: 'CRate',
    RuneInstance.STAT_CRIT_DMG_PCT: 'CDmg',
    RuneInstance.STAT_RESIST_PCT: 'RES',
    RuneInstance.STAT_ACCURACY_PCT: 'ACC',
}

type_decode_dict = {
    'Energy': RuneInstance.TYPE_ENERGY,
    'Fatal': RuneInstance.TYPE_FATAL,
    'Blade': RuneInstance.TYPE_BLADE,
    'Rage': RuneInstance.TYPE_RAGE,
    'Swift': RuneInstance.TYPE_SWIFT,
    'Focus': RuneInstance.TYPE_FOCUS,
    'Guard': RuneInstance.TYPE_GUARD,
    'Endure': RuneInstance.TYPE_ENDURE,
    'Violent': RuneInstance.TYPE_VIOLENT,
    'Will': RuneInstance.TYPE_WILL,
    'Nemesis': RuneInstance.TYPE_NEMESIS,
    'Shield': RuneInstance.TYPE_SHIELD,
    'Revenge': RuneInstance.TYPE_REVENGE,
    'Despair': RuneInstance.TYPE_DESPAIR,
    'Vampire': RuneInstance.TYPE_VAMPIRE,
    'Destroy': RuneInstance.TYPE_DESTROY,
}

stat_decode_dict = {
    'HP flat': RuneInstance.STAT_HP,
    'HP%': RuneInstance.STAT_HP_PCT,
    'DEF flat': RuneInstance.STAT_DEF,
    'DEF%': RuneInstance.STAT_DEF_PCT,
    'ATK flat': RuneInstance.STAT_ATK,
    'ATK%': RuneInstance.STAT_ATK_PCT,
    'SPD': RuneInstance.STAT_SPD,
    'CRate': RuneInstance.STAT_CRIT_RATE_PCT,
    'CDmg': RuneInstance.STAT_CRIT_DMG_PCT,
    'RES': RuneInstance.STAT_RESIST_PCT,
    'ACC': RuneInstance.STAT_ACCURACY_PCT,
}


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
        raise ValidationError('[Rune ID=' + str(rune_id) + '] Unable to decode rune type. Runes prior to this one have been successfully imported.')

    rune.stars = grade
    rune.level = level
    rune.slot = slot

    if main_stat in stat_decode_dict:
        rune.main_stat = stat_decode_dict[main_stat]
        if main_stat_value > 0:
            rune.main_stat_value = main_stat_value
        else:
            raise ValidationError('[Rune ID=' + str(rune_id) + '] Main stat value is 0 or lower. Runes prior to this one have been successfully imported.')
    else:
        raise ValidationError('[Rune ID=' + str(rune_id) + '] Unable to decode main stat type. Runes prior to this one have been successfully imported.')

    if innate_stat:
        if innate_stat in stat_decode_dict:
            rune.innate_stat = stat_decode_dict[innate_stat]
            if innate_stat_value > 0:
                rune.innate_stat_value = innate_stat_value
            else:
                raise ValidationError('[Rune ID=' + str(rune_id) + '] Innate stat value is 0 or lower. Runes prior to this one have been successfully imported.')
        else:
            raise ValidationError('[Rune ID=' + str(rune_id) + '] Innate stat is present but unable to decode. Runes prior to this one have been successfully imported.')

    if substat_1_stat:
        if substat_1_stat in stat_decode_dict:
            rune.substat_1 = stat_decode_dict[substat_1_stat]
            if substat_1_value > 0:
                rune.substat_1_value = substat_1_value
            else:
                raise ValidationError('[Rune ID=' + str(rune_id) + '] Substat 1 value is 0 or lower. Runes prior to this one have been successfully imported.')
        else:
            raise ValidationError('[Rune ID=' + str(rune_id) + '] Substat 1 is present but unable to decode. Runes prior to this one have been successfully imported.')

    if substat_2_stat:
        if substat_2_stat in stat_decode_dict:
            rune.substat_2 = stat_decode_dict[substat_2_stat]
            if substat_2_value > 0:
                rune.substat_2_value = substat_2_value
            else:
                raise ValidationError('[Rune ID=' + str(rune_id) + '] Substat 2 value is 0 or lower. Runes prior to this one have been successfully imported.')
        else:
            raise ValidationError('[Rune ID=' + str(rune_id) + '] Substat 2 is present but unable to decode. Runes prior to this one have been successfully imported.')

    if substat_3_stat:
        if substat_3_stat in stat_decode_dict:
            rune.substat_3 = stat_decode_dict[substat_3_stat]
            if substat_3_value > 0:
                rune.substat_3_value = substat_3_value
            else:
                raise ValidationError('[Rune ID=' + str(rune_id) + '] Substat 3 value is 0 or lower. Runes prior to this one have been successfully imported.')
        else:
            raise ValidationError('[Rune ID=' + str(rune_id) + '] Substat 3 is present but unable to decode. Runes prior to this one have been successfully imported.')

    if substat_4_stat:
        if substat_4_stat in stat_decode_dict:
            rune.substat_4 = stat_decode_dict[substat_4_stat]
            if substat_4_value > 0:
                rune.substat_4_value = substat_4_value
            else:
                raise ValidationError('[Rune ID=' + str(rune_id) + '] Substat 4 value is 0 or lower. Runes prior to this one have been successfully imported.')
        else:
            raise ValidationError('[Rune ID=' + str(rune_id) + '] Substat 4 is present but unable to decode. Runes prior to this one have been successfully imported.')

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

    return json.dumps({'runes': exported_runes, 'mons': exported_monsters, 'savedBuilds': []})


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
