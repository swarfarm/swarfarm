from bestiary.models import Monster, LeaderSkill, Rune, RuneCraft

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

craft_type_map = {
    1: RuneCraft.CRAFT_ENCHANT_GEM,
    2: RuneCraft.CRAFT_GRINDSTONE,
    3: RuneCraft.CRAFT_IMMEMORIAL_GEM,
    4: RuneCraft.CRAFT_IMMEMORIAL_GRINDSTONE,
}

craft_quality_map = {
    1: RuneCraft.QUALITY_NORMAL,
    2: RuneCraft.QUALITY_MAGIC,
    3: RuneCraft.QUALITY_RARE,
    4: RuneCraft.QUALITY_HERO,
    5: RuneCraft.QUALITY_LEGEND,
}
