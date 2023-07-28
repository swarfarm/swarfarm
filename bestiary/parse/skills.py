import json
import re
from numbers import Number

from sympy import simplify

from bestiary.models import Monster, Skill, SkillUpgrade, ScalingStat, HomunculusSkill, HomunculusSkillCraftCost, \
    GameItem
from bestiary.parse import game_data
from .util import update_bestiary_obj


def _get_skill_slot(master_id):
    # Search for skill usage on a monster and determine what index the skill occupies in the monster's skillset
    if master_id in game_data.tables.HOMUNCULUS_SKILL_TREES.keys():
        for skill_data in game_data.tables.HOMUNCULUS_SKILL_TREES.values():
            if master_id == skill_data['master id']:
                return skill_data['slot']
    else:
        for monster_data in game_data.tables.MONSTERS.values():
            if master_id in monster_data['base skill']:
                return monster_data['base skill'].index(master_id) + 1

    # Not found
    return -1


PLAIN_OPERATORS = '+-*/^'


def _force_eval_ltr(expr):
    # Convert Com2US' skill function data into more understandable mathematical expressions
    fixed = False
    if isinstance(expr, list):
        # Check if elements are strings or another array
        if expr and all(isinstance(elem, str) or isinstance(elem, Number) for elem in expr):
            expr_string = ''.join(map(str, expr))

            if 'FIXED' in expr_string:
                fixed = True
                expr_string = expr_string.replace('FIXED', '')

            if 'CEIL' in expr_string:
                expr_string = expr_string.replace('CEIL', '')

            # Hack for missing multiplication sign for ALIVE_RATE
            if 'ALIVE_RATE' in expr_string and not '*ALIVE_RATE' in expr_string:
                expr_string = expr_string.replace('ALIVE_RATE', '*ALIVE_RATE')

            # Remove any multiplications by 1 beforehand. It makes the simplifier function happier.
            expr_string = expr_string.replace('*1.0', '')

            if expr_string not in PLAIN_OPERATORS:
                all_operations = filter(None, re.split(r'([+\-*/^])', expr_string))
                operands = list(filter(None, re.split(r'[+\-*/^]', expr_string)))
                group_formula = '(' * len(operands)

                for operator in all_operations:
                    if operator in PLAIN_OPERATORS:
                        group_formula += operator
                    else:
                        group_formula += f'{operator})'
                return f'({group_formula})', fixed
            else:
                return f'{expr_string}', fixed
        else:
            # Process each sub-expression in LTR manner
            ltr_expr = ''
            for partial_expr in expr:
                partial_expr_ltr, fixed = _force_eval_ltr(partial_expr)
                if partial_expr_ltr not in PLAIN_OPERATORS:
                    ltr_expr = f'({ltr_expr}{partial_expr_ltr})'
                else:
                    ltr_expr += partial_expr_ltr

            return ltr_expr, fixed


def _simplify_multiplier(raw_multiplier):
    # Simplify the expression and change format to follow usual order of operations
    formula, fixed = _force_eval_ltr(raw_multiplier)
    if formula:
        formula = str(simplify(formula))

    if fixed:
        formula += ' (Fixed)'

    return formula


def _extract_scaling_stats(mult_formula):
    # Extract/refine the scaling stats used in the formula
    scaling_stats = []
    for stat in ScalingStat.objects.all():
        if re.search(f'{stat.com2us_desc}\\b', mult_formula):
            mult_formula = mult_formula.replace(stat.com2us_desc, f'{{{stat.stat}}}')
            scaling_stats.append(stat)

    return scaling_stats, mult_formula


def skills():
    for master_id, raw in game_data.tables.SKILLS.items():
        # Fix up raw data prior to parsing
        raw = preprocess_errata(master_id, raw)

        # Parse basic skill information from game data
        level_up_bonuses = []
        for upgrade_id, amount in raw['level']:
            upgrade = SkillUpgrade.COM2US_UPGRADE_MAP[upgrade_id]
            level_up_bonuses.append(SkillUpgrade.UPGRADE_CHOICES[upgrade][1].format(amount))
        level_up_text = '\n'.join(level_up_bonuses)

        multiplier_formula = _simplify_multiplier(raw['fun data'])
        scaling_stats, multiplier_formula = _extract_scaling_stats(multiplier_formula)

        defaults = {
            'name': game_data.strings.SKILL_NAMES.get(master_id, f'skill_{master_id}').strip(),
            'description': game_data.strings.SKILL_DESCRIPTIONS.get(master_id, raw['desc']).strip(),
            'slot': _get_skill_slot(master_id),
            'icon_filename': 'skill_icon_{0:04d}_{1}_{2}.png'.format(*raw['thumbnail']),
            'cooltime': raw['cool time'] if raw['cool time'] > 0 else None,
            'passive': bool(raw['passive']),
            'max_level': raw['max level'],
            'multiplier_formula_raw': json.dumps(raw['fun data']),
            'multiplier_formula': multiplier_formula,
            'level_progress_description': level_up_text,
        }

        skill = update_bestiary_obj(Skill, master_id, defaults)

        # Update skill level up progress
        SkillUpgrade.objects.filter(skill=skill, level__gt=skill.max_level).delete()
        for idx, (upgr_type, amount) in enumerate(raw['level']):
            SkillUpgrade.objects.update_or_create(
                skill=skill,
                level=idx + 2,  # upgrades start applying at skill lv.2
                defaults={
                    'effect': SkillUpgrade.COM2US_UPGRADE_MAP[upgr_type],
                    'amount': amount,
                }
            )

        # Update scaling stats
        skill.scaling_stats.set(scaling_stats)

        # Post-process skill object with any known issues
        postprocess_errata(master_id, skill, raw)


# Skill erratum
def replace_golem_multiplier(raw):
    raw['fun data'] = [["ATK", "*", 1.8], ["+"], ["DEF", "*", 2.5]]
    return raw


def replace_attack_def_with_just_def(raw):
    raw['fun data'] = [[el.replace('ATTACK_DEF', 'DEF') if isinstance(el, str) else el for el in row] for row in raw['fun data']]
    return raw


def fix_noble_agreement_multiplier(raw):
    raw['fun data'] = [["ATK", "*", 1.0], ["*"], ["ATTACK_SPEED", "+", 240], ["/"], [60]]
    return raw


def fix_holy_light_multiplier(raw):
    raw['fun data'] = [["TARGET_CUR_HP", "*", 0.15]]
    return raw


def add_scales_with_def(obj, raw):
    obj.scaling_stats.add(ScalingStat.objects.get(com2us_desc='DEF'))
    return obj


def add_scales_with_max_hp(obj, raw):
    obj.scaling_stats.add(ScalingStat.objects.get(com2us_desc='ATTACK_TOT_HP'))
    return obj


def add_scales_with_target_hp(obj, raw):
    obj.scaling_stats.add(ScalingStat.objects.get(com2us_desc='TARGET_TOT_HP'))
    return obj


def remove_multiplier(raw):
    raw['fun data'] = []
    return raw


