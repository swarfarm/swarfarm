from bestiary.models import Monster
from herders.models import RuneInstance, RuneCraftInstance, Summoner
from .models import RunLog, SummonLog, RuneDrop, ItemDrop

element_map = {
    1: Monster.ELEMENT_WATER,
    2: Monster.ELEMENT_FIRE,
    3: Monster.ELEMENT_WIND,
    4: Monster.ELEMENT_LIGHT,
    5: Monster.ELEMENT_DARK,
}

building_id_map = {
    'summoners_tower': 1,
    'summonhenge': 2,
    'pond_of_mana': 3,
    'crystal_mine': 4,
    'gateway': 8,
    'temple_of_wishes': 10,
    'magic_shop': 11,
    'ancient_stones': 12,
    'arcane_tower': 14,
    'crystal_titan': 15,
    'fusion_hexagram': 16,
    'fuse_center': 17,
    'power_up_circle': 20,
    'tranquil_forest': 22,
    'gusty_cliffs': 23,
    'deep_forest_ent': 24,
    'monster_storage': 25,
    'transmogrification_building': 27,
}

decoration_id_map = {
    'guardstone': 4,
    'mana_fountain': 5,
    'sky_tribe_totem': 6,
    'arcane_booster_tower': 7,
    'crystal_altar': 8,
    'ancient_sword': 9,
    'sanctum_of_energy': 10,
    'mysterious_plant': 11,
    'fire_sanctuary': 15,
    'water_sanctuary': 16,
    'wind_sanctuary': 17,
    'light_sanctuary': 18,
    'dark_sanctuary': 19,
    'fallen_ancient_guardian': 31,
    'crystal_rock': 34,
    'fairy_tree': 35,
    'flag_of_battle': 36,
    'flag_of_rage': 37,
    'flag_of_hope': 38,
    'flag_of_will': 39,
}

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
    'rune_craft': 27,
    'craft_stuff': 29,
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
    19: RuneInstance.TYPE_FIGHT,
    20: RuneInstance.TYPE_DETERMINATION,
    21: RuneInstance.TYPE_ENHANCE,
    22: RuneInstance.TYPE_ACCURACY,
    23: RuneInstance.TYPE_TOLERANCE,
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

craft_type_map = {
    1: RuneInstance.CRAFT_ENCHANT_GEM,
    2: RuneInstance.CRAFT_GRINDSTONE,
}

craft_quality_map = {
    1: RuneCraftInstance.QUALITY_NORMAL,
    2: RuneCraftInstance.QUALITY_MAGIC,
    3: RuneCraftInstance.QUALITY_RARE,
    4: RuneCraftInstance.QUALITY_HERO,
    5: RuneCraftInstance.QUALITY_LEGEND,
}

scenario_difficulty_map = {
    1: RunLog.DIFFICULTY_NORMAL,
    2: RunLog.DIFFICULTY_HARD,
    3: RunLog.DIFFICULTY_HELL,
}

summon_source_map = {
    1: SummonLog.SCROLL_UNKNOWN,
    2: SummonLog.SCROLL_MYSTICAL,
    3: SummonLog.SCROLL_LIGHT_AND_DARK,
    4: SummonLog.SCROLL_WATER,
    5: SummonLog.SCROLL_FIRE,
    6: SummonLog.SCROLL_WIND,
    7: SummonLog.SCROLL_LEGENDARY,
    8: SummonLog.SUMMON_EXCLUSIVE,
    9: SummonLog.SUMMON_LEGENDARY_PIECES,
    10: SummonLog.SUMMON_LIGHT_AND_DARK_PIECES,
    11: SummonLog.SCROLL_TRANSCENDANCE,
}

drop_essence_map = {
    11006: RunLog.DROP_ESSENCE_MAGIC_LOW,
    12006: RunLog.DROP_ESSENCE_MAGIC_MID,
    13006: RunLog.DROP_ESSENCE_MAGIC_HIGH,
    11001: RunLog.DROP_ESSENCE_WATER_LOW,
    12001: RunLog.DROP_ESSENCE_WATER_MID,
    13001: RunLog.DROP_ESSENCE_WATER_HIGH,
    11002: RunLog.DROP_ESSENCE_FIRE_LOW,
    12002: RunLog.DROP_ESSENCE_FIRE_MID,
    13002: RunLog.DROP_ESSENCE_FIRE_HIGH,
    11003: RunLog.DROP_ESSENCE_WIND_LOW,
    12003: RunLog.DROP_ESSENCE_WIND_MID,
    13003: RunLog.DROP_ESSENCE_WIND_HIGH,
    11004: RunLog.DROP_ESSENCE_LIGHT_LOW,
    12004: RunLog.DROP_ESSENCE_LIGHT_MID,
    13004: RunLog.DROP_ESSENCE_LIGHT_HIGH,
    11005: RunLog.DROP_ESSENCE_DARK_LOW,
    12005: RunLog.DROP_ESSENCE_DARK_MID,
    13005: RunLog.DROP_ESSENCE_DARK_HIGH,
}

