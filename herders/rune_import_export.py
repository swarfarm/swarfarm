from django.forms import ValidationError
from herders.models import RuneInstance

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
        raise ValidationError('Unable to decode rune type.')

    rune.stars = grade
    rune.level = level
    rune.slot = slot

    if main_stat in stat_decode_dict:
        rune.main_stat = stat_decode_dict[main_stat]
        rune.main_stat_value = main_stat_value
    else:
        raise ValidationError('Unable to decode main stat type.')

    if innate_stat:
        if innate_stat in stat_decode_dict:
            rune.innate_stat = stat_decode_dict[innate_stat]
            if rune.innate_stat_value > 0:
                rune.innate_stat_value = innate_stat_value
            else:
                raise ValidationError('Innate stat value is 0 or lower')
        else:
            raise ValidationError('Innate stat is present but unable to decode')

    if substat_1_stat:
        if substat_1_stat in stat_decode_dict:
            rune.substat_1 = stat_decode_dict[substat_1_stat]
            rune.substat_1_value = substat_1_value
        else:
            raise ValidationError('Substat 1 is present but unable to decode')

    if substat_2_stat:
        if substat_2_stat in stat_decode_dict:
            rune.substat_2 = stat_decode_dict[substat_2_stat]
            rune.substat_2_value = substat_2_value
        else:
            raise ValidationError('Substat 2 is present but unable to decode')

    if substat_3_stat:
        if substat_3_stat in stat_decode_dict:
            rune.substat_3 = stat_decode_dict[substat_3_stat]
            rune.substat_3_value = substat_3_value
        else:
            raise ValidationError('Substat 3 is present but unable to decode')

    if substat_4_stat:
        if substat_4_stat in stat_decode_dict:
            rune.substat_4 = stat_decode_dict[substat_4_stat]
            rune.substat_4_value = substat_4_value
        else:
            raise ValidationError('Substat 4 is present but unable to decode')

    return rune


def export_rune(rune):
    pass