_preprocess_erratum = {
    2401: [replace_golem_multiplier],  # Water Golem S1
    2402: [replace_golem_multiplier],  # Fire Golem S1
    2403: [replace_golem_multiplier],  # Wind Golem S1
    2404: [replace_golem_multiplier],  # Light Golem S1
    2405: [replace_golem_multiplier],  # Dark Golem S1
    2406: [replace_golem_multiplier],  # Water Golem S2
    2407: [replace_golem_multiplier],  # Fire Golem S2
    2410: [replace_golem_multiplier],  # Dark Golem S2
    2816: [remove_multiplier], # Water Sylphid S3
    2901: [replace_attack_def_with_just_def],  # Water Dragon S1
    2909: [fix_holy_light_multiplier],  # Light Dragon S2
    4214: [remove_multiplier], # Light Chimera S3
    4606: [remove_multiplier], # Water Howl (Unawakened) S2
    4607: [remove_multiplier], # Fire Howl (Unawakened) S2
    4608: [remove_multiplier], # Wind Howl (Unawakened) S2
    4609: [remove_multiplier], # Light Howl (Unawakened) S2
    4610: [remove_multiplier], # Dark Howl (Unawakened) S2
    4656: [remove_multiplier], # Water Howl (2A) S2
    4657: [remove_multiplier], # Fire Howl (2A) S2
    4658: [remove_multiplier], # Wind Howl (2A) S2
    4659: [remove_multiplier], # Light Howl (2A) S2
    4660: [remove_multiplier], # Dark Howl (2A) S2
    5609: [remove_multiplier], # Light Werewolf S2
    6313: [remove_multiplier], # Wind Archangel S3
    6519: [fix_noble_agreement_multiplier],  # Julianne S2
    8307: [remove_multiplier], # Fire Beast Monk S2
    8308: [remove_multiplier], # Wind Beast Monk S2
    8309: [remove_multiplier], # Light Beast Monk S2
    9015: [remove_multiplier], # Dark Hell Lady S3
    9108: [remove_multiplier], # Wind Sky Dancer S2
    9114: [remove_multiplier], # Light Sky Dancer S3
    9508: [remove_multiplier], # Wind Penguin Knight S2
    9510: [remove_multiplier], # Dark Penguin Knight S2
    9713: [remove_multiplier], # Wind Polar Queen S3
    9714: [remove_multiplier], # Light Polar Queen S3
    11011: [remove_multiplier], # Water Martial Artist S3
    12212: [remove_multiplier], # Fire Harp Magician S3
    12313: [remove_multiplier], # Wind Unicorn S3 (Passive)
    13115: [remove_multiplier], # Dark Lightning Emperor S3
}

_postprocess_erratum = {
    5663: [add_scales_with_max_hp],  # Shakan S3
    5665: [add_scales_with_max_hp],  # Jultan S3
    11012: [add_scales_with_def],  # Fire Martial Artist S3
    11214: [add_scales_with_max_hp],  # Light Anubis S3
    12614: [add_scales_with_target_hp],  # Light Chakram Dancer S3
}


def preprocess_errata(master_id, raw):
    if master_id in _preprocess_erratum:
        print(f'Preprocessing raw data for {master_id}.')
        for processing_func in _preprocess_erratum[master_id]:
            raw = processing_func(raw)
    return raw


def postprocess_errata(master_id, skill, raw):
    if master_id in _postprocess_erratum:
        print(f'Postprocessing erratum for {master_id}.')
        for processing_func in _postprocess_erratum[master_id]:
            skill = processing_func(skill, raw)
        skill.save()


def homonculus_skills():
    for master_id, raw in game_data.tables.HOMUNCULUS_SKILL_TREES.items():
        base_skill = Skill.objects.get(com2us_id=master_id)
        homu_skill, created = HomunculusSkill.objects.update_or_create(skill=base_skill)
        homu_skill.monsters.set(Monster.objects.filter(com2us_id__in=raw['unit master id']))
        homu_skill.prerequisites.set(Skill.objects.filter(com2us_id__in=raw['prerequisite']))

        # Upgrade cost items
        craft_cost_ids = []
        all_materials = [raw['upgrade cost']] + raw['upgrade stuff']
        for item_category, item_id, qty in all_materials:
            obj, _ = HomunculusSkillCraftCost.objects.update_or_create(
                skill=homu_skill,
                item=GameItem.objects.get(category=item_category, com2us_id=item_id),
                defaults={
                    'quantity': qty,
                }
            )
            craft_cost_ids.append(obj.pk)

        # Delete any no longer used
        HomunculusSkillCraftCost.objects.filter(skill=homu_skill).exclude(pk__in=craft_cost_ids).delete()
