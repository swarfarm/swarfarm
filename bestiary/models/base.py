# Definitions of commonly reused elements in the game


class Elements:
    ELEMENT_PURE = 'pure'
    ELEMENT_FIRE = 'fire'
    ELEMENT_WIND = 'wind'
    ELEMENT_WATER = 'water'
    ELEMENT_LIGHT = 'light'
    ELEMENT_DARK = 'dark'

    ELEMENT_CHOICES = (
        (ELEMENT_PURE, 'Pure'),
        (ELEMENT_FIRE, 'Fire'),
        (ELEMENT_WIND, 'Wind'),
        (ELEMENT_WATER, 'Water'),
        (ELEMENT_LIGHT, 'Light'),
        (ELEMENT_DARK, 'Dark'),
    )

    # Mappings from com2us' API data to model defined values
    COM2US_ELEMENT_MAP = {
        1: ELEMENT_WATER,
        2: ELEMENT_FIRE,
        3: ELEMENT_WIND,
        4: ELEMENT_LIGHT,
        5: ELEMENT_DARK,
        6: ELEMENT_PURE,
    }


class Stats:
    STAT_HP = 1
    STAT_HP_PCT = 2
    STAT_ATK = 3
    STAT_ATK_PCT = 4
    STAT_DEF = 5
    STAT_DEF_PCT = 6
    STAT_SPD = 7
    STAT_CRIT_RATE_PCT = 8
    STAT_CRIT_DMG_PCT = 9
    STAT_RESIST_PCT = 10
    STAT_ACCURACY_PCT = 11

    # Used for selecting type of stat in form
    STAT_CHOICES = (
        (STAT_HP, 'HP'),
        (STAT_HP_PCT, 'HP %'),
        (STAT_ATK, 'ATK'),
        (STAT_ATK_PCT, 'ATK %'),
        (STAT_DEF, 'DEF'),
        (STAT_DEF_PCT, 'DEF %'),
        (STAT_SPD, 'SPD'),
        (STAT_CRIT_RATE_PCT, 'CRI Rate %'),
        (STAT_CRIT_DMG_PCT, 'CRI Dmg %'),
        (STAT_RESIST_PCT, 'Resistance %'),
        (STAT_ACCURACY_PCT, 'Accuracy %'),
    )

    STAT_DISPLAY = {
        STAT_HP: 'HP',
        STAT_HP_PCT: 'HP',
        STAT_ATK: 'ATK',
        STAT_ATK_PCT: 'ATK',
        STAT_DEF: 'DEF',
        STAT_DEF_PCT: 'DEF',
        STAT_SPD: 'SPD',
        STAT_CRIT_RATE_PCT: 'CRI Rate',
        STAT_CRIT_DMG_PCT: 'CRI Dmg',
        STAT_RESIST_PCT: 'Resistance',
        STAT_ACCURACY_PCT: 'Accuracy',
    }

    PERCENT_STATS = (
        STAT_HP_PCT,
        STAT_ATK_PCT,
        STAT_DEF_PCT,
        STAT_CRIT_RATE_PCT,
        STAT_CRIT_DMG_PCT,
        STAT_RESIST_PCT,
        STAT_ACCURACY_PCT,
    )

    FLAT_STATS = (
        STAT_HP,
        STAT_ATK,
        STAT_DEF,
        STAT_SPD,
    )

    COM2US_STAT_MAP = {
        1: STAT_HP,
        2: STAT_HP_PCT,
        3: STAT_ATK,
        4: STAT_ATK_PCT,
        5: STAT_DEF,
        6: STAT_DEF_PCT,
        8: STAT_SPD,
        9: STAT_CRIT_RATE_PCT,
        10: STAT_CRIT_DMG_PCT,
        11: STAT_RESIST_PCT,
        12: STAT_ACCURACY_PCT,
    }

    COM2US_STAT_ATTRIBUTES = {
        STAT_HP: 'base con',
        STAT_ATK: 'base atk',
        STAT_DEF: 'base def',
        STAT_SPD: 'base speed',
        STAT_CRIT_RATE_PCT: 'critical rate',
        STAT_CRIT_DMG_PCT: 'critical damage',
        STAT_RESIST_PCT: 'resistance',
        STAT_ACCURACY_PCT: 'accuracy',
    }


class Quality:
    QUALITY_NORMAL = 0
    QUALITY_MAGIC = 1
    QUALITY_RARE = 2
    QUALITY_HERO = 3
    QUALITY_LEGEND = 4

    QUALITY_CHOICES = (
        (QUALITY_NORMAL, 'Normal'),
        (QUALITY_MAGIC, 'Magic'),
        (QUALITY_RARE, 'Rare'),
        (QUALITY_HERO, 'Hero'),
        (QUALITY_LEGEND, 'Legend'),
    )

    COM2US_QUALITY_MAP = {
        1: QUALITY_NORMAL,
        2: QUALITY_MAGIC,
        3: QUALITY_RARE,
        4: QUALITY_HERO,
        5: QUALITY_LEGEND,
    }