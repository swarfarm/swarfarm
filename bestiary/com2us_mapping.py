from bestiary.models import Monster, LeaderSkill as LeaderSkill
from herders.models import RuneInstance, RuneCraftInstance

element_map = {
    1: Monster.ELEMENT_WATER,
    2: Monster.ELEMENT_FIRE,
    3: Monster.ELEMENT_WIND,
    4: Monster.ELEMENT_LIGHT,
    5: Monster.ELEMENT_DARK,
    6: Monster.ELEMENT_PURE,
}

archetype_map = {
    0: Monster.TYPE_NONE,
    1: Monster.TYPE_ATTACK,
    2: Monster.TYPE_DEFENSE,
    3: Monster.TYPE_HP,
    4: Monster.TYPE_SUPPORT,
    5: Monster.TYPE_MATERIAL
}

leader_skill_stat_map = {
    1: LeaderSkill.ATTRIBUTE_HP,
    2: LeaderSkill.ATTRIBUTE_ATK,
    3: LeaderSkill.ATTRIBUTE_DEF,
    4: LeaderSkill.ATTRIBUTE_SPD,
    5: LeaderSkill.ATTRIBUTE_CRIT_RATE,
    6: LeaderSkill.ATTRIBUTE_CRIT_DMG,
    7: LeaderSkill.ATTRIBUTE_RESIST,
    8: LeaderSkill.ATTRIBUTE_ACCURACY,
}

leader_skill_area_map = {
    0: LeaderSkill.AREA_GENERAL,
    1: LeaderSkill.AREA_ARENA,
    2: LeaderSkill.AREA_DUNGEON,
    5: LeaderSkill.AREA_GUILD,
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
    'rainbowmon': 25,   # Possibly material monsters in general. Appears when wish returns a rainbowmon.
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

rune_quality_map = {
    1: RuneInstance.QUALITY_NORMAL,
    2: RuneInstance.QUALITY_MAGIC,
    3: RuneInstance.QUALITY_RARE,
    4: RuneInstance.QUALITY_HERO,
    5: RuneInstance.QUALITY_LEGEND,
}

craft_type_map = {
    1: RuneInstance.CRAFT_ENCHANT_GEM,
    2: RuneInstance.CRAFT_GRINDSTONE,
    3: RuneInstance.CRAFT_IMMEMORIAL_GEM,
    4: RuneInstance.CRAFT_IMMEMORIAL_GRINDSTONE,
}

craft_quality_map = {
    1: RuneCraftInstance.QUALITY_NORMAL,
    2: RuneCraftInstance.QUALITY_MAGIC,
    3: RuneCraftInstance.QUALITY_RARE,
    4: RuneCraftInstance.QUALITY_HERO,
    5: RuneCraftInstance.QUALITY_LEGEND,
}
