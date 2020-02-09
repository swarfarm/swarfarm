import base64
import binascii
import csv
import io
import json
import re
import zlib
from enum import IntEnum
from glob import iglob

from Crypto.Cipher import AES
from PIL import Image
from bitstring import Bits, BitStream, ConstBitStream, ReadError
from django.conf import settings
from sympy import simplify

from bestiary.com2us_mapping import *
from bestiary.parse.skills import _force_eval_ltr
from .models import Skill, ScalingStat, CraftMaterial, MonsterCraftCost, HomunculusSkill, \
    HomunculusSkillCraftCost, Dungeon, SecretDungeon, Level
from .models.monsters import AwakenBonusType


def _decrypt(msg):
    obj = AES.new(
        bytes(settings.SUMMONERS_WAR_SECRET_KEY, encoding='latin-1'),
        AES.MODE_CBC,
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    )
    decrypted = obj.decrypt(msg)
    return decrypted[:-decrypted[-1]]


def decrypt_request(msg):
    return _decrypt(base64.b64decode(msg))


def decrypt_response(msg):
    decoded = base64.b64decode(msg)
    decrypted = _decrypt(decoded)
    decompressed = zlib.decompress(decrypted)
    return decompressed


def update_all():
    decrypt_com2us_png()
    crop_monster_images()
    parse_skill_data()
    parse_monster_data()
    parse_monster_data()  # Runs twice to set awakens to/from relationships which is not possible until after both monsters are created
    parse_homunculus_data()


def _create_new_skill(com2us_id, slot):
    print('!!! Creating new skill with com2us ID {}, slot {}'.format(com2us_id, slot))
    return Skill.objects.create(com2us_id=com2us_id, name='tempname', slot=slot, max_level=1)


def parse_skill_data(preview=False):
    monster_table = _get_localvalue_tables(LocalvalueTables.MONSTERS)
    skill_table = _get_localvalue_tables(LocalvalueTables.SKILLS)
    skill_names = get_skill_names_by_id()
    skill_descriptions = get_skill_descs_by_id()
    homunculus_skill_table = _get_localvalue_tables(LocalvalueTables.HOMUNCULUS_SKILL_TREES)
    homunculus_skill_list = [json.loads(row['master id']) for row in homunculus_skill_table['rows']]

    scaling_stats = ScalingStat.objects.all()

    # Tracking IDs of skills with known issues/special cases
    golem_def_skills = [2401, 2402, 2403, 2404, 2405, 2406, 2407, 2410]
    noble_agreement_speed_id = 6519
    holy_light_id = 2909
    scale_with_max_hp_skills = [
        11214,  # Amarna S3
        5663,  # Shakan (2A) S3
        5665,  # Jultan (2A) S3
    ]
    sin_s3_scale_with_def = 11012
    deva_s3_scale_with_target_hp = 12614

    for skill_data in skill_table['rows']:
        # Get matching skill in DB
        master_id = json.loads(skill_data['master id'])

        # Skip it if no translation exists
        if master_id not in skill_names or master_id not in skill_descriptions:
            continue

        ###############################################################################################
        # KNOWN ISSUES W/ SOURCE DATA
        # skills with known issues are forcefully modified here. May need updating if skills are updated.
        ###############################################################################################
        if master_id in golem_def_skills:
            # Some golem skills use ATTACK_DEF scaling variable, which is the same as DEF that every other monster has
            skill_data['fun data'] = skill_data['fun data'].replace('ATTACK_DEF', 'DEF')

        if master_id == noble_agreement_speed_id:
            # Skill has different formula compared to other speed skills, so we're gonna set it here
            # It makes no difference to Com2US because they evaluate formulas right to left instead of using order of operations
            skill_data['fun data'] = '[["ATK", "*", 1.0], ["*"], ["ATTACK_SPEED", "+", 240], ["/"], [60]]'

        if master_id == holy_light_id:
            # This is a heal skill, but multiplier in game files is for an attack.
            # Setting multiplier formula based on skill description.
            skill_data['fun data'] = '[["TARGET_CUR_HP", "*", 0.15]]'

        updated = False
        try:
            skill = Skill.objects.get(com2us_id=master_id)
        except Skill.DoesNotExist:
            # Check if it is used on any monster. If so, create it
            # Homunculus skills beyond the starting set are not listed in the monster table
            skill = None
            if master_id in homunculus_skill_list:
                for homu_skill in homunculus_skill_table['rows']:
                    if master_id == json.loads(homu_skill['master id']):
                        slot = json.loads(homu_skill['slot'])
                        skill = _create_new_skill(master_id, slot)
                        break
            else:
                for monster in monster_table['rows']:
                    skill_array = json.loads(monster['base skill'])

                    if master_id in skill_array:
                        slot = skill_array.index(master_id) + 1
                        skill = _create_new_skill(master_id, slot)
                        break

            if skill is None:
                print('Skill ID {} is not used anywhere, skipping...'.format(master_id))
                continue
            else:
                updated = True

        # Name
        if skill.name != skill_names[master_id]:
            skill.name = skill_names[master_id]
            print('Updated name to {}'.format(skill.name))
            updated = True

        # Description
        if skill.description != skill_descriptions[master_id]:
            skill.description = skill_descriptions[master_id]
            print('Updated description to {}'.format(skill.description))
            updated = True

        # Icon
        icon_nums = json.loads(skill_data['thumbnail'])
        icon_filename = 'skill_icon_{0:04d}_{1}_{2}.png'.format(*icon_nums)
        if skill.icon_filename != icon_filename:
            skill.icon_filename = icon_filename
            print('Updated icon to {}'.format(skill.icon_filename))
            updated = True

        # Cooltime
        cooltime = json.loads(skill_data['cool time']) + 1 if json.loads(skill_data['cool time']) > 0 else None

        if skill.cooltime != cooltime:
            skill.cooltime = cooltime
            print('Updated cooltime to {}'.format(skill.cooltime))
            updated = True

        # Max Level
        max_lv = json.loads(skill_data['max level'])
        if skill.max_level != max_lv:
            skill.max_level = max_lv
            print('Updated max level to {}'.format(skill.max_level))
            updated = True

        # Level up progress
        level_up_desc = {
            'DR': 'Effect Rate +{0}%',
            'AT': 'Damage +{0}%',
            'AT1': 'Damage +{0}%',
            'HE': 'Recovery +{0}%',
            'TN': 'Cooltime Turn -{0}',
            'SD': 'Shield +{0}%',
            'SD1': 'Shield +{0}%',
            'GA': 'Attack Bar Recovery +{0}%',
            'DT': 'Harmful Effect Rate +{0} Turns',
        }

        level_up_text = ''

        for level in json.loads(skill_data['level']):
            level_up_text += level_up_desc[level[0]].format(level[1]) + '\n'

        if skill.level_progress_description != level_up_text:
            skill.level_progress_description = level_up_text
            print('Updated level-up progress description')
            updated = True

        # Buffs
        # maybe this later. Data seems incomplete sometimes.

        # Scaling formula and stats
        skill.scaling_stats.clear()

        # Skill multiplier formula
        if skill.multiplier_formula_raw != skill_data['fun data']:
            skill.multiplier_formula_raw = skill_data['fun data']
            print('Updated raw multiplier formula to {}'.format(skill.multiplier_formula_raw))
            updated = True

        formula, fixed = _force_eval_ltr(json.loads(skill_data['fun data']))
        if formula:
            formula = str(simplify(formula))

        # Find the scaling stat used in this section of formula
        for stat in scaling_stats:
            if re.search(f'{stat.com2us_desc}\\b', formula):
                skill.scaling_stats.add(stat)
                formula = formula.replace(stat.com2us_desc, f'{{{stat.stat}}}')

        if fixed:
            formula += ' (Fixed)'

        if skill.multiplier_formula != formula:
            skill.multiplier_formula = formula
            print('Updated multiplier formula to {}'.format(skill.multiplier_formula))
            updated = True

        # Special cases for scaling stats
        if master_id in scale_with_max_hp_skills:
            max_hp = scaling_stats.get(com2us_desc='ATTACK_TOT_HP')
            if max_hp not in skill.scaling_stats.all():
                skill.scaling_stats.add(max_hp)
                updated = True
        if master_id == sin_s3_scale_with_def:
            defense = scaling_stats.get(com2us_desc='DEF')
            if defense not in skill.scaling_stats.all():
                skill.scaling_stats.add(defense)
                updated = True
        if master_id == deva_s3_scale_with_target_hp:
            target_max_hp = scaling_stats.get(com2us_desc='TARGET_TOT_HP')
            if target_max_hp not in skill.scaling_stats.all():
                skill.scaling_stats.add(target_max_hp)
                updated = True

        # Finally save it if required
        if updated:
            print('Updated skill {}\n'.format(str(skill)))
            if not preview:
                skill.save()

    if preview:
        print('No changes were saved.')


