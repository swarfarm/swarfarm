from django.db.models import Q

from .models import Monster, MonsterInstance


def fusion_progress(summoner, product_monster_id, stars, cost, ingredient_monster_ids):
    # Assumes: Product monster is unawakened. Ingredients are awakened.

    # Get instance of the fusion product
    product_instance = Monster.objects.get(pk=product_monster_id)

    # Indicate if already in summoner's collection
    acquired = MonsterInstance.objects.filter(
        Q(owner=summoner), Q(monster__pk=product_instance.pk) | Q(monster__pk=product_instance.awakens_to().pk)
    ).count() > 0,

    # Collect all the ingredients
    ingredients = []
    for ingredient_id in ingredient_monster_ids:
        ingredient_instance = Monster.objects.get(pk=ingredient_id)

        owned_ingredients = MonsterInstance.objects.filter(
            Q(owner=summoner) & (
                Q(monster__pk=ingredient_instance.pk) | Q(monster__pk=ingredient_instance.awakens_from.pk)),
        ).order_by('-stars', '-level', '-monster__is_awakened')

        complete = MonsterInstance.objects.filter(
            owner=summoner, monster__pk=ingredient_instance.pk, stars=stars, level=10 + stars * 5
        ).count() > 0

        ingredient = {
            'instance': ingredient_instance,
            'owned': owned_ingredients,
            'complete': complete,
        }
        ingredients.append(ingredient)

    return {
        'instance': product_instance,
        'acquired': acquired,
        'stars': stars,
        'level': 10 + stars * 5,
        'cost': cost,
        'ingredients': ingredients,
        'ready': _all_ingredients_satisfied(ingredients)
    }


def _all_ingredients_satisfied(ingredients):
    for i in ingredients:
        if not i['complete']:
            return False
    return True
