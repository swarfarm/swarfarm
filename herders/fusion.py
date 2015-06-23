from copy import deepcopy
from collections import OrderedDict

def essences_missing(summoner, ingredients):
    # Calculate how many essences are missing
    # Initialize with the current summoner's storage
    essences_missing_max_leveled = OrderedDict({
        'magic': {
            'low': summoner.storage_magic_low,
            'mid': summoner.storage_magic_mid,
            'high': summoner.storage_magic_high,
        },
        'fire': {
            'low': summoner.storage_fire_low,
            'mid': summoner.storage_fire_mid,
            'high': summoner.storage_fire_high,
        },
        'water': {
            'low': summoner.storage_water_low,
            'mid': summoner.storage_water_mid,
            'high': summoner.storage_water_high,
        },
        'wind': {
            'low': summoner.storage_wind_low,
            'mid': summoner.storage_wind_mid,
            'high': summoner.storage_wind_high,
        },
        'dark': {
            'low': summoner.storage_dark_low,
            'mid': summoner.storage_dark_mid,
            'high': summoner.storage_dark_high,
        },
        'light': {
            'low': summoner.storage_light_low,
            'mid': summoner.storage_light_mid,
            'high': summoner.storage_light_high,
        },
    })

    essences_missing_use_awakened = deepcopy(essences_missing_max_leveled)

    # Method 1: Assume user wants to awaken the highest star/level ingredient
    for ingredient in ingredients:
        if len(ingredient['owned']) > 0:
            base_monster = ingredient['owned'][0].monster
        else:
            base_monster = ingredient['instance'].awakens_from

        # If the best ingredient monster is not awakened, subtract it's awakening cost
        if not base_monster.is_awakened:
            if base_monster.awaken_magic_mats_low is not None:
                essences_missing_max_leveled['magic']['low'] -= base_monster.awaken_magic_mats_low

            if base_monster.awaken_magic_mats_mid is not None:
                essences_missing_max_leveled['magic']['mid'] -= base_monster.awaken_magic_mats_mid

            if base_monster.awaken_magic_mats_high is not None:
                essences_missing_max_leveled['magic']['high'] -= base_monster.awaken_magic_mats_high

            if base_monster.awaken_ele_mats_low is not None:
                essences_missing_max_leveled[str(base_monster.element)]['low'] -= base_monster.awaken_ele_mats_low

            if base_monster.awaken_ele_mats_mid is not None:
                essences_missing_max_leveled[str(base_monster.element)]['mid'] -= base_monster.awaken_ele_mats_mid

            if base_monster.awaken_ele_mats_high is not None:
                essences_missing_max_leveled[str(base_monster.element)]['high'] -= base_monster.awaken_ele_mats_high

    # Method 2: Assume user wants to level an already awakened ingredient
    for ingredient in ingredients:
        awakened_ingredient_owned = False
        base_monster = ingredient['instance'].awakens_from

        # Check if ANY of the owned ingredients is awakened
        if len(ingredient['owned']) > 0:
            for owned_ingredient in ingredient['owned']:
                if owned_ingredient.monster.is_awakened:
                    awakened_ingredient_owned = True

        # If none are, subtract the essences from the available essences
        if not awakened_ingredient_owned:
            if base_monster.awaken_magic_mats_low is not None:
                essences_missing_use_awakened['magic']['low'] -= base_monster.awaken_magic_mats_low

            if base_monster.awaken_magic_mats_mid is not None:
                essences_missing_use_awakened['magic']['mid'] -= base_monster.awaken_magic_mats_mid

            if base_monster.awaken_magic_mats_high is not None:
                essences_missing_use_awakened['magic']['high'] -= base_monster.awaken_magic_mats_high

            if base_monster.awaken_ele_mats_low is not None:
                essences_missing_use_awakened[str(base_monster.element)]['low'] -= base_monster.awaken_ele_mats_low

            if base_monster.awaken_ele_mats_mid is not None:
                essences_missing_use_awakened[str(base_monster.element)]['mid'] -= base_monster.awaken_ele_mats_mid

            if base_monster.awaken_ele_mats_high is not None:
                essences_missing_use_awakened[str(base_monster.element)]['high'] -= base_monster.awaken_ele_mats_high

    return {
        'max_leveled': essences_missing_max_leveled,
        'use_awakened': essences_missing_use_awakened,
    }