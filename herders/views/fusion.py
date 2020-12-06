from copy import deepcopy

from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from bestiary.models import Fusion, ESSENCE_MAP, Monster
from herders.decorators import username_case_redirect
from herders.models import Summoner, MonsterInstance, MonsterPiece, MaterialStorage, MonsterShrineStorage


def fusion_progress(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    fusions = Fusion.objects.all()

    context = {
        'view': 'fusion',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'fusions': fusions,
    }

    return render(request, 'herders/profile/fusion/base.html', context)


@username_case_redirect
def fusion_progress_detail(request, profile_name, monster_slug):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    context = {
        'view': 'fusion',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        try:
            fusion = Fusion.objects.select_related(
                'product'
            ).prefetch_related(
                'ingredients'
            ).get(product__bestiary_slug=monster_slug)
        except Fusion.DoesNotExist:
            return HttpResponseBadRequest()
        else:
            level = 10 + fusion.product.base_stars * 5
            ingredients = []

            # Check if fusion has been completed already
            fusion_complete = MonsterInstance.objects.filter(
                Q(owner=summoner), Q(monster=fusion.product) | Q(monster=fusion.product.awakens_to)
            ).exists()

            # Scan summoner's collection for instances each ingredient
            fusion_ready = True

            for ingredient in fusion.ingredients.all().select_related('awakens_from', 'awakens_to'):
                owned_ingredients = MonsterInstance.objects.filter(
                    Q(owner=summoner),
                    Q(monster=ingredient) | Q(monster=ingredient.awakens_from),
                ).order_by('-stars', '-level', '-monster__is_awakened')

                owned_ingredient_pieces = MonsterPiece.objects.filter(
                    Q(owner=summoner),
                    Q(monster=ingredient) | Q(monster=ingredient.awakens_from),
                ).first()

                owned_shrines = MonsterShrineStorage.objects.select_related('item').filter(Q(owner=summoner),Q(item=ingredient) | Q(item=ingredient.awakens_from),)

                # Determine if each individual requirement is met using highest evolved/leveled monster that is not ignored for fusion
                for owned_ingredient in owned_ingredients:
                    if not owned_ingredient.ignore_for_fusion:
                        acquired = True
                        evolved = owned_ingredient.stars >= fusion.product.base_stars
                        leveled = owned_ingredient.level >= level
                        awakened = owned_ingredient.monster.is_awakened
                        complete = acquired & evolved & leveled & awakened
                        break
                else:
                    if owned_ingredient_pieces:
                        acquired = owned_ingredient_pieces.can_summon()
                    else:
                        acquired = False

                    evolved = False
                    leveled = False
                    awakened = False
                    complete = False
                
                for owned_shrine in owned_shrines:
                    # never evolved so never completed
                    acquired = True
                    if owned_shrine.item.awaken_level == Monster.AWAKEN_LEVEL_AWAKENED:
                        # the best possible outcome, awakened monster in Shrine - no point checking others
                        awakened = True
                        break

                if not complete:
                    fusion_ready = False

                # Check if this ingredient is fusable
                sub_fusion = None
                sub_fusion_awakening_cost = None
                try:
                    sub_fusion = Fusion.objects.get(product=ingredient.awakens_from)
                except Fusion.DoesNotExist:
                    pass
                else:
                    if not acquired:
                        awakened_sub_fusion_ingredients = MonsterInstance.objects.filter(
                            monster__pk__in=sub_fusion.ingredients.values_list('pk', flat=True),
                            ignore_for_fusion=False,
                            owner=summoner,
                        )
                        sub_fusion_awakening_cost = sub_fusion.total_awakening_cost(awakened_sub_fusion_ingredients)

                ingredient_progress = {
                    'instance': ingredient,
                    'owned': owned_ingredients,
                    'pieces': owned_ingredient_pieces,
                    'shrine': sum(o.quantity for o in owned_shrines),
                    'complete': complete,
                    'acquired': acquired,
                    'evolved': evolved,
                    'leveled': leveled,
                    'awakened': awakened,
                    'is_fuseable': True if sub_fusion else False,
                    'sub_fusion_cost': sub_fusion_awakening_cost,
                }
                ingredients.append(ingredient_progress)

            awakened_owned_ingredients = MonsterInstance.objects.filter(
                monster__pk__in=fusion.ingredients.values_list('pk', flat=True),
                ignore_for_fusion=False,
                owner=summoner,
            )
            total_cost = fusion.total_awakening_cost(awakened_owned_ingredients)

            # Calculate fulfilled/missing essences
            summoner_storage = {ms.item.com2us_id: ms for ms in MaterialStorage.objects.select_related('item').filter(owner=summoner)}
            essence_storage = {
                element: { 
                    size: summoner_storage[ESSENCE_MAP[element][size]].quantity
                    for size, _ in element_sizes.items()
                }
                for element, element_sizes in ESSENCE_MAP.items()
            }

            total_missing = {
                element: {
                    size: total_cost[element][size] - essence_storage[element][size] if total_cost[element][size] > essence_storage[element][size] else 0
                    for size, qty in element_sizes.items()
                }
                for element, element_sizes in total_cost.items()
            }

            # Check if there are any missing
            essences_satisfied = True
            for sizes in total_missing.values():
                for qty in sizes.values():
                    if qty > 0:
                        essences_satisfied = False

            # Determine the total/missing essences including sub-fusions
            if fusion.sub_fusion_available():
                total_sub_fusion_cost = deepcopy(total_cost)
                for ingredient in ingredients:
                    if ingredient['sub_fusion_cost']:
                        for element, sizes in total_sub_fusion_cost.items():
                            for size, qty in sizes.items():
                                total_sub_fusion_cost[element][size] += ingredient['sub_fusion_cost'][element][size]

                # Now determine what's missing based on owner's storage
                sub_fusion_total_missing = {
                    element: {
                            size: total_sub_fusion_cost[element][size] - essence_storage[element][size] if total_sub_fusion_cost[element][size] > essence_storage[element][size] else 0
                            for size, qty in element_sizes.items()
                        }
                    for element, element_sizes in total_sub_fusion_cost.items()
                    }

                sub_fusion_mats_satisfied = True
                for sizes in total_sub_fusion_cost.values():
                    for qty in sizes.values():
                        if qty > 0:
                            sub_fusion_mats_satisfied = False
            else:
                sub_fusion_total_missing = None
                sub_fusion_mats_satisfied = None

            progress = {
                'instance': fusion.product,
                'acquired': fusion_complete,
                'stars': fusion.product.base_stars,
                'level': level,
                'cost': fusion.cost,
                'ingredients': ingredients,
                'awakening_mats': essence_storage,
                'awakening_mats_cost': total_cost,
                'awakening_mats_sufficient': essences_satisfied,
                'awakening_mats_missing': total_missing,
                'sub_fusion_mats_missing': sub_fusion_total_missing,
                'sub_fusion_mats_sufficient': sub_fusion_mats_satisfied,
                'ready': fusion_ready,
            }

            context['fusion'] = progress

            return render(request, 'herders/profile/fusion/fusion_detail.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)

