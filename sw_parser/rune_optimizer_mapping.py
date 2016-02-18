from herders.models import RuneInstance

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