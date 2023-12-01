import copy
import itertools
from numbers import Number
from operator import attrgetter

from django.utils.text import slugify
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Avg, Count, Max, Min, StdDev, Sum

from bestiary.models import Rune, RuneCraft, Artifact, Monster, Fusion

from herders.aggregations import Median, Perc25, Perc75
from herders.decorators import username_case_redirect
from herders.models import MonsterShrineStorage, RuneInstance, RuneCraftInstance, ArtifactInstance, ArtifactCraftInstance, Summoner, MonsterInstance
from herders.forms import CompareMonstersWithFollowerForm


def _get_efficiency_statistics(model, owner, field="efficiency", count=False, worth=False, worth_field='value'):
    eff_values = {}
    eff_map = {
        "efficiency__avg": "Efficiency (Average)",
        "efficiency__stddev": "Efficiency (Standard Deviation)",
        "efficiency__min": "Efficiency (Minimum)",
        "efficiency__perc25": "Efficiency (25th Percentile)",
        "efficiency__median": "Efficiency (Median)",
        "efficiency__perc75": "Efficiency (75th Percentile)",
        "efficiency__max": "Efficiency (Maximum)",
        "efficiency__count": "Count",
        "value__sum": "Worth",
    }
    aggregations = [
        Avg(field),
        StdDev(field),
        Min(field),
        Perc25(field),
        Median(field),
        Perc75(field),
        Max(field)
    ]
    if worth:
        aggregations.insert(0, Sum(worth_field))
    if count:
        aggregations.insert(0, Count(field))

    efficiencies = model.objects.filter(owner=owner).aggregate(*aggregations)
    for eff_key, eff_val in efficiencies.items():
        eff_values[eff_map[eff_key]] = round(eff_val or 0, 2)

    return eff_values


def _find_comparison_winner(data):
    for key, val in data.items():
        if isinstance(val, dict) and "summoner" not in val.keys():
            _find_comparison_winner(val)
        elif isinstance(val, dict):
            record = data[key]
            diff = round(record["summoner"] - record["follower"], 2)
            record["diff"] = diff
            if diff > 0:
                record["winner"] = "summoner"
                record["diff"] = "> " + str(abs(diff))
            elif diff < 0:
                record["winner"] = "follower"
                record["diff"] = "< " + str(abs(diff))
            else:
                record["winner"] = "tie"
        else:
            raise ValueError(
                "Dictionary depth doesn't end with `summoner`, `follower` dictionary.")


def _compare_summary(summoner, follower):
    report = {
        "runes": {},
        "artifacts": {},
        "monsters": {
            'Count': {
                "summoner": MonsterInstance.objects.filter(owner=summoner).count() + (MonsterShrineStorage.objects.filter(owner=summoner).aggregate(count=Sum('quantity'))['count'] or 0),
                "follower": MonsterInstance.objects.filter(owner=follower).count() + (MonsterShrineStorage.objects.filter(owner=follower).aggregate(count=Sum('quantity'))['count'] or 0),
            },
            'Nat 5⭐': {
                "summoner": MonsterInstance.objects.filter(owner=summoner, monster__natural_stars=5).count(),
                "follower": MonsterInstance.objects.filter(owner=follower, monster__natural_stars=5).count(),
            },
            'Nat 4⭐': {
                "summoner": MonsterInstance.objects.filter(owner=summoner, monster__natural_stars=4).count(),
                "follower": MonsterInstance.objects.filter(owner=follower, monster__natural_stars=4).count(),
            },
        },
    }
    runes_summoner_eff = _get_efficiency_statistics(
        RuneInstance, summoner, count=True, worth=True)
    runes_follower_eff = _get_efficiency_statistics(
        RuneInstance, follower, count=True, worth=True)
    for key in runes_summoner_eff.keys():
        report["runes"][key] = {
            "summoner": runes_summoner_eff[key],
            "follower": runes_follower_eff[key],
        }

    artifacts_summoner_eff = _get_efficiency_statistics(
        ArtifactInstance, summoner, count=True)
    artifacts_follower_eff = _get_efficiency_statistics(
        ArtifactInstance, follower, count=True)
    for key in artifacts_summoner_eff.keys():
        report["artifacts"][key] = {
            "summoner": artifacts_summoner_eff[key],
            "follower": artifacts_follower_eff[key],
        }

    owners = [summoner, follower]
    monsters_shrine = MonsterShrineStorage.objects.select_related('owner', 'item').filter(
        owner__in=owners, item__natural_stars__gte=4).order_by('owner')
    for owner, iter_ in itertools.groupby(monsters_shrine, key=attrgetter('owner')):
        owner_str = "summoner"
        if owner == follower:
            owner_str = "follower"
        monsters_owner = list(iter_)
        for monster in monsters_owner:
            report['monsters'][f'Nat {monster.item.natural_stars}⭐'][owner_str] += monster.quantity or 0

    _find_comparison_winner(report)

    return report


@username_case_redirect
@login_required
def summary(request, profile_name, follow_username):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    try:
        follower = Summoner.objects.select_related(
            'user').get(user__username=follow_username)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    can_compare = (follower in summoner.following.all(
    ) and follower in summoner.followed_by.all() and follower.public)

    context = {
        'is_owner': is_owner,
        'can_compare': can_compare,
        'profile_name': profile_name,
        'follower_name': follow_username,
        'comparison': _compare_summary(summoner, follower),
        'view': 'compare-summary',
    }

    return render(request, 'herders/profile/compare/summary.html', context)


def _compare_runes(summoner, follower):
    stats = {stat[1]: {"summoner": 0, "follower": 0}
             for stat in sorted(Rune.STAT_CHOICES, key=lambda x: x[1])}
    qualities = {quality[1]: {"summoner": 0, "follower": 0}
                 for quality in Rune.QUALITY_CHOICES}
    qualities[None] = {"summoner": 0, "follower": 0}
    report_runes = {
        'summary': {
            'Count': {"summoner": 0, "follower": 0},
            'Worth': {"summoner": 0, "follower": 0},
        },
        'stars': {
            6: {"summoner": 0, "follower": 0},
            5: {"summoner": 0, "follower": 0},
            4: {"summoner": 0, "follower": 0},
            3: {"summoner": 0, "follower": 0},
            2: {"summoner": 0, "follower": 0},
            1: {"summoner": 0, "follower": 0},
        },
        'sets': {rune_set[1]: {"summoner": 0, "follower": 0} for rune_set in sorted(Rune.TYPE_CHOICES, key=lambda x: x[1])},
        'quality': copy.deepcopy(qualities),
        'quality_original': copy.deepcopy(qualities),
        'slot': {
            1: {"summoner": 0, "follower": 0},
            2: {"summoner": 0, "follower": 0},
            3: {"summoner": 0, "follower": 0},
            4: {"summoner": 0, "follower": 0},
            5: {"summoner": 0, "follower": 0},
            6: {"summoner": 0, "follower": 0},
        },
        'main_stat': copy.deepcopy(stats),
        'innate_stat': copy.deepcopy(stats),
        'substats': copy.deepcopy(stats),
    }
    report_runes['innate_stat'][None] = {"summoner": 0, "follower": 0}
    owners = [summoner, follower]
    runes = RuneInstance.objects.select_related(
        'owner').filter(owner__in=owners).order_by('owner')

    rune_substats = dict(Rune.STAT_CHOICES)

    for owner, iter_ in itertools.groupby(runes, key=attrgetter('owner')):
        owner_str = "summoner"
        if owner == follower:
            owner_str = "follower"
        runes_owner = list(iter_)
        report_runes['summary']['Count'][owner_str] = len(runes_owner)
        for rune in runes_owner:
            for sub_stat in rune.substats:
                report_runes['substats'][rune_substats[sub_stat]
                                         ][owner_str] += 1

            report_runes['stars'][rune.stars][owner_str] += 1
            report_runes['sets'][rune.get_type_display()][owner_str] += 1
            report_runes['quality'][rune.get_quality_display()][owner_str] += 1
            report_runes['quality_original'][rune.get_original_quality_display(
            )][owner_str] += 1
            report_runes['slot'][rune.slot][owner_str] += 1
            report_runes['main_stat'][rune.get_main_stat_display()
                                      ][owner_str] += 1
            report_runes['innate_stat'][rune.get_innate_stat_display()
                                        ][owner_str] += 1
            report_runes['summary']['Worth'][owner_str] += rune.value or 0

    summoner_eff = _get_efficiency_statistics(RuneInstance, summoner)
    follower_eff = _get_efficiency_statistics(RuneInstance, follower)
    for key in summoner_eff.keys():
        report_runes["summary"][key] = {
            "summoner": summoner_eff[key],
            "follower": follower_eff[key],
        }

    _find_comparison_winner(report_runes)

    return report_runes


@username_case_redirect
@login_required
def runes(request, profile_name, follow_username):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    try:
        follower = Summoner.objects.select_related(
            'user').get(user__username=follow_username)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    can_compare = (follower in summoner.following.all(
    ) and follower in summoner.followed_by.all() and follower.public)

    context = {
        'is_owner': is_owner,
        'can_compare': can_compare,
        'profile_name': profile_name,
        'follower_name': follow_username,
        'runes': _compare_runes(summoner, follower),
        'view': 'compare-runes',
        'subviews': {type_[1]: slugify(type_[1]) for type_ in RuneCraft.CRAFT_CHOICES}
    }

    return render(request, 'herders/profile/compare/runes/base.html', context)


def _compare_rune_crafts(summoner, follower, craft_type):
    if craft_type in RuneCraft.CRAFT_GRINDSTONES:
        stats = {stat[1]: {"summoner": 0, "follower": 0} for stat in sorted(
            RuneCraft.STAT_CHOICES, key=lambda x: x[1]) if stat[0] in RuneCraft.STAT_GRINDABLE}
    else:
        stats = {stat[1]: {"summoner": 0, "follower": 0} for stat in sorted(
            RuneCraft.STAT_CHOICES, key=lambda x: x[1])}
    sets = {rune_set[1]: {"summoner": 0, "follower": 0}
            for rune_set in sorted(RuneCraft.TYPE_CHOICES, key=lambda x: x[1])}
    sets[None] = {"summoner": 0, "follower": 0}
    qualities = {quality[1]: {"summoner": 0, "follower": 0}
                 for quality in RuneCraft.QUALITY_CHOICES}
    report = {
        'sets': copy.deepcopy(sets),
        'quality': copy.deepcopy(qualities),
        'stat': copy.deepcopy(stats),
        'summary': {
            'Count': {"summoner": 0, "follower": 0},
            'Worth': {"summoner": 0, "follower": 0},
        },
    }
    owners = [summoner, follower]
    runes = RuneCraftInstance.objects.select_related('owner').filter(
        owner__in=owners, type=craft_type).order_by('owner')

    for owner, iter_ in itertools.groupby(runes, key=attrgetter('owner')):
        owner_str = "summoner"
        if owner == follower:
            owner_str = "follower"
        records_owner = list(iter_)
        for record in records_owner:
            report['summary']['Count'][owner_str] += record.quantity or 0
            report['sets'][record.get_rune_display(
            )][owner_str] += record.quantity or 0
            report['quality'][record.get_quality_display(
            )][owner_str] += record.quantity or 0
            report['stat'][record.get_stat_display(
            )][owner_str] += record.quantity or 0
            if record.value:
                report['summary']['Worth'][owner_str] += record.value * \
                    record.quantity or 0

    _find_comparison_winner(report)

    return report


@username_case_redirect
@login_required
def rune_crafts(request, profile_name, follow_username, rune_craft_slug):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    try:
        follower = Summoner.objects.select_related(
            'user').get(user__username=follow_username)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    can_compare = (follower in summoner.following.all(
    ) and follower in summoner.followed_by.all() and follower.public)

    craft_types = {slugify(type_[1]): {"idx": type_[0], "name": type_[
        1]} for type_ in RuneCraft.CRAFT_CHOICES}
    craft_type = craft_types.get(rune_craft_slug, None)
    if craft_type is None:
        return HttpResponseBadRequest()

    context = {
        'is_owner': is_owner,
        'can_compare': can_compare,
        'profile_name': profile_name,
        'follower_name': follow_username,
        'crafts': _compare_rune_crafts(summoner, follower, craft_type["idx"]),
        'view': 'compare-runes',
        'craft_type': craft_type["name"],
        'subviews': {type_[1]: slugify(type_[1]) for type_ in RuneCraft.CRAFT_CHOICES}
    }

    return render(request, 'herders/profile/compare/runes/crafts.html', context)


