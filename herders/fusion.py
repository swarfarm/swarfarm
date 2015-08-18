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
        'magic': {},
        'fire': {},
        'water': {},
        'wind': {},
        'dark': {},
        'light': {},
    })

    # Method 1: Assume user wants to awaken the highest star/level ingredient
    for ingredient in ingredients:
        base_monster = ingredient['instance'].awakens_from

        # Find first monster not ignored for fusion
        for owned in ingredient['owned']:
            if not owned.ignore_for_fusion:
                base_monster = owned.monster

        # If the best ingredient monster is not awakened, total up it's awakening cost
        if not base_monster.is_awakened:
            awakening_cost = base_monster.get_awakening_materials()

            for element, essences in awakening_cost.iteritems():
                for size in awakening_cost[element].keys():
                    total_cost[element][size] = total_cost[element].get(size, 0) + awakening_cost[element][size]

    return total_cost
