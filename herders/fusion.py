from copy import deepcopy
from collections import OrderedDict


def essences_missing(summoner_storage, ingredients):
    # Calculate how many essences are missing to awaken all ingredients
    total_awakening_cost = OrderedDict({
        'magic': {},
        'fire': {},
        'water': {},
        'wind': {},
        'dark': {},
        'light': {},
    })

    total_missing = deepcopy(total_awakening_cost)

    # Method 1: Assume user wants to awaken the highest star/level ingredient
    for ingredient in ingredients:
        if len(ingredient['owned']) > 0:
            base_monster = ingredient['owned'][0].monster
        else:
            base_monster = ingredient['instance'].awakens_from

        # If the best ingredient monster is not awakened, total up it's awakening cost
        if not base_monster.is_awakened:
            awakening_cost = base_monster.get_awakening_materials()

            for element, essences in awakening_cost.iteritems():
                for size in awakening_cost[element].keys():
                    total_awakening_cost[element][size] = total_awakening_cost[element].get(size, 0) + awakening_cost[element][size]

    for element in total_awakening_cost.keys():
        total_missing[element] = {key: summoner_storage[element][key] - total_awakening_cost[element][key] if summoner_storage[element][key] - total_awakening_cost[element][key] < 0 else 0 for key in total_awakening_cost[element].keys()}

    return total_missing