def _compare_artifacts(summoner, follower):
    qualities = {quality[1]: {"summoner": 0, "follower": 0}
                 for quality in Artifact.QUALITY_CHOICES}
    report = {
        'summary': {
            'Count': {"summoner": 0, "follower": 0},
        },
        'quality': copy.deepcopy(qualities),
        'quality_original': copy.deepcopy(qualities),
        'slot': {artifact_slot[1]: {"summoner": 0, "follower": 0} for artifact_slot in (Artifact.ARCHETYPE_CHOICES + Artifact.NORMAL_ELEMENT_CHOICES)},
        'main_stat': {stat[1]: {"summoner": 0, "follower": 0} for stat in sorted(Artifact.MAIN_STAT_CHOICES, key=lambda x: x[1])},
        'substats': {effect[1]: {"summoner": 0, "follower": 0} for effect in sorted(Artifact.EFFECT_CHOICES, key=lambda x: x[1])},
    }
    owners = [summoner, follower]
    artifacts = ArtifactInstance.objects.select_related(
        'owner').filter(owner__in=owners).order_by('owner')

    artifact_substats = dict(Artifact.EFFECT_CHOICES)

    for owner, iter_ in itertools.groupby(artifacts, key=attrgetter('owner')):
        owner_str = "summoner"
        if owner == follower:
            owner_str = "follower"
        artifacts_owner = list(iter_)
        report['summary']['Count'][owner_str] = len(artifacts_owner)
        for artifact in artifacts_owner:
            for sub_stat in artifact.effects:
                report['substats'][artifact_substats[sub_stat]][owner_str] += 1

            report['quality'][artifact.get_quality_display()][owner_str] += 1
            report['quality_original'][artifact.get_original_quality_display()
                                       ][owner_str] += 1
            report['slot'][artifact.get_precise_slot_display()][owner_str] += 1
            report['main_stat'][artifact.get_main_stat_display()][owner_str] += 1

    summoner_eff = _get_efficiency_statistics(ArtifactInstance, summoner)
    follower_eff = _get_efficiency_statistics(ArtifactInstance, follower)
    for key in summoner_eff.keys():
        report["summary"][key] = {
            "summoner": summoner_eff[key],
            "follower": follower_eff[key],
        }

    _find_comparison_winner(report)

    return report


@username_case_redirect
@login_required
def artifacts(request, profile_name, follow_username):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    try:
        follower = Summoner.objects.select_related(
            'user').get(user__username=follow_username)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    can_compare = (follower in summoner.following.all(
    ) and follower in summoner.followed_by.all() and follower.public)

    context = {
        'is_owner': is_owner,
        'can_compare': can_compare,
        'profile_name': profile_name,
        'follower_name': follow_username,
        'artifacts': _compare_artifacts(summoner, follower),
        'view': 'compare-artifacts',
    }

    return render(request, 'herders/profile/compare/artifacts/base.html', context)


def _compare_artifact_crafts(summoner, follower):
    report = {
        'summary': {
            'Count': {"summoner": 0, "follower": 0},
        },
        'quality': {quality[1]: {"summoner": 0, "follower": 0} for quality in Artifact.QUALITY_CHOICES},
        'slot': {artifact_slot[1]: {"summoner": 0, "follower": 0} for artifact_slot in (Artifact.ARCHETYPE_CHOICES + Artifact.NORMAL_ELEMENT_CHOICES)},
        'substats': {effect[1]: {"summoner": 0, "follower": 0} for effect in sorted(Artifact.EFFECT_CHOICES, key=lambda x: x[1])},
    }
    owners = [summoner, follower]
    artifacts = ArtifactCraftInstance.objects.select_related(
        'owner').filter(owner__in=owners).order_by('owner')

    for owner, iter_ in itertools.groupby(artifacts, key=attrgetter('owner')):
        owner_str = "summoner"
        if owner == follower:
            owner_str = "follower"
        artifacts_owner = list(iter_)
        for artifact in artifacts_owner:
            report['substats'][artifact.get_effect_display(
            )][owner_str] += artifact.quantity or 0
            report['quality'][artifact.get_quality_display(
            )][owner_str] += artifact.quantity or 0
            report['slot'][artifact.get_archetype_display(
            ) or artifact.get_element_display()][owner_str] += artifact.quantity or 0
            report['summary']['Count'][owner_str] += artifact.quantity or 0

    _find_comparison_winner(report)

    return report


@username_case_redirect
@login_required
def artifact_crafts(request, profile_name, follow_username):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    try:
        follower = Summoner.objects.select_related(
            'user').get(user__username=follow_username)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    can_compare = (follower in summoner.following.all(
    ) and follower in summoner.followed_by.all() and follower.public)

    context = {
        'is_owner': is_owner,
        'can_compare': can_compare,
        'profile_name': profile_name,
        'follower_name': follow_username,
        'artifact_craft': _compare_artifact_crafts(summoner, follower),
        'view': 'compare-artifacts',
    }

    return render(request, 'herders/profile/compare/artifacts/crafts.html', context)


def _compare_monsters(summoner, follower):
    owners = [summoner, follower]
    report = {
        'summary': {
            'Count': {"summoner": 0, "follower": 0},
            'In Storage': {"summoner": 0, "follower": 0},
            'Outside Storage': {"summoner": 0, "follower": 0},
            'Max Skillups': {"summoner": 0, "follower": 0},
            'Fusion Food': {"summoner": 0, "follower": 0},
            'In Monster Shrine Storage': {"summoner": 0, "follower": 0},
        },
        'stars': {
            1: {"summoner": 0, "follower": 0},
            2: {"summoner": 0, "follower": 0},
            3: {"summoner": 0, "follower": 0},
            4: {"summoner": 0, "follower": 0},
            5: {"summoner": 0, "follower": 0},
            6: {"summoner": 0, "follower": 0},
        },
        'natural_stars': {
            i: {
                "fusion": {
                    "elemental": {"summoner": 0, "follower": 0},
                    "ld": {"summoner": 0, "follower": 0},
                },
                "nonfusion": {
                    "elemental": {"summoner": 0, "follower": 0},
                    "ld": {"summoner": 0, "follower": 0},
                },
            } for i in range(1, 6)},
        'elements': {element[1]: {"summoner": 0, "follower": 0} for element in Monster.NORMAL_ELEMENT_CHOICES},
        'archetypes': {archetype[1]: {"summoner": 0, "follower": 0} for archetype in Monster.ARCHETYPE_CHOICES},
    }
    monsters = MonsterInstance.objects.select_related('owner', 'monster', 'monster__awakens_to', 'monster__awakens_from', 'monster__awakens_from__awakens_from',
                                                      'monster__awakens_to__awakens_to').prefetch_related('monster__skills').filter(owner__in=owners).order_by('owner')
    monsters_fusion = [
        f'{mon.product.family_id}-{mon.product.element}' for mon in Fusion.objects.select_related('product').only('product')]
    free_nat5_families = [19200, 23000, 24100, 24600, 1000100, 1000200]

    for owner, iter_ in itertools.groupby(monsters, key=attrgetter('owner')):
        owner_str = "summoner"
        if owner == follower:
            owner_str = "follower"
        monsters_owner = list(iter_)
        report['summary']['Count'][owner_str] = len(monsters_owner)
        for monster in monsters_owner:
            if monster.monster.archetype == Monster.ARCHETYPE_MATERIAL:
                report['summary']['Count'][owner_str] -= 1
                continue

            if monster.in_storage:
                report['summary']['In Storage'][owner_str] += 1
            else:
                report['summary']['Outside Storage'][owner_str] += 1
            if monster.skill_ups_to_max() == 0:
                report['summary']['Max Skillups'][owner_str] += 1
            report['stars'][monster.stars][owner_str] += 1

            mon_el = "elemental" if monster.monster.element in [
                Monster.ELEMENT_WATER, Monster.ELEMENT_FIRE, Monster.ELEMENT_WIND] else "ld"
            if f'{monster.monster.family_id}-{monster.monster.element}' in monsters_fusion or monster.monster.family_id in free_nat5_families:
                report['natural_stars'][monster.monster.natural_stars]['fusion'][mon_el][owner_str] += 1
            else:
                report['natural_stars'][monster.monster.natural_stars]['nonfusion'][mon_el][owner_str] += 1

            report['elements'][monster.monster.get_element_display()
                               ][owner_str] += 1
            report['archetypes'][monster.monster.get_archetype_display()
                                 ][owner_str] += 1

            if monster.monster.fusion_food:
                report['summary']['Fusion Food'][owner_str] += 1

    monsters_shrine = MonsterShrineStorage.objects.select_related(
        'owner', 'item').filter(owner__in=owners).order_by('owner')

    for owner, iter_ in itertools.groupby(monsters_shrine, key=attrgetter('owner')):
        owner_str = "summoner"
        if owner == follower:
            owner_str = "follower"
        monsters_owner = list(iter_)
        for monster in monsters_owner:
            if monster.item.archetype == Monster.ARCHETYPE_MATERIAL:
                continue

            report['summary']['Count'][owner_str] += monster.quantity
            report['summary']['In Monster Shrine Storage'][owner_str] += monster.quantity or 0
            report['stars'][monster.item.natural_stars][owner_str] += monster.quantity or 0

            mon_el = "elemental" if monster.item.element in [
                Monster.ELEMENT_WATER, Monster.ELEMENT_FIRE, Monster.ELEMENT_WIND] else "ld"
            if f'{monster.item.family_id}-{monster.item.element}' in monsters_fusion or monster.item.family_id in free_nat5_families:
                report['natural_stars'][monster.item.natural_stars]['fusion'][mon_el][owner_str] += monster.quantity
            else:
                report['natural_stars'][monster.item.natural_stars]['nonfusion'][mon_el][owner_str] += monster.quantity

            report['elements'][monster.item.get_element_display(
            )][owner_str] += monster.quantity or 0
            report['archetypes'][monster.item.get_archetype_display()
                                 ][owner_str] += monster.quantity or 0

    _find_comparison_winner(report)

    return report


