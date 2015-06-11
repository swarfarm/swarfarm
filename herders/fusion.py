from django.db.models import Q

from .models import Monster, MonsterInstance


def fusion_progress(summoner, product_monster_id, stars, cost, ingredient_monster_ids):
    # Assumes: Product monster is unawakened. Ingredients are awakened.

    # Get instance of the fusion product
    product_instance = Monster.objects.get(pk=product_monster_id)

    # Indicate if already in summoner's collection
    fusion_complete = MonsterInstance.objects.filter(
        Q(owner=summoner), Q(monster__pk=product_instance.pk) | Q(monster__pk=product_instance.awakens_to().pk)
    ).count() > 0,

    level = 10 + stars * 5

    # Collect all the ingredients
    ingredients = []
    for ingredient_id in ingredient_monster_ids:
        ingredient_instance = Monster.objects.get(pk=ingredient_id)

        owned_ingredients = MonsterInstance.objects.filter(
            Q(owner=summoner),
            Q(monster__pk=ingredient_instance.pk) | Q(monster__pk=ingredient_instance.awakens_from.pk),
        ).order_by('-stars', '-level', '-monster__is_awakened')

        # Determine if each individual requirement is met using highest evolved/leveled monster
        if len(owned_ingredients) > 0:
            acquired = True
            evolved = owned_ingredients[0].stars >= stars
            leveled = owned_ingredients[0].level >= level
            awakened = owned_ingredients[0].monster.pk == ingredient_instance.pk
            complete = acquired & evolved & leveled & awakened
        else:
            acquired = False
            evolved = False
            leveled = False
            awakened = False
            complete = False

        ingredient = {
            'instance': ingredient_instance,
            'owned': owned_ingredients,
            'complete': complete,
            'acquired': acquired,
            'evolved': evolved,
            'leveled': leveled,
            'awakened': awakened,
        }
        ingredients.append(ingredient)

    return {
        'instance': product_instance,
        'acquired': fusion_complete,
        'stars': stars,
        'level': level,
        'cost': cost,
        'ingredients': ingredients,
        'ready': _all_ingredients_satisfied(ingredients)
    }


def _all_ingredients_satisfied(ingredients):
    for i in ingredients:
        if not i['complete']:
            return False
    return True
