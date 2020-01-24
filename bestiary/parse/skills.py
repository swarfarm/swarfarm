from numbers import Number
import json
from sympy import simplify
import re

from bestiary.models import Skill, SkillUpgrade, ScalingStat
from bestiary.parse import game_data


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


_all_scaling_stats = ScalingStat.objects.all()


def _extract_scaling_stats(mult_formula):
    # Extract/refine the scaling stats used in the formula
    scaling_stats = []
    for stat in _all_scaling_stats:
        if re.search(f'{stat.com2us_desc}\\b', mult_formula):
            mult_formula = mult_formula.replace(stat.com2us_desc, f'{{{stat.stat}}}')
            scaling_stats.append(stat)

    return scaling_stats, mult_formula


def skills():
    for master_id, raw in game_data.tables.SKILLS.items():
        # TODO: Implement overrides for known issues w/ skill data

        # Get skill object based on com2us_id
        skill, created = Skill.objects.get_or_create(
            com2us_id=master_id,
            defaults={
                'name': '',
                'description': '',
                'max_level': 0
            }
        )

        if created:
            print(f'!!! Created new skill {master_id}')

        # Parse basic skill information from game data
        level_up_text = ''
        for upgrade_id, amount in raw['level']:
            upgrade = SkillUpgrade.COM2US_UPGRADE_MAP[upgrade_id]
            level_up_text += SkillUpgrade.UPGRADE_CHOICES[upgrade][1].format(amount) + '\n'

        scaling_stats, multiplier_formula = _extract_scaling_stats(_simplify_multiplier(raw['fun data']))

        skill_values = {
            'name': game_data.strings.SKILL_NAMES.get(master_id, f'skill_{master_id}').strip(),
            'description': game_data.strings.SKILL_DESCRIPTIONS.get(master_id, raw['description']).strip(),
            'slot': _get_skill_slot(master_id),
            'icon_filename': 'skill_icon_{0:04d}_{1}_{2}.png'.format(*raw['thumbnail']),
            'cooltime': raw['cool time'] + 1 if raw['cool time'] > 0 else None,
            'passive': bool(raw['passive']),
            'max_level': raw['max level'],
            'multiplier_formula_raw': json.dumps(raw['fun data']),
            'multiplier_formula': multiplier_formula,
            'level_progress_description': level_up_text,
        }

        # Compare parsed values to existing values in skill object
        updated = False
        for field, value in skill_values.items():
            if getattr(skill, field) != value:
                print(f'Updating {field} for {master_id}.')
                setattr(skill, field, value)
                updated = True

        # Update skill instance
        if created or updated:
            skill.save()

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


def homonculus_skills():
    pass