def _get_monster_data_by_id(master_id):
    monster_table = _get_localvalue_tables(LocalvalueTables.MONSTERS)
    for row in monster_table['rows']:
        unit_master_id = json.loads(row['unit master id'])
        if unit_master_id == master_id:
            return row


def _find_monster_awakens_from(master_id):
    monster_table = _get_localvalue_tables(LocalvalueTables.MONSTERS)
    for row in monster_table['rows']:
        awakens_to_id = json.loads(row['awaken unit id'])
        if awakens_to_id == master_id:
            return row


def parse_monster_data(preview=False):
    monster_table = _get_localvalue_tables(LocalvalueTables.MONSTERS)
    monster_names = get_monster_names_by_id()
    awaken_stat_bonuses = _get_translation_tables()[TranslationTables.AWAKEN_STAT_BONUSES]

    # List of monsters that data indicates are not obtainable, but actually are
    # Dark cow girl
    # Vampire Lord
    definitely_obtainable_monsters = [19305, 19315, 23005, 23015]

    for row in monster_table['rows']:
        master_id = json.loads(row['unit master id'])

        # Skip it if no name translation exists
        if master_id not in monster_names:
            continue

        try:
            monster = Monster.objects.get(com2us_id=master_id)
            updated = False
        except Monster.DoesNotExist:
            monster = Monster.objects.create(com2us_id=master_id, obtainable=False, name='tempname', base_stars=1, natural_stars=1)
            print('!!! Creating new monster {} with com2us ID {}'.format(monster_names[master_id], master_id))
            updated = True

        monster_family = json.loads(row['group id'])
        if monster.family_id != monster_family:
            monster.family_id = monster_family
            print('Updated {} ({}) family ID to {}'.format(monster, master_id, monster_family))
            updated = True

        # Name
        if monster.name != monster_names[master_id]:
            print("Updated {} ({}) name to {}".format(monster, master_id, monster_names[master_id]))
            monster.name = monster_names[master_id]
            updated = True

        # Archetype
        archetype = archetype_map.get(json.loads(row['style type']))
        if monster.archetype != archetype:
            monster.archetype = archetype
            print('Updated {} ({}) archetype to {}'.format(monster, master_id, monster.get_archetype_display()))
            updated = True

        # Element
        element = element_map[json.loads(row['attribute'])]
        if monster.element != element:
            monster.element = element
            print('Updated {} ({}) element to {}'.format(monster, master_id, element))
            updated = True

        # Obtainable
        obtainable = sum(json.loads(row['collection view'])) > 0 or master_id in definitely_obtainable_monsters
        if monster.obtainable != obtainable:
            monster.obtainable = obtainable
            print('Updated {} ({}) obtainability to {}'.format(monster, master_id, obtainable))
            updated = True

        # Homunculus
        is_homunculus = bool(json.loads(row['homunculus']))
        if monster.homunculus != is_homunculus:
            monster.homunculus = is_homunculus
            print('Updated {} ({}) homunculus status to {}'.format(monster, master_id, is_homunculus))
            updated = True

        # Unicorn
        transforms_to_id = json.loads(row['change'])
        if transforms_to_id != 0:
            try:
                transforms_to = Monster.objects.get(com2us_id=transforms_to_id)
            except Monster.DoesNotExist:
                print('!!! {} ({}) can transform into {} but could not find transform monster in database'.format(monster, master_id, transforms_to_id))
            else:
                if monster.transforms_to != transforms_to:
                    monster.transforms_to = transforms_to
                    print('Updated {} ({}) can transform into {} ({})'.format(monster, master_id, transforms_to, transforms_to_id))
                    updated = True
        else:
            if monster.transforms_to is not None:
                monster.transforms_to = None
                print('Removed monster transformation from {} ({})'.format(monster, master_id))
                updated = True

        # Stats
        base_stars = json.loads(row['base class'])
        if monster.base_stars != base_stars:
            monster.base_stars = base_stars
            print('Updated {} ({}) base stars to {}'.format(monster, master_id, monster.base_stars))
            updated = True

        # Set natural stars based on lowest form of the monster's awakening chain
        natural_stars = json.loads(row['natural class'])
        if monster.natural_stars != natural_stars:
            monster.natural_stars = natural_stars
            print('Updated {} ({}) natural stars to {}'.format(monster, master_id, monster.natural_stars))
            updated = True

        if monster.raw_hp != json.loads(row['base con']):
            monster.raw_hp = json.loads(row['base con'])
            print('Updated {} ({}) raw HP to {}'.format(monster, master_id, monster.raw_hp))
            updated = True

        if monster.raw_attack != json.loads(row['base atk']):
            monster.raw_attack = json.loads(row['base atk'])
            print('Updated {} ({}) raw attack to {}'.format(monster, master_id, monster.raw_attack))
            updated = True

        if monster.raw_defense != json.loads(row['base def']):
            monster.raw_defense = json.loads(row['base def'])
            print('Updated {} ({}) raw defense to {}'.format(monster, master_id, monster.raw_defense))
            updated = True

        if monster.resistance != json.loads(row['resistance']):
            monster.resistance = json.loads(row['resistance'])
            print('Updated {} ({}) resistance to {}'.format(monster, master_id, monster.resistance))
            updated = True

        if monster.accuracy != json.loads(row['accuracy']):
            monster.accuracy = json.loads(row['accuracy'])
            print('Updated {} ({}) accuracy to {}'.format(monster, master_id, monster.accuracy))
            updated = True

        if monster.speed != json.loads(row['base speed']):
            monster.speed = json.loads(row['base speed'])
            print('Updated {} ({}) speed to {}'.format(monster, master_id, monster.speed))
            updated = True

        if monster.crit_rate != json.loads(row['critical rate']):
            monster.crit_rate = json.loads(row['critical rate'])
            print('Updated {} ({}) critical rate to {}'.format(monster, master_id, monster.crit_rate))
            updated = True

        if monster.crit_damage != json.loads(row['critical damage']):
            monster.crit_damage = json.loads(row['critical damage'])
            print('Updated {} ({}) critical damage to {}'.format(monster, master_id, monster.crit_damage))
            updated = True

        # Awakening
        awakening_type = AwakenBonusType(json.loads(row['awaken type']))
        awaken_level = json.loads(row['awaken'])
        awakens_to_com2us_id = json.loads(row['awaken unit id'])

        can_awaken = json.loads(row['awaken rank']) > 0
        if monster.can_awaken != can_awaken:
            monster.can_awaken = can_awaken
            print('Updated {} ({}) can awaken status to {}'.format(monster, master_id, monster.can_awaken))

        if can_awaken:
            is_awakened = awaken_level > 0
            awaken_level = Monster.COM2US_AWAKEN_MAP[awaken_level]
        else:
            is_awakened = False
            awaken_level = Monster.AWAKEN_LEVEL_UNAWAKENED

        if is_awakened != monster.is_awakened:
            monster.is_awakened = is_awakened
            print('Updated {} ({}) awakened status to {}'.format(monster, master_id, monster.is_awakened))
            updated = True

        if awaken_level != monster.awaken_level:
            monster.awaken_level = awaken_level
            print('Updated {} ({}) awakening level to {}'.format(monster, master_id, monster.get_awaken_level_display()))
            updated = True

        if monster.can_awaken and awakens_to_com2us_id > 0 and monster.obtainable:
            # Auto-assign awakens_to if possible (which will auto-update awakens_from on other monster)
            try:
                awakens_to_monster = Monster.objects.get(com2us_id=awakens_to_com2us_id)
            except Monster.DoesNotExist:
                print('!!! {} ({}) can awaken but could not find awakened monster in database'.format(monster, master_id))
            else:
                if monster.awakens_to != awakens_to_monster:
                    monster.awakens_to = awakens_to_monster
                    print('Updated {} ({}) awakened version to {}'.format(monster, master_id, awakens_to_monster))
                    updated = True

        awaken_bonus_desc = ''

        if awaken_bonus_desc and monster.awaken_bonus != awaken_bonus_desc:
            monster.awaken_bonus = awaken_bonus_desc
            print('Updated {} ({}) awakened bonus to {}'.format(monster, master_id, awaken_bonus_desc))
            updated = True

        awaken_materials = json.loads(row['awaken materials'])
        essences = [x[0] for x in awaken_materials]  # Extract the essences actually used.

        # Set the essences not used to 0
        if 11001 not in essences and monster.awaken_mats_water_low != 0:
            monster.awaken_mats_water_low = 0
            print("Updated {} ({}) water low awakening essence to 0.".format(monster, master_id))
            updated = True
        if 12001 not in essences and monster.awaken_mats_water_mid != 0:
            monster.awaken_mats_water_mid = 0
            print("Updated {} ({}) water mid awakening essence to 0.".format(monster, master_id))
            updated = True
        if 13001 not in essences and monster.awaken_mats_water_high != 0:
            monster.awaken_mats_water_high = 0
            print("Updated {} ({}) water high awakening essence to 0.".format(monster, master_id))
            updated = True
        if 11002 not in essences and monster.awaken_mats_fire_low != 0:
            monster.awaken_mats_fire_low = 0
            print("Updated {} ({}) fire low awakening essence to 0.".format(monster, master_id))
            updated = True
        if 12002 not in essences and monster.awaken_mats_fire_mid != 0:
            monster.awaken_mats_fire_mid = 0
            print("Updated {} ({}) fire mid awakening essence to 0.".format(monster, master_id))
            updated = True
        if 13002 not in essences and monster.awaken_mats_fire_high != 0:
            monster.awaken_mats_fire_high = 0
            print("Updated {} ({}) fire high awakening essence to 0.".format(monster, master_id))
            updated = True
        if 11003 not in essences and monster.awaken_mats_wind_low != 0:
            monster.awaken_mats_wind_low = 0
            print("Updated {} ({}) wind low awakening essence to 0.".format(monster, master_id))
            updated = True
        if 12003 not in essences and monster.awaken_mats_wind_mid != 0:
            monster.awaken_mats_wind_mid = 0
            print("Updated {} ({}) wind mid awakening essence to 0.".format(monster, master_id))
            updated = True
        if 13003 not in essences and monster.awaken_mats_wind_high != 0:
            monster.awaken_mats_wind_high = 0
            print("Updated {} ({}) wind high awakening essence to 0.".format(monster, master_id))
            updated = True
        if 11004 not in essences and monster.awaken_mats_light_low != 0:
            monster.awaken_mats_light_low = 0
            print("Updated {} ({}) light low awakening essence to 0.".format(monster, master_id))
            updated = True
        if 12004 not in essences and monster.awaken_mats_light_mid != 0:
            monster.awaken_mats_light_mid = 0
            print("Updated {} ({}) light mid awakening essence to 0.".format(monster, master_id))
            updated = True
        if 13004 not in essences and monster.awaken_mats_light_high != 0:
            monster.awaken_mats_light_high = 0
            print("Updated {} ({}) light high awakening essence to 0.".format(monster, master_id))
            updated = True
        if 11005 not in essences and monster.awaken_mats_dark_low != 0:
            monster.awaken_mats_dark_low = 0
            print("Updated {} ({}) dark low awakening essence to 0.".format(monster, master_id))
            updated = True
        if 12005 not in essences and monster.awaken_mats_dark_mid != 0:
            monster.awaken_mats_dark_mid = 0
            print("Updated {} ({}) dark mid awakening essence to 0.".format(monster, master_id))
            updated = True
        if 13005 not in essences and monster.awaken_mats_dark_high != 0:
            monster.awaken_mats_dark_high = 0
            print("Updated {} ({}) dark high awakening essence to 0.".format(monster, master_id))
            updated = True
        if 11006 not in essences and monster.awaken_mats_magic_low != 0:
            monster.awaken_mats_magic_low = 0
            print("Updated {} ({}) magic low awakening essence to 0.".format(monster, master_id))
            updated = True
        if 12006 not in essences and monster.awaken_mats_magic_mid != 0:
            monster.awaken_mats_magic_mid = 0
            print("Updated {} ({}) magic mid awakening essence to 0.".format(monster, master_id))
            updated = True
        if 13006 not in essences and monster.awaken_mats_magic_high != 0:
            monster.awaken_mats_magic_high = 0
            print("Updated {} ({}) magic high awakening essence to 0.".format(monster, master_id))
            updated = True

        # Fill in values for the essences specified
        for essence in awaken_materials:
            if essence[0] == 11001 and monster.awaken_mats_water_low != essence[1]:
                monster.awaken_mats_water_low = essence[1]
                print("Updated {} ({}) water low awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 12001 and monster.awaken_mats_water_mid != essence[1]:
                monster.awaken_mats_water_mid = essence[1]
                print("Updated {} ({}) water mid awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 13001 and monster.awaken_mats_water_high != essence[1]:
                monster.awaken_mats_water_high = essence[1]
                print("Updated {} ({}) water high awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 11002 and monster.awaken_mats_fire_low != essence[1]:
                monster.awaken_mats_fire_low = essence[1]
                print("Updated {} ({}) fire low awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 12002 and monster.awaken_mats_fire_mid != essence[1]:
                monster.awaken_mats_fire_mid = essence[1]
                print("Updated {} ({}) fire mid awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 13002 and monster.awaken_mats_fire_high != essence[1]:
                monster.awaken_mats_fire_high = essence[1]
                print("Updated {} ({}) fire high awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 11003 and monster.awaken_mats_wind_low != essence[1]:
                monster.awaken_mats_wind_low = essence[1]
                print("Updated {} ({}) wind low awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 12003 and monster.awaken_mats_wind_mid != essence[1]:
                monster.awaken_mats_wind_mid = essence[1]
                print("Updated {} ({}) wind mid awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 13003 and monster.awaken_mats_wind_high != essence[1]:
                monster.awaken_mats_wind_high = essence[1]
                print("Updated {} ({}) wind high awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 11004 and monster.awaken_mats_light_low != essence[1]:
                monster.awaken_mats_light_low = essence[1]
                print("Updated {} ({}) light low awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 12004 and monster.awaken_mats_light_mid != essence[1]:
                monster.awaken_mats_light_mid = essence[1]
                print("Updated {} ({}) light mid awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 13004 and monster.awaken_mats_light_high != essence[1]:
                monster.awaken_mats_light_high = essence[1]
                print("Updated {} ({}) light high awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 11005 and monster.awaken_mats_dark_low != essence[1]:
                monster.awaken_mats_dark_low = essence[1]
                print("Updated {} ({}) dark low awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 12005 and monster.awaken_mats_dark_mid != essence[1]:
                monster.awaken_mats_dark_mid = essence[1]
                print("Updated {} ({}) dark mid awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 13005 and monster.awaken_mats_dark_high != essence[1]:
                monster.awaken_mats_dark_high = essence[1]
                print("Updated {} ({}) dark high awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 11006 and monster.awaken_mats_magic_low != essence[1]:
                monster.awaken_mats_magic_low = essence[1]
                print("Updated {} ({}) magic low awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 12006 and monster.awaken_mats_magic_mid != essence[1]:
                monster.awaken_mats_magic_mid = essence[1]
                print("Updated {} ({}) magic mid awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True
            elif essence[0] == 13006 and monster.awaken_mats_magic_high != essence[1]:
                monster.awaken_mats_magic_high = essence[1]
                print("Updated {} ({}) magic high awakening essence to {}".format(monster, master_id, essence[1]))
                updated = True

        # Leader skill
        # Data is a 5 element array
        # [0] - arbitrary unique ID
        # [1] - Area of effect: see com2us_mapping.leader_skill_area_map
        # [2] - Element: see com2us_mapping.element_map
        # [3] - Stat: see com2us_mapping.leader_skill_stat_map
        # [4] - Value of skill bonus

        leader_skill_data = json.loads(row['leader skill'])
        if leader_skill_data:
            stat = leader_skill_stat_map[leader_skill_data[3]]
            value = int(leader_skill_data[4] * 100)

            if leader_skill_data[2]:
                area = LeaderSkill.AREA_ELEMENT
                element = element_map[leader_skill_data[2]]
            else:
                area = leader_skill_area_map[leader_skill_data[1]]
                element = None

            try:
                matching_skill = LeaderSkill.objects.get(attribute=stat, amount=value, area=area, element=element)
            except LeaderSkill.DoesNotExist:
                # Create the new leader skill
                matching_skill = LeaderSkill.objects.create(attribute=stat, amount=value, area=area, element=element)

            if monster.leader_skill != matching_skill:
                monster.leader_skill = matching_skill
                print('Updated {} ({}) leader skill to {}'.format(monster, master_id, matching_skill))
                updated = True
        else:
            if monster.leader_skill is not None:
                monster.leader_skill = None
                print('Removed ({}) leader skill from {}'.format(monster, master_id))
                updated = True

        # Skills
        existing_skills = monster.skills.all()
        skill_set = Skill.objects.filter(com2us_id__in=json.loads(row['base skill']))

        if set(existing_skills) != set(skill_set):
            if not preview:
                monster.skills.set(skill_set)
            print("Updated {} ({}) skill set".format(monster, master_id))
            # updated=True skipped because m2m relationship set directly

        skill_max_levels = skill_set.values_list('max_level', flat=True)
        skill_ups_to_max = sum(skill_max_levels) - len(skill_max_levels)

        if monster.skill_ups_to_max != skill_ups_to_max:
            monster.skill_ups_to_max = skill_ups_to_max
            print(f'Updated {monster} ({master_id}) skill ups to max to {skill_ups_to_max}.')
            updated = True

        # Icon
        icon_nums = json.loads(row['thumbnail'])
        icon_filename = 'unit_icon_{0:04d}_{1}_{2}.png'.format(*icon_nums)
        if monster.image_filename != icon_filename:
            monster.image_filename = icon_filename
            print("Updated {} ({}) icon filename".format(monster, master_id))
            updated = True

        if updated and not preview:
            monster.save()
            print('Saved changes to {} ({})\n'.format(monster, master_id))

    if preview:
        print('No changes were saved.')


def parse_homunculus_data():
    # Homunculus craft costs
    craft_cost_table = _get_localvalue_tables(LocalvalueTables.HOMUNCULUS_CRAFT_COSTS)

    for row in craft_cost_table['rows']:
        mana_cost = json.loads(row['craft cost'])[2]

        for monster_id in json.loads(row['unit master id']):
            monster = Monster.objects.get(com2us_id=monster_id)
            monster.craft_cost = mana_cost
            print('Set craft cost of {} ({}) to {}'.format(monster, monster.com2us_id, mana_cost))
            monster.save()

            # Material costs - clear and re-init
            monster.monstercraftcost_set.all().delete()
            for material_cost in json.loads(row['craft stuff']):
                qty = material_cost[2]
                material = CraftMaterial.objects.get(com2us_id=material_cost[1])
                craft_cost = MonsterCraftCost.objects.create(monster=monster, craft=material, quantity=qty)
                print('Set craft material {} on {} ({})'.format(craft_cost, monster, monster.com2us_id))

    # Homunculus skill costs/requirements
    skill_table = _get_localvalue_tables(LocalvalueTables.HOMUNCULUS_SKILL_TREES)

    for row in skill_table['rows']:
        skill_id = json.loads(row['master id'])
        print('\nUpdating skill upgrade recipe for {}'.format(skill_id))

        try:
            skill = HomunculusSkill.objects.get(skill__com2us_id=skill_id)
        except HomunculusSkill.DoesNotExist:
            skill = HomunculusSkill.objects.create(skill=Skill.objects.get(com2us_id=skill_id))

        skill.mana_cost = json.loads(row['upgrade cost'])[2]
        print('Set upgrade cost of {} upgrade recipe to {}'.format(skill, skill.mana_cost))
        skill.save()

        monsters_used_on_ids = json.loads(row['unit master id'])
        monsters_used_on = Monster.objects.filter(com2us_id__in=monsters_used_on_ids)
        skill.monsters.set(monsters_used_on, clear=True)
        print('Set monster list of {} upgrade recipe to {}'.format(skill, list(skill.monsters.values_list('name', 'com2us_id'))))

        prerequisite_skill_ids = json.loads(row['prerequisite'])
        prerequisite_skills = Skill.objects.filter(com2us_id__in=prerequisite_skill_ids)
        skill.prerequisites.set(prerequisite_skills, clear=True)
        print('Set prerequisite skills of {} upgrade recipe to {}'.format(skill, list(skill.prerequisites.values_list('name', 'com2us_id'))))

        # Material costs - clear and re-init
        skill.homunculusskillcraftcost_set.all().delete()
        for material_cost in json.loads(row['upgrade stuff']):
            qty = material_cost[2]
            material = CraftMaterial.objects.get(com2us_id=material_cost[1])
            upgrade_cost = HomunculusSkillCraftCost.objects.create(skill=skill, craft=material, quantity=qty)
            print('Set upgrade material {} on {} upgrade recipe'.format(upgrade_cost, skill))


def crop_monster_images():
    # If the image is 102x102, we need to crop out the 1px white border.
    for im_path in iglob('herders/static/herders/images/monsters/*.png'):
        im = Image.open(im_path)

        if im.size == (102, 102):
            print(f'Cropping {im_path}')
            crop = im.crop((1, 1, 101, 101))
            im.close()
            crop.save(im_path)


def decrypt_com2us_png():
    com2us_decrypt_values = [
        0x2f, 0x7c, 0x47, 0x55, 0x32, 0x77, 0x9f, 0xfb, 0x5b, 0x86, 0xfe, 0xb6, 0x3e, 0x06, 0xf4, 0xc4,
        0x2e, 0x08, 0x49, 0x11, 0x0e, 0xce, 0x84, 0xd3, 0x7b, 0x18, 0xa6, 0x5c, 0x71, 0x56, 0xe2, 0x3b,
        0xfd, 0xb3, 0x2b, 0x97, 0x9d, 0xfc, 0xca, 0xba, 0x8e, 0x7e, 0x6f, 0x0f, 0xe8, 0xbb, 0xc7, 0xc2,
        0xd9, 0xa4, 0xd2, 0xe0, 0xa5, 0x95, 0xee, 0xab, 0xf3, 0xe4, 0xcb, 0x63, 0x25, 0x70, 0x4e, 0x8d,
        0x21, 0x37, 0x9a, 0xb0, 0xbc, 0xc6, 0x48, 0x3f, 0x23, 0x80, 0x20, 0x01, 0xd7, 0xf9, 0x5e, 0xec,
        0x16, 0xd6, 0xd4, 0x1f, 0x51, 0x42, 0x6c, 0x10, 0x14, 0xb7, 0xcc, 0x82, 0x7f, 0x13, 0x02, 0x00,
        0x72, 0xed, 0x90, 0x57, 0xc1, 0x2c, 0x5d, 0x28, 0x81, 0x1d, 0x38, 0x1a, 0xac, 0xad, 0x35, 0x78,
        0xdc, 0x68, 0xb9, 0x8b, 0x6a, 0xe1, 0xc3, 0xe3, 0xdb, 0x6d, 0x04, 0x27, 0x9c, 0x64, 0x5a, 0x8f,
        0x83, 0x0c, 0xd8, 0xa8, 0x1c, 0x89, 0xd5, 0x43, 0x74, 0x73, 0x4d, 0xae, 0xea, 0x31, 0x6e, 0x1e,
        0x91, 0x1b, 0x59, 0xc9, 0xbd, 0xf7, 0x07, 0xe7, 0x8a, 0x05, 0x8c, 0x4c, 0xbe, 0xc5, 0xdf, 0xe5,
        0xf5, 0x2d, 0x4b, 0x76, 0x66, 0xf2, 0x50, 0xd0, 0xb4, 0x85, 0xef, 0xb5, 0x3c, 0x7d, 0x3d, 0xe6,
        0x9b, 0x03, 0x0d, 0x61, 0x33, 0xf1, 0x92, 0x53, 0xff, 0x96, 0x09, 0x67, 0x69, 0x44, 0xa3, 0x4a,
        0xaf, 0x41, 0xda, 0x54, 0x46, 0xd1, 0xfa, 0xcd, 0x24, 0xaa, 0x88, 0xa7, 0x19, 0xde, 0x40, 0xeb,
        0x94, 0x5f, 0x45, 0x65, 0xf0, 0xb8, 0x34, 0xdd, 0x0b, 0xb1, 0x29, 0xe9, 0x2a, 0x75, 0x87, 0x39,
        0xcf, 0x79, 0x93, 0xa1, 0xb2, 0x30, 0x15, 0x7a, 0x52, 0x12, 0x62, 0x36, 0xbf, 0x22, 0x4f, 0xc0,
        0xa2, 0x17, 0xc8, 0x99, 0x3a, 0x60, 0xa9, 0xa0, 0x58, 0xf6, 0x0a, 0x9e, 0xf8, 0x6b, 0x26, 0x98
    ]

    for im_path in iglob('herders/static/herders/images/**/*.png', recursive=True):
        encrypted = BitStream(filename=im_path)

        # Check if it is encrypted. 8th byte is 0x0B instead of the correct signature 0x0A
        encrypted.pos = 0x07 * 8
        signature = encrypted.peek('uint:8')
        if signature == 0x0B:
            print(f'Decrypting {im_path}')
            # Correct the PNG signature
            encrypted.overwrite('0x0A', encrypted.pos)

            # Replace bits with magic decrypted values
            try:
                while True:
                    pos = encrypted.pos
                    val = encrypted.peek('uint:8')
                    encrypted.overwrite(Bits(uint=com2us_decrypt_values[val], length=8), pos)
            except ReadError:
                # EOF
                pass

            # Write it back to the file
            with open(im_path, 'wb') as f:
                encrypted.tofile(f)

            continue

        # Check for the weird jpeg files that need to be trimmed
        encrypted.pos = 0
        if encrypted.peek('bytes:5') == b'Joker':
            print(f'Trimming and converting weird JPEG to PNG {im_path}')
            del encrypted[0:16 * 8]

            # Open it as a jpg and resave to disk
            new_imfile = Image.open(io.BytesIO(encrypted.tobytes()))
            new_imfile.save(im_path)


class TranslationTables(IntEnum):
    ISLAND_NAMES = 1
    MONSTER_NAMES = 2
    SUMMON_METHODS = 10
    SKILL_NAMES = 20
    SKILL_DESCRIPTIONS = 21
    AWAKEN_STAT_BONUSES = 24
    LEADER_SKILL_DESCRIPTIONS = 25
    WORLD_MAP_DUNGEON_NAMES = 29
    CAIROS_DUNGEON_NAMES = 30


def get_monster_names_by_id():
    return _get_translation_tables()[TranslationTables.MONSTER_NAMES]


def get_skill_names_by_id():
    return _get_translation_tables()[TranslationTables.SKILL_NAMES]


def get_skill_descs_by_id():
    return _get_translation_tables()[TranslationTables.SKILL_DESCRIPTIONS]


# Dungeons and Scenarios
def parse_scenarios():
    scenario_table = _get_localvalue_tables(LocalvalueTables.SCENARIO_LEVELS)
    scenario_names = _get_scenario_names_by_id()

    for row in scenario_table['rows']:
        dungeon_id = int(row['region id'])
        name = scenario_names.get(dungeon_id, 'UNKNOWN')

        # Update (or create) the dungeon this scenario level will be assigned to
        dungeon, created = Dungeon.objects.update_or_create(
            com2us_id=dungeon_id,
            name=name,
            category=Dungeon.CATEGORY_SCENARIO,
        )

        if created:
            print(f'Added new dungeon {dungeon.name} - {dungeon.slug}')

        # Update (or create) the scenario level
        difficulty = int(row['difficulty'])
        stage = int(row['stage no'])
        energy_cost = int(row['energy cost'])
        slots = int(row['player unit slot'])

        level, created = Level.objects.update_or_create(
            dungeon=dungeon,
            difficulty=difficulty,
            floor=stage,
            energy_cost=energy_cost,
            frontline_slots=slots,
            backline_slots=None,
            total_slots=slots,
        )

        if created:
            print(f'Added new level for {dungeon.name} - {level.get_difficulty_display()} B{stage}')


def _get_scenario_names_by_id():
    # Assemble scenario-only names from world map table to match the 'region id' in SCENARIOS localvalue table
    world_map_names = _get_translation_tables()[TranslationTables.WORLD_MAP_DUNGEON_NAMES]
    world_map_table = _get_localvalue_tables(LocalvalueTables.WORLD_MAP)

    scenario_table = [
        val for val in world_map_table['rows'] if int(val['type']) == 3
    ]

    return {
        scen_id + 1: world_map_names[int(scenario_data['world id'])] for scen_id, scenario_data in enumerate(scenario_table)
    }


def parse_cairos_dungeons():
    dungeon_names = _get_translation_tables()[TranslationTables.CAIROS_DUNGEON_NAMES]

    with open('bestiary/parse/com2us_data/dungeon_list.json', 'r') as f:
        for dungeon_data in json.load(f):
            group_id = dungeon_data['group_id']

            dungeon_id = dungeon_data['dungeon_id']
            name = dungeon_names[group_id]

            dungeon, created = Dungeon.objects.update_or_create(
                com2us_id=dungeon_id,
                name=name,
                category=Dungeon.CATEGORY_CAIROS,
            )

            if created:
                print(f'Added new dungeon {dungeon.name} - {dungeon.slug}')

            # Create levels
            for level_data in dungeon_data['stage_list']:
                stage = int(level_data['stage_id'])
                energy_cost = int(level_data['cost'])
                slots = 5

                level, created = Level.objects.update_or_create(
                    dungeon=dungeon,
                    floor=stage,
                    energy_cost=energy_cost,
                    frontline_slots=slots,
                    backline_slots=None,
                    total_slots=slots,
                )

                if created:
                    print(f'Added new level for {dungeon.name} - {level.get_difficulty_display() if level.difficulty is not None else ""} B{stage}')


def parse_secret_dungeons():
    dungeon_table = _get_localvalue_tables(LocalvalueTables.SECRET_DUNGEONS)

    for row in dungeon_table['rows']:
        dungeon_id = int(row['instance id'])
        monster_id = int(row['summon pieces'])
        monster = Monster.objects.get(com2us_id=monster_id)

        dungeon, created = SecretDungeon.objects.update_or_create(
            com2us_id=dungeon_id,
            name=f'{monster.get_element_display()} {monster.name} Secret Dungeon',
            category=SecretDungeon.CATEGORY_SECRET,
            monster=monster,
        )

        if created:
            print(f'Added new secret dungeon {dungeon.name} - {dungeon.slug}')

        # Create a single level referencing this dungeon
        level, created = Level.objects.update_or_create(
            dungeon=dungeon,
            floor=1,
            energy_cost=3,
            frontline_slots=5,
            backline_slots=None,
            total_slots=5,
        )

        if created:
            print(f'Added new level for {dungeon.name} - {level.get_difficulty_display() if level.difficulty is not None else ""} B{1}')


def parse_elemental_rift_dungeons():
    dungeon_table = _get_localvalue_tables(LocalvalueTables.ELEMENTAL_RIFT_DUNGEONS)
    monster_names = _get_translation_tables()[TranslationTables.MONSTER_NAMES]

    for row in dungeon_table['rows']:
        if int(row['enable']):
            dungeon_id = int(row['master id'])
            name = monster_names[int(row['unit id'])].strip()

            dungeon, created = Dungeon.objects.update_or_create(
                com2us_id=dungeon_id,
                name=name,
                category=Dungeon.CATEGORY_RIFT_OF_WORLDS_BEASTS,
            )

            if created:
                print(f'Added new dungeon {dungeon.name} - {dungeon.slug}')

            # Create a single level referencing this dungeon
            level, created = Level.objects.update_or_create(
                dungeon=dungeon,
                floor=1,
                energy_cost=int(row['cost energy']),
                frontline_slots=4,
                backline_slots=4,
                total_slots=6,
            )

            if created:
                print(f'Added new level for {dungeon.name} - {level.get_difficulty_display() if level.difficulty is not None else ""} B{1}')


def parse_rift_raid():
    raid_table = _get_localvalue_tables(LocalvalueTables.RIFT_RAIDS)

    for row in raid_table['rows']:
        raid_id = int(row['raid id'])
        dungeon, created = Dungeon.objects.update_or_create(
            com2us_id=raid_id,
            name='Rift Raid',
            category=Dungeon.CATEGORY_RIFT_OF_WORLDS_RAID,
        )

        if created:
            print(f'Added new dungeon {dungeon.name} - {dungeon.slug}')

        level, created = Level.objects.update_or_create(
            dungeon=dungeon,
            floor=int(row['stage id']),
            energy_cost=int(row['cost energy']),
            frontline_slots=4,
            backline_slots=4,
            total_slots=6,
        )

        if created:
            print(f'Added new level for {dungeon.name} - {level.get_difficulty_display() if level.difficulty is not None else ""} B{1}')


def save_translation_tables():
    tables = _get_translation_tables()
    with open('bestiary/parse/com2us_data/text_eng.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['table_num', 'id', 'text'])
        for table_idx, table in enumerate(tables):
            for key, text in table.items():
                writer.writerow([table_idx, key, text.strip()])


def _get_translation_tables(filename='bestiary/parse/com2us_data/text_eng.dat'):
    raw = ConstBitStream(filename=filename)
    tables = []

    table_ver = raw.read('intle:32')
    print(f'Translation table version {table_ver}')

    try:
        while True:
            table_len = raw.read('intle:32')
            table = {}

            for _ in range(table_len):
                str_id, str_len = raw.readlist('intle:32, intle:32')
                parsed_str = binascii.a2b_hex(raw.read('hex:{}'.format(str_len * 8))[:-4])
                table[str_id] = parsed_str.decode("utf-8")

            tables.append(table)
    except ReadError:
        # EOF
        pass

    return tables


class LocalvalueTables(IntEnum):
    WIZARD_XP_REQUIREMENTS = 1
    SKY_ISLANDS = 2
    BUILDINGS = 3
    DECORATIONS = 4
    OBSTACLES = 5
    MONSTERS = 6
    MONSTER_LEVELING = 7
    # Unknown table 8 - some sort of effect mapping
    SKILL_EFFECTS = 9
    SKILLS = 10
    SUMMON_METHODS = 11
    RUNE_SET_DEFINITIONS = 12
    NPC_ARENA_RIVALS = 13
    ACHIEVEMENTS = 14
    TUTORIALS = 15
    SCENARIO_BOSSES = 16
    SCENARIO_LEVELS = 17
    CAIROS_BOSS_INTROS = 18
    # Unknown table 19 - more effect mapping
    WORLD_MAP = 20
    ARENA_RANKS = 21
    MONTHLY_REWARDS = 22
    CAIROS_DUNGEON_LIST = 23
    INVITE_FRIEND_REWARDS_OLD = 24
    # Unknown table 25 - probably x/y positions of 3d models in dungeons/scenarios
    AWAKENING_ESSENCES = 26
    ACCOUNT_BOOSTS = 27  # XP boost, mana boost, etc
    ARENA_WIN_STREAK_BONUSES = 28
    CHAT_BANNED_WORDS = 29
    IFRIT_SUMMON_ITEM = 30
    SECRET_DUNGEONS = 31
    SECRET_DUNGEON_ENEMIES = 32
    PURCHASEABLE_ITEMS = 33
    DAILY_MISSIONS = 34
    VARIOUS_CONSTANTS = 35
    MONSTER_POWER_UP_COSTS = 36
    RUNE_UNEQUIP_COSTS = 37
    RUNE_UPGRADE_COSTS_AND_CHANCES = 38
    SCENARIO_REGIONS = 39
    PURCHASEABLE_ITEMS2 = 40
    # Unknown table 41 - scroll/cost related?
    MAIL_ITEMS = 42
    # Unknown table 43 - angelmon reward sequences?
    MONSTER_FUSION_RECIPES_OLD = 44
    TOA_REWARDS = 45
    MONSTER_FUSION_RECIPES = 46
    TOA_FLOOR_MODELS_AND_EFFECTS = 47
    ELLIA_COSTUMES = 48
    GUILD_LEVELS = 49  # Unimplemented in-game
    GUILD_BONUSES = 50  # Unimplemented in-game
    RUNE_STAT_VALUES = 51
    GUILD_RANKS = 52
    GUILD_UNASPECTED_SUMMON_PIECES = 53  # Ifrit and Cowgirl pieces
    # Unknown table 54 - possible rune crafting or package
    MONSTER_TRANSMOGS = 55
    ELEMENTAL_RIFT_DUNGEONS = 56
    WORLD_BOSS_SCRIPT = 57
    WORLD_BOSS_ELEMENTAL_ADVANTAGES = 58
    WORLD_BOSS_FIGHT_RANKS = 59
    WORLD_BOSS_PLAYER_RANKS = 60
    SKILL_TRANSMOGS = 61
    ENCHANT_GEMS = 62
    GRINDSTONES = 63
    RUNE_CRAFT_APPLY_COSTS = 64
    RIFT_RAIDS = 65
    # Unknown table 66 - some sort of reward related
    ELLIA_COSTUME_ITEMS = 67
    CHAT_BANNED_WORDS2 = 68
    CHAT_BANNED_WORDS3 = 69
    CHAT_BANNED_WORDS4 = 70
    CRAFT_MATERIALS = 71
    HOMUNCULUS_SKILL_TREES = 72
    HOMUNCULUS_CRAFT_COSTS = 73
    ELEMENTAL_DAMAGE_RANKS = 74
    WORLD_ARENA_RANKS = 75
    WORLD_ARENA_SHOP_ITEMS = 76
    CHAT_BANNED_WORDS5 = 77
    CHAT_BANNED_WORDS6 = 78
    CHAT_BANNED_WORDS7 = 79
    CHAT_BANNED_WORDS8 = 80
    ARENA_CHOICE_UI = 81
    IFRIT_TRANSMOGS = 82
    # Unknown table 83 - value lists related to game version
    CHALLENGES = 84
    # Unknown table 85 - some sort of rules
    WORLD_ARENA_SEASON_REWARDS = 86
    WORLD_ARENA_RANKS2 = 87
    WORLD_ARENA_REWARD_LIST = 88
    GUILD_SIEGE_MAP = 89
    GUILD_SIEGE_REWARD_BOXES = 90
    GUILD_SIEGE_RANKINGS = 91


def save_localvalue_tables():
    for x in range(1,102):
        table = _get_localvalue_tables(x)
        with open(f'bestiary/parse/com2us_data/localvalue_{x}.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=table['header'])
            writer.writeheader()
            for row in table['rows']:
                writer.writerow(row)


def _decrypt_localvalue_dat():
    with open('bestiary/parse/com2us_data/localvalue.dat') as f:
        return decrypt_response(f.read().strip('\0'))


_localvalue_table_cache = {}


def _get_localvalue_tables(table_id):
    if table_id in _localvalue_table_cache:
        return _localvalue_table_cache[table_id]

    tables = {}
    decrypted_localvalue = _decrypt_localvalue_dat()

    raw = ConstBitStream(decrypted_localvalue)
    raw.read('pad:{}'.format(0x24 * 8))
    num_tables = raw.read('intle:32') - 1
    raw.read('pad:{}'.format(0xc * 8))

    # if num_tables > int(max(LocalvalueTables)):
    #     print('WARNING! Found {} tables in localvalue.dat. There are only {} tables defined!'.format(num_tables, int(max(LocalvalueTables))))

    # Read the locations of all defined tables
    for x in range(0, num_tables):
        table_num, start, end = raw.readlist(['intle:32']*3)
        tables[table_num] = {
            'start': start,
            'end': end
        }

    # Record where we are now, as that is the offset of where the first table starts
    table_start_offset = int(raw.pos / 8)

    # Load the requested table and return it
    raw = ConstBitStream(decrypted_localvalue)
    table_data = {
        'header': [],
        'rows': []
    }

    raw.read('pad:{}'.format((table_start_offset + tables[table_id]['start']) * 8))
    table_str = raw.read('bytes:{}'.format(tables[table_id]['end'] - tables[table_id]['start'])).decode('utf-8').strip()
    table_rows = table_str.split('\r\n')
    table_data['header'] = table_rows[0].split('\t')
    table_data['rows'] = [{table_data['header'][col]: value for col, value in enumerate(row.split('\t'))} for row in table_rows[1:]]

    # Cache results
    _localvalue_table_cache[table_id] = table_data

    return table_data
