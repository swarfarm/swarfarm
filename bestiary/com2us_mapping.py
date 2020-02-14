from bestiary.models import Rune

# TODO: Move these definitions to the models if not already done, delete this file.

inventory_type_map = {
    'monster': 1,
    'currency': 6,
    'rune': 8,
    'scroll': 9,
    'booster': 10,
    'essences': 11,
    'monster_piece': 12,
    # '': 15, Unknown. Appears in inventory_info with qty 0
    'guild_monster_piece': 19,
    'rainbowmon': 25,   # Possibly material monsters in general. Appears when wish returns a rainbowmon.
    'rune_craft': 27,
    'craft_stuff': 29,
    'enhancing_monster': 61,
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

inventory_craft_map = {
    1001: 'wood',
    1002: 'leather',
    1003: 'rock',
    1004: 'ore',
    1005: 'mithril',
    1006: 'cloth',
    2001: 'rune_piece',
    3001: 'powder',
    4001: 'symbol_harmony',
    4002: 'symbol_transcendance',
    4003: 'symbol_chaos',
    5001: 'crystal_water',
    5002: 'crystal_fire',
    5003: 'crystal_wind',
    5004: 'crystal_light',
    5005: 'crystal_dark',
    6001: 'crystal_magic',
    7001: 'crystal_pure',
}

inventory_enhance_monster_map = {
    142110115: 'water_angelmon',
    142120115: 'fire_angelmon',
    142130115: 'wind_angelmon',
    142140115: 'light_angelmon',
    142150115: 'dark_angelmon',
    182110115: 'water_king_angelmon',
    182120115: 'fire_king_angelmon',
    182130115: 'wind_king_angelmon',
    182140115: 'light_king_angelmon',
    182150115: 'dark_king_angelmon',
    143140220: 'rainbowmon_2_20',
    143140301: 'rainbowmon_3_1',
    143140325: 'rainbowmon_3_25',
    143140401: 'rainbowmon_4_1',
    143140430: 'rainbowmon_4_30',
    143140501: 'rainbowmon_5_1',
    151050101: 'devilmon',
    217140115: 'super_angelmon,'
}

rune_set_map = {
    1: Rune.TYPE_ENERGY,
    2: Rune.TYPE_GUARD,
    3: Rune.TYPE_SWIFT,
    4: Rune.TYPE_BLADE,
    5: Rune.TYPE_RAGE,
    6: Rune.TYPE_FOCUS,
    7: Rune.TYPE_ENDURE,
    8: Rune.TYPE_FATAL,
    10: Rune.TYPE_DESPAIR,
    11: Rune.TYPE_VAMPIRE,
    13: Rune.TYPE_VIOLENT,
    14: Rune.TYPE_NEMESIS,
    15: Rune.TYPE_WILL,
    16: Rune.TYPE_SHIELD,
    17: Rune.TYPE_REVENGE,
    18: Rune.TYPE_DESTROY,
    19: Rune.TYPE_FIGHT,
    20: Rune.TYPE_DETERMINATION,
    21: Rune.TYPE_ENHANCE,
    22: Rune.TYPE_ACCURACY,
    23: Rune.TYPE_TOLERANCE,
}

rune_stat_type_map = {
    1: Rune.STAT_HP,
    2: Rune.STAT_HP_PCT,
    3: Rune.STAT_ATK,
    4: Rune.STAT_ATK_PCT,
    5: Rune.STAT_DEF,
    6: Rune.STAT_DEF_PCT,
    8: Rune.STAT_SPD,
    9: Rune.STAT_CRIT_RATE_PCT,
    10: Rune.STAT_CRIT_DMG_PCT,
    11: Rune.STAT_RESIST_PCT,
    12: Rune.STAT_ACCURACY_PCT,
}

rune_quality_map = {
    1: Rune.QUALITY_NORMAL,
    2: Rune.QUALITY_MAGIC,
    3: Rune.QUALITY_RARE,
    4: Rune.QUALITY_HERO,
    5: Rune.QUALITY_LEGEND,
}
