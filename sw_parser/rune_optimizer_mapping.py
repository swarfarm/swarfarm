from herders.models import RuneInstance, RuneCraftInstance
from bestiary.models import Monster

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
    RuneInstance.TYPE_FIGHT: 'Fight',
    RuneInstance.TYPE_DETERMINATION: 'Determination',
    RuneInstance.TYPE_ENHANCE: 'Enhance',
    RuneInstance.TYPE_ACCURACY: 'Accuracy',
    RuneInstance.TYPE_TOLERANCE: 'Tolerance',
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
    'Fight': RuneInstance.TYPE_FIGHT,
    'Determination': RuneInstance.TYPE_DETERMINATION,
    'Enhance': RuneInstance.TYPE_ENHANCE,
    'Accuracy': RuneInstance.TYPE_ACCURACY,
    'Tolerance': RuneInstance.TYPE_TOLERANCE,
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

element_map = {
    Monster.ELEMENT_WATER: 1,
    Monster.ELEMENT_FIRE: 2,
    Monster.ELEMENT_WIND: 3,
    Monster.ELEMENT_LIGHT: 4,
    Monster.ELEMENT_DARK: 5,
}

rune_set_map = {
    RuneInstance.TYPE_ENERGY: 1,
    RuneInstance.TYPE_GUARD: 2,
    RuneInstance.TYPE_SWIFT: 3,
    RuneInstance.TYPE_BLADE: 4,
    RuneInstance.TYPE_RAGE: 5,
    RuneInstance.TYPE_FOCUS: 6,
    RuneInstance.TYPE_ENDURE: 7,
    RuneInstance.TYPE_FATAL: 8,
    RuneInstance.TYPE_DESPAIR: 10,
    RuneInstance.TYPE_VAMPIRE: 11,
    RuneInstance.TYPE_VIOLENT: 13,
    RuneInstance.TYPE_NEMESIS: 14,
    RuneInstance.TYPE_WILL: 15,
    RuneInstance.TYPE_SHIELD: 16,
    RuneInstance.TYPE_REVENGE: 17,
    RuneInstance.TYPE_DESTROY: 18,
    RuneInstance.TYPE_FIGHT: 19,
    RuneInstance.TYPE_DETERMINATION: 20,
    RuneInstance.TYPE_ENHANCE: 21,
    RuneInstance.TYPE_ACCURACY: 22,
    RuneInstance.TYPE_TOLERANCE: 23,
}

rune_stat_type_map = {
    RuneInstance.STAT_HP: 1,
    RuneInstance.STAT_HP_PCT: 2,
    RuneInstance.STAT_ATK: 3,
    RuneInstance.STAT_ATK_PCT: 4,
    RuneInstance.STAT_DEF: 5,
    RuneInstance.STAT_DEF_PCT: 6,
    RuneInstance.STAT_SPD: 8,
    RuneInstance.STAT_CRIT_RATE_PCT: 9,
    RuneInstance.STAT_CRIT_DMG_PCT: 10,
    RuneInstance.STAT_RESIST_PCT: 11,
    RuneInstance.STAT_ACCURACY_PCT: 12,
}

rune_quality_map = {
    RuneInstance.QUALITY_NORMAL: 1,
    RuneInstance.QUALITY_MAGIC: 2,
    RuneInstance.QUALITY_RARE: 3,
    RuneInstance.QUALITY_HERO: 4,
    RuneInstance.QUALITY_LEGEND: 5,
}

craft_type_map = {
    RuneInstance.CRAFT_ENCHANT_GEM: 1,
    RuneInstance.CRAFT_GRINDSTONE: 2,
}

craft_quality_map = {
    RuneCraftInstance.QUALITY_NORMAL: 1,
    RuneCraftInstance.QUALITY_MAGIC: 2,
    RuneCraftInstance.QUALITY_RARE: 3,
    RuneCraftInstance.QUALITY_HERO: 4,
    RuneCraftInstance.QUALITY_LEGEND: 5,
}