@username_case_redirect
@login_required
def monsters(request, profile_name, follow_username):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    try:
        follower = Summoner.objects.select_related(
            'user').get(user__username=follow_username)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    can_compare = (follower in summoner.following.all(
    ) and follower in summoner.followed_by.all() and follower.public)

    context = {
        'is_owner': is_owner,
        'can_compare': can_compare,
        'profile_name': profile_name,
        'follower_name': follow_username,
        'monsters': _compare_monsters(summoner, follower),
        'view': 'compare-monsters',
    }

    return render(request, 'herders/profile/compare/monsters/base.html', context)


def _compare_monster_objects(mon_s, mon_f):
    comparison = {
        "Level": {"summoner": mon_s.level, "follower": mon_f.level},
        "Stars": {"summoner": mon_s.stars, "follower": mon_f.stars},
        "HP": {"summoner": mon_s.hp(), "follower": mon_f.hp()},
        "Attack": {"summoner": mon_s.attack(), "follower": mon_f.attack()},
        "Defense": {"summoner": mon_s.defense(), "follower": mon_f.defense()},
        "Speed": {"summoner": mon_s.speed(), "follower": mon_f.speed()},
        "Critical Rate": {"summoner": mon_s.crit_rate(), "follower": mon_f.crit_rate()},
        "Critical Damage": {"summoner": mon_s.crit_damage(), "follower": mon_f.crit_damage()},
        "Resistance": {"summoner": mon_s.resistance(), "follower": mon_f.resistance()},
        "Accuracy": {"summoner": mon_s.accuracy(), "follower": mon_f.accuracy()},
        "Effective HP": {"summoner": mon_s.effective_hp(), "follower": mon_f.effective_hp()},
        "Skillups To Max": {"summoner": mon_s.skill_ups_to_max(), "follower": mon_f.skill_ups_to_max()},
    }

    _find_comparison_winner(comparison)
    # reverse comparison
    if comparison["Skillups To Max"]["winner"] == "summoner":
        comparison["Skillups To Max"]["winner"] == "follower"
    elif comparison["Skillups To Max"]["winner"] == "follower":
        comparison["Skillups To Max"]["winner"] = "summoner"

    return comparison


def _compare_monster_rune_sets(s_build, f_build):
    sets = {"summoner": s_build.active_rune_sets,
            "follower": f_build.active_rune_sets}
    sets_without_stat_increase = {"summoner": [], "follower": []}

    for owner, sets_ in sets.items():
        for set_ in sets_:
            stat = RuneInstance.RUNE_SET_BONUSES[set_]['stat']
            if not stat:
                sets_without_stat_increase[owner].append(set_)

    final_sets = {"summoner": [], "follower": [], "diff": []}

    for set_ in sets_without_stat_increase["summoner"]:
        final_sets["summoner"].append(RuneInstance.TYPE_CHOICES[set_ - 1][1])
        if set_ not in sets_without_stat_increase["follower"]:
            final_sets["diff"].append({
                "text": "+ " + final_sets["summoner"][-1],
                "winner": "summoner"
            })

    for set_ in sets_without_stat_increase["follower"]:
        final_sets["follower"].append(RuneInstance.TYPE_CHOICES[set_ - 1][1])
        if set_ not in sets_without_stat_increase["summoner"]:
            final_sets["diff"].append({
                "text": "- " + final_sets["follower"][-1],
                "winner": "follower"
            })

    final_sets["summoner"] = "/".join(final_sets["summoner"])
    final_sets["follower"] = "/".join(final_sets["follower"])

    return final_sets


