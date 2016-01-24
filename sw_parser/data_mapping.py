from herders.models import Monster, RuneInstance

element_map = {
    1: Monster.ELEMENT_WATER,
    2: Monster.ELEMENT_FIRE,
    3: Monster.ELEMENT_WIND,
    4: Monster.ELEMENT_LIGHT,
    5: Monster.ELEMENT_DARK,
}

building_map = {
    1: "Summoner's Tower",
    2: '',
    3: 'pond_of_mana',
    4: '',
    5: '',
    6: '',
    7: '',
    8: '',
    9: '',
    10: '',
    11: '',
    12: 'ancient_stones',
    13: '',
    14: '',
    15: '',
    16: '',
    17: '',
    18: '',
    19: '',
    20: '',
    21: '',
    22: 'tranquil_forest',
    23: '',
    24: 'deep_forest_ent',
    25: 'monster_storage',
    26: '',
    27: '',
}

inventory_type_map = {
    'inventory': 11,
    'monster_piece': 12,
}

inventory_essence_map = {
    11006: "storage_magic_low",
    12006: "storage_magic_mid",
    13006: "storage_magic_high",
    11001: "storage_water_low",
    12001: "storage_water_mid",
    13001: "storage_water_high",
    11002: "storage_fire_low",
    12002: "storage_fire_mid",
    13002: "storage_fire_high",
    11003: "storage_wind_low",
    12003: "storage_wind_mid",
    13003: "storage_wind_high",
    11004: "storage_light_low",
    12004: "storage_light_mid",
    13004: "storage_light_high",
    11005: "storage_dark_low",
    12005: "storage_dark_mid",
    13005: "storage_dark_high",
}

rune_set_map = {
    1: RuneInstance.TYPE_ENERGY,
    2: RuneInstance.TYPE_GUARD,
    3: RuneInstance.TYPE_SWIFT,
    4: RuneInstance.TYPE_BLADE,
    5: RuneInstance.TYPE_RAGE,
    6: RuneInstance.TYPE_FOCUS,
    7: RuneInstance.TYPE_ENDURE,
    8: RuneInstance.TYPE_FATAL,
    10: RuneInstance.TYPE_DESPAIR,
    11: RuneInstance.TYPE_VAMPIRE,
    13: RuneInstance.TYPE_VIOLENT,
    14: RuneInstance.TYPE_NEMESIS,
    15: RuneInstance.TYPE_WILL,
    16: RuneInstance.TYPE_SHIELD,
    17: RuneInstance.TYPE_REVENGE,
    18: RuneInstance.TYPE_DESTROY,
}

rune_stat_type_map = {
    1: RuneInstance.STAT_HP,
    2: RuneInstance.STAT_HP_PCT,
    3: RuneInstance.STAT_ATK,
    4: RuneInstance.STAT_ATK_PCT,
    5: RuneInstance.STAT_DEF,
    6: RuneInstance.STAT_DEF_PCT,
    8: RuneInstance.STAT_SPD,
    9: RuneInstance.STAT_CRIT_RATE_PCT,
    10: RuneInstance.STAT_CRIT_DMG_PCT,
    11: RuneInstance.STAT_RESIST_PCT,
    12: RuneInstance.STAT_ACCURACY_PCT,
}
