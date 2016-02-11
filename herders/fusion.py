from copy import deepcopy
from collections import OrderedDict


def essences_missing(summoner_storage, total_cost):
    # Calculate how many essences are missing to awaken all ingredients
    total_missing = deepcopy(total_cost)

    for element in total_cost.keys():
        total_missing[element] = {key: summoner_storage[element][key] - total_cost[element].get(key, 0) if summoner_storage[element][key] - total_cost[element].get(key, 0) < 0 else 0 for key in summoner_storage[element].keys()}

    return total_missing


def total_awakening_cost(ingredients):
    total_cost = OrderedDict({
        'magic': OrderedDict(),
        'fire': OrderedDict(),
        'water': OrderedDict(),
        'wind': OrderedDict(),
        'dark': OrderedDict(),
        'light': OrderedDict(),
    })

    # Assume user wants to awaken the highest star/level ingredient
    for ingredient in ingredients:
        base_monster = ingredient['instance'].awakens_from

        # Find first monster not ignored for fusion
        for owned in ingredient['owned']:
            if not owned.ignore_for_fusion:
                base_monster = owned.monster
                break

        # If the best ingredient monster is not awakened, total up it's awakening cost
        if not base_monster.is_awakened:
            total_cost['magic']['low'] = total_cost['magic'].get('low', 0) + base_monster.awaken_mats_magic_low
            total_cost['magic']['mid'] = total_cost['magic'].get('mid', 0) + base_monster.awaken_mats_magic_mid
            total_cost['magic']['high'] = total_cost['magic'].get('high', 0) + base_monster.awaken_mats_magic_high
            total_cost['fire']['low'] = total_cost['fire'].get('low', 0) + base_monster.awaken_mats_fire_low
            total_cost['fire']['mid'] = total_cost['fire'].get('mid', 0) + base_monster.awaken_mats_fire_mid
            total_cost['fire']['high'] = total_cost['fire'].get('high', 0) + base_monster.awaken_mats_fire_high
            total_cost['water']['low'] = total_cost['water'].get('low', 0) + base_monster.awaken_mats_water_low
            total_cost['water']['mid'] = total_cost['water'].get('mid', 0) + base_monster.awaken_mats_water_mid
            total_cost['water']['high'] = total_cost['water'].get('high', 0) + base_monster.awaken_mats_water_high
            total_cost['wind']['low'] = total_cost['wind'].get('low', 0) + base_monster.awaken_mats_wind_low
            total_cost['wind']['mid'] = total_cost['wind'].get('mid', 0) + base_monster.awaken_mats_wind_mid
            total_cost['wind']['high'] = total_cost['wind'].get('high', 0) + base_monster.awaken_mats_wind_high
            total_cost['light']['low'] = total_cost['light'].get('low', 0) + base_monster.awaken_mats_light_low
            total_cost['light']['mid'] = total_cost['light'].get('mid', 0) + base_monster.awaken_mats_light_mid
            total_cost['light']['high'] = total_cost['light'].get('high', 0) + base_monster.awaken_mats_light_high
            total_cost['dark']['low'] = total_cost['dark'].get('low', 0) + base_monster.awaken_mats_dark_low
            total_cost['dark']['mid'] = total_cost['dark'].get('mid', 0) + base_monster.awaken_mats_dark_mid
            total_cost['dark']['high'] = total_cost['dark'].get('high', 0) + base_monster.awaken_mats_dark_high

    return total_cost