def _compare_build_objects(mon_s, mon_f, rta=False):
    if rta:
        mon_s_build = mon_s.rta_build
        mon_f_build = mon_f.rta_build
    else:
        mon_s_build = mon_s.default_build
        mon_f_build = mon_f.default_build

    comparison = {
        "HP": {"summoner": mon_s_build.hp, "follower": mon_f_build.hp},
        "HP %": {"summoner": mon_s_build.hp_pct, "follower": mon_f_build.hp_pct},
        "Attack": {"summoner": mon_s_build.attack, "follower": mon_f_build.attack},
        "Attack %": {"summoner": mon_s_build.attack_pct, "follower": mon_f_build.attack_pct},
        "Defense": {"summoner": mon_s_build.defense, "follower": mon_f_build.defense},
        "Defense %": {"summoner": mon_s_build.defense_pct, "follower": mon_f_build.defense_pct},
        "Speed": {"summoner": mon_s_build.speed, "follower": mon_f_build.speed},
        "Speed %": {"summoner": mon_s_build.speed_pct, "follower": mon_f_build.speed_pct},
        "Critical Rate": {"summoner": mon_s_build.crit_rate, "follower": mon_f_build.crit_rate},
        "Critical Damage": {"summoner": mon_s_build.crit_damage, "follower": mon_f_build.crit_damage},
        "Resistance": {"summoner": mon_s_build.resistance, "follower": mon_f_build.resistance},
        "Accuracy": {"summoner": mon_s_build.accuracy, "follower": mon_f_build.accuracy},
    }

    _find_comparison_winner(comparison)

    comparison["Rune sets"] = _compare_monster_rune_sets(
        mon_s_build, mon_f_build)
    for slot in [2, 4, 6]:
        s_rune = mon_s_build.runes.filter(slot=slot).first()
        f_rune = mon_f_build.runes.filter(slot=slot).first()
        comparison[f"Slot {slot}"] = {
            "summoner": s_rune.get_main_stat_display() if s_rune else "",
            "follower": f_rune.get_main_stat_display() if f_rune else "",
        }

    return comparison


@username_case_redirect
@login_required
def builds(request, profile_name, follow_username):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    try:
        follower = Summoner.objects.select_related(
            'user').get(user__username=follow_username)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    can_compare = (follower in summoner.following.all(
    ) and follower in summoner.followed_by.all() and follower.public)

    if request.method == 'POST':
        form = CompareMonstersWithFollowerForm(
            request.POST, summoner_name=profile_name, follower_name=follow_username)

        if form.is_valid():
            context = {
                'is_owner': is_owner,
                'can_compare': can_compare,
                'profile_name': profile_name,
                'follower_name': follow_username,
                'form': form,
                "monsters": {"summoner": form.cleaned_data['summoner_monster'], "follower": form.cleaned_data['follower_monster']},
                'comparison': {
                    'builds': _compare_build_objects(form.cleaned_data['summoner_monster'], form.cleaned_data['follower_monster']),
                    'monsters': _compare_monster_objects(form.cleaned_data['summoner_monster'], form.cleaned_data['follower_monster']),
                    'rta_builds': _compare_build_objects(form.cleaned_data['summoner_monster'], form.cleaned_data['follower_monster'], rta=True),
                },
                'view': 'compare-builds',
            }
            return render(request, 'herders/profile/compare/builds/base.html', context)
        else:
            return HttpResponseBadRequest()
    else:
        context = {
            'is_owner': is_owner,
            'can_compare': can_compare,
            'profile_name': profile_name,
            'follower_name': follow_username,
            'form': CompareMonstersWithFollowerForm(summoner_name=profile_name, follower_name=follow_username),
            'view': 'compare-builds',
        }

        return render(request, 'herders/profile/compare/builds/base.html', context)