drop_craft_map = {
    1001: RunLog.DROP_CRAFT_WOOD,
    1002: RunLog.DROP_CRAFT_LEATHER,
    1003: RunLog.DROP_CRAFT_ROCK,
    1004: RunLog.DROP_CRAFT_ORE,
    1005: RunLog.DROP_CRAFT_MITHRIL,
    1006: RunLog.DROP_CRAFT_CLOTH,
    2001: RunLog.DROP_CRAFT_RUNE_PIECE,
    3001: RunLog.DROP_CRAFT_POWDER,
    4001: RunLog.DROP_CRAFT_SYMBOL_HARMONY,
    4002: RunLog.DROP_CRAFT_SYMBOL_TRANSCENDANCE,
    4003: RunLog.DROP_CRAFT_SYMBOL_CHAOS,
    5001: RunLog.DROP_CRAFT_CRYSTAL_WATER,
    5002: RunLog.DROP_CRAFT_CRYSTAL_FIRE,
    5003: RunLog.DROP_CRAFT_CRYSTAL_WIND,
    5004: RunLog.DROP_CRAFT_CRYSTAL_LIGHT,
    5005: RunLog.DROP_CRAFT_CRYSTAL_DARK,
    6001: RunLog.DROP_CRAFT_CRYSTAL_MAGIC,
    7001: RunLog.DROP_CRAFT_CRYSTAL_PURE,
}

drop_currency_map = {
    1: ItemDrop.DROP_CURRENCY_CRYSTALS,
    2: ItemDrop.DROP_CURRENCY_SOCIAL,
    3: ItemDrop.DROP_CURRENCY_REAL_MONEY,
    4: ItemDrop.DROP_CURRENCY_GLORY_POINT,
    5: ItemDrop.DROP_CURRENCY_GUILD_POINT,
    6: ItemDrop.DROP_COSTUME_POINT,
    102: ItemDrop.DROP_CURRENCY_MANA,
    103: ItemDrop.DROP_CURRENCY_ENERGY,
    104: ItemDrop.DROP_CURRENCY_ARENA_WING,
}

timezone_server_map = {
    'America/Los_Angeles': Summoner.SERVER_GLOBAL,
    'Europe/Berlin': Summoner.SERVER_EUROPE,
    'Asia/Seoul': Summoner.SERVER_KOREA,
    'Asia/Shanghai': Summoner.SERVER_ASIA,
}

valid_rune_drop_map = {
    1: [RuneDrop.TYPE_ENERGY],
    2: [RuneDrop.TYPE_FATAL],
    3: [RuneDrop.TYPE_BLADE],
    4: [RuneDrop.TYPE_SWIFT],
    5: [RuneDrop.TYPE_FOCUS],
    6: [RuneDrop.TYPE_GUARD],
    7: [RuneDrop.TYPE_ENDURE],
    8: [RuneDrop.TYPE_SHIELD],
    9: [RuneDrop.TYPE_REVENGE],
    10: [RuneDrop.TYPE_WILL],
    11: [RuneDrop.TYPE_NEMESIS],
    12: [RuneDrop.TYPE_VAMPIRE],
    13: [RuneDrop.TYPE_DESTROY],
    6001: [RuneDrop.TYPE_RAGE, RuneDrop.TYPE_WILL, RuneDrop.TYPE_NEMESIS, RuneDrop.TYPE_VAMPIRE, RuneDrop.TYPE_DESTROY],
    8001: [RuneDrop.TYPE_DESPAIR, RuneDrop.TYPE_ENERGY, RuneDrop.TYPE_FATAL, RuneDrop.TYPE_BLADE, RuneDrop.TYPE_SWIFT],
    9001: [RuneDrop.TYPE_VIOLENT, RuneDrop.TYPE_FOCUS, RuneDrop.TYPE_GUARD, RuneDrop.TYPE_ENDURE, RuneDrop.TYPE_SHIELD, RuneDrop.TYPE_REVENGE],
}
