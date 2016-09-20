from glob import iglob
from PIL import Image
import csv
import json
from sympy import simplify
from bitstring import ConstBitStream, ReadError

from .models import *
from sw_parser.com2us_mapping import *

# This routine expects two CSV files in the root of the project.
# One is the monster definition table and the other is the skill definition table in localvalue.dat


def assign_skill_ids():
    with open('monsters.csv', 'rb') as csvfile:
        monster_data = csv.DictReader(csvfile)

        for row in monster_data:
            monster_family = int(row['unit master id'][:3])
            awakened = row['unit master id'][3] == '1'
            element = element_map.get(int(row['unit master id'][-1:]))

            try:
                monster = Monster.objects.get(com2us_id=monster_family, is_awakened=awakened, element=element)
            except Monster.DoesNotExist:
                print 'Unable to find monster ' + str(row['unit master id'])
            else:
                skills = monster.skills.all().order_by('slot')
                skill_ids = json.loads(row['base skill'])

                if len(skills) != len(skill_ids):
                    print 'Error! ' + str(monster) + ' skill count in bestiary does not match CSV skill count'
                else:
                    for x, skill_id in enumerate(skill_ids):
                        if skills[x].com2us_id is None:
                            skills[x].com2us_id = skill_id
                            skills[x].save()
                            # print 'Updated ID of ' + str(skills[x])
                        elif skills[x].com2us_id != skill_id:
                            print 'Error! Skill ' + str(skills[x]) + ' already has an ID assigned. Tried to assign ' + str(skill_id)


def parse_skill_data(preview=False):
    parsed_skill_names = get_skill_names_by_id()
    parsed_skill_descs = get_skill_descs_by_id()

    with open('skills.csv', 'rb') as csvfile:
        skill_data = csv.DictReader(csvfile)

        scaling_stats = ScalingStat.objects.all()
        ignore_def_effect = Effect.objects.get(name='Ignore DEF')

        for csv_skill in skill_data:
            # Get matching skill in DB
            master_id = int(csv_skill['master id'])

            try:
                skill = Skill.objects.get(com2us_id=master_id)
            except Skill.DoesNotExist:
                continue
            else:
                updated = False

                # Name
                if skill.name != parsed_skill_names[master_id]:
                    skill.name = parsed_skill_names[master_id]
                    print 'Updated name to {}'.format(skill.name)
                    updated = True

                # Description
                if skill.description != parsed_skill_descs[master_id]:
                    skill.description = parsed_skill_descs[master_id]
                    print 'Updated description to {}'.format(skill.description)
                    updated = True

                # Icon
                icon_nums = json.loads(csv_skill['thumbnail'])
                icon_filename = 'skill_icon_{0:04d}_{1}_{2}.png'.format(*icon_nums)
                if skill.icon_filename != icon_filename:
                    skill.icon_filename = icon_filename
                    print 'Updated icon to {}'.format(skill.icon_filename)
                    updated = True

                # Cooltime
                cooltime = int(csv_skill['cool time']) + 1 if int(csv_skill['cool time']) > 0 else None

                if skill.cooltime != cooltime:
                    skill.cooltime = cooltime
                    print 'Updated cooltime to {}'.format(skill.cooltime)
                    updated = True

                # Max Level
                max_lv = int(csv_skill['max level'])
                if skill.max_level != max_lv:
                    skill.max_level = max_lv
                    print 'Updated max level to {}'.format(skill.max_level)
                    updated = True

                # Level up progress
                level_up_desc = {
                    'DR': 'Effect Rate +{0}%',
                    'AT': 'Damage +{0}%',
                    'HE': 'Recovery +{0}%',
                    'TN': 'Cooltime Turn -{0}',
                    'SD': 'Shield +{0}%',
                }

                level_up_text = ''

                for level in json.loads(csv_skill['level']):
                    level_up_text += level_up_desc[level[0]].format(level[1]) + '\n'

                if skill.level_progress_description != level_up_text:
                    skill.level_progress_description = level_up_text
                    print 'Updated level-up progress description'
                    updated = True

                # Buffs
                # maybe this later. Data seems incomplete sometimes.

                # Scaling formula and stats
                skill.scaling_stats.clear()

                # Skill multiplier formula
                if skill.multiplier_formula_raw != csv_skill['fun data']:
                    skill.multiplier_formula_raw = csv_skill['fun data']
                    print 'Updated raw multiplier formula to {}'.format(skill.multiplier_formula_raw)
                    updated = True

                formula = ''
                fixed = False
                formula_array = [''.join(map(str, scale)) for scale in json.loads(csv_skill['fun data'])]
                plain_operators = '+-*/'
                if len(formula_array):
                    for operation in formula_array:
                        # Remove any multiplications by 1 beforehand. It makes the simplifier function happier.
                        operation = operation.replace('*1.0', '')
                        if 'FIXED' in operation:
                            operation = operation.replace('FIXED', '')
                            fixed = True
                            # TODO: Add Ignore Defense effect to skill if not present already

                        if operation not in plain_operators:
                            formula += '({0})'.format(operation)
                        else:
                            formula += '{0}'.format(operation)

                    formula = str(simplify(formula))

                    # Find the scaling stat used in this section of formula
                    for stat in scaling_stats:
                        if stat.com2us_desc in formula:
                            skill.scaling_stats.add(stat)
                            if stat.description:
                                human_readable = '<mark data-toggle="tooltip" data-placement="top" title="' + stat.description + '">' + stat.stat + '</mark>'
                            else:
                                human_readable = '<mark>' + stat.stat + '</mark>'
                            formula = formula.replace(stat.com2us_desc, human_readable)

                    if fixed:
                        formula += ' (Fixed)'
                        
                    if skill.multiplier_formula != formula:
                        skill.multiplier_formula = formula
                        print 'Updated multiplier formula to {}'.format(skill.multiplier_formula)
                        updated = True

                # Finally save it if required
                if updated and not preview:
                    skill.save()
                    print 'Updated skill ' + str(skill)

        if preview:
            print 'No changes were saved.'


def parse_monster_data(preview=False):
    parsed_monster_names = get_monster_names_by_id()

    with open('monsters.csv', 'rb') as csvfile:
        monster_data = csv.DictReader(csvfile)

        for row in monster_data:
            master_id = int(row['unit master id'])

            if (master_id < 40000 and row['unit master id'][3] != '2') or (1000101 <= master_id <= 1000113):
                # Non-summonable monsters appear with IDs above 40000 and a 2 in that position represents the japanese 'incomplete' monsters
                # Homonculus IDs start at 1000101

                monster_family = int(row['discussion id'])
                awakened = row['unit master id'][-2] == '1'
                element = element_map.get(int(row['attribute']))

                try:
                    monster = Monster.objects.get(family_id=monster_family, is_awakened=awakened, element=element)
                except Monster.DoesNotExist:
                    continue
                else:
                    updated = False

                    # Com2us family and ID
                    if monster.com2us_id != master_id:
                        monster.com2us_id = master_id
                        print 'Updated {} master ID to {}'.format(monster, master_id)
                        updated = True

                    if monster.family_id != monster_family:
                        monster.family_id = monster_family
                        print 'Updated {} family ID to {}'.format(monster, monster_family)
                        updated = True

                    # Name
                    if monster.name != parsed_monster_names[master_id]:
                        print "Updated {}'s name to {}".format(monster, parsed_monster_names[master_id])
                        monster.name = parsed_monster_names[master_id]
                        updated = True

                    # Archetype
                    archetype = row['style type']

                    if archetype == 1 and monster.archetype != Monster.TYPE_ATTACK:
                        monster.archetype = Monster.TYPE_ATTACK
                        print 'Updated {} archetype to attack'.format(monster)
                        updated = True
                    elif archetype == 2 and monster.archetype != Monster.TYPE_DEFENSE:
                        monster.archetype = Monster.TYPE_DEFENSE
                        print "Updated {} archetype to defense".format(monster)
                        updated = True
                    elif archetype == 3 and monster.archetype != Monster.TYPE_HP:
                        monster.archetype = Monster.TYPE_HP
                        print "Updated {} archetype to hp".format(monster)
                        updated = True
                    elif archetype == 4 and monster.archetype != Monster.TYPE_SUPPORT:
                        monster.archetype = Monster.TYPE_SUPPORT
                        print "Updated {} archetype to support".format(monster)
                        updated = True
                    elif archetype == 5 and monster.archetype != Monster.TYPE_MATERIAL:
                        monster.archetype = Monster.TYPE_MATERIAL
                        print "Updated {} archetype to material".format(monster)
                        updated = True

                    # Base stars
                    if monster.base_stars != int(row['base class']):
                        monster.base_stars = int(row['base class'])
                        print 'Updated {} base stars to {}'.format(monster, monster.base_stars)
                        updated = True

                    # Base Stats
                    # Need to figure out how to translate base stats from given 1* values to base values.
                    if monster.resistance != int(row['resistance']):
                        monster.resistance = int(row['resistance'])
                        print 'Updated {} resistance to {}'.format(monster, monster.resistance)
                        updated = True

                    if monster.accuracy != int(row['accuracy']):
                        monster.accuracy = int(row['accuracy'])
                        print 'Updated {} accuracy to {}'.format(monster, monster.accuracy)
                        updated = True

                    if monster.speed != int(row['base speed']):
                        monster.speed = int(row['base speed'])
                        print 'Updated {} speed to {}'.format(monster, monster.speed)
                        updated = True

                    if monster.crit_rate != int(row['critical rate']):
                        monster.crit_rate = int(row['critical rate'])
                        print 'Updated {} critical rate to {}'.format(monster, monster.crit_rate)
                        updated = True

                    if monster.crit_damage != int(row['critical damage']):
                        monster.crit_damage = int(row['critical damage'])
                        print 'Updated {} critical damage to {}'.format(monster, monster.crit_damage)
                        updated = True

                    # Awaken materials
                    awaken_materials = json.loads(row['awaken materials'])
                    essences = [x[0] for x in awaken_materials]  # Extract the essences actually used.

                    # Set the essences not used to 0
                    if 11001 not in essences and monster.awaken_mats_water_low != 0:
                        monster.awaken_mats_water_low = 0
                        print "Updated {} water low awakening essence to 0.".format(monster)
                        updated = True
                    if 12001 not in essences and monster.awaken_mats_water_mid != 0:
                        monster.awaken_mats_water_mid = 0
                        print "Updated {} water mid awakening essence to 0.".format(monster)
                        updated = True
                    if 13001 not in essences and monster.awaken_mats_water_high != 0:
                        monster.awaken_mats_water_high = 0
                        print "Updated {} water high awakening essence to 0.".format(monster)
                        updated = True
                    if 11002 not in essences and monster.awaken_mats_fire_low != 0:
                        monster.awaken_mats_fire_low = 0
                        print "Updated {} fire low awakening essence to 0.".format(monster)
                        updated = True
                    if 12002 not in essences and monster.awaken_mats_fire_mid != 0:
                        monster.awaken_mats_fire_mid = 0
                        print "Updated {} fire mid awakening essence to 0.".format(monster)
                        updated = True
                    if 13002 not in essences and monster.awaken_mats_fire_high != 0:
                        monster.awaken_mats_fire_high = 0
                        print "Updated {} fire high awakening essence to 0.".format(monster)
                        updated = True
                    if 11003 not in essences and monster.awaken_mats_wind_low != 0:
                        monster.awaken_mats_wind_low = 0
                        print "Updated {} wind low awakening essence to 0.".format(monster)
                        updated = True
                    if 12003 not in essences and monster.awaken_mats_wind_mid != 0:
                        monster.awaken_mats_wind_mid = 0
                        print "Updated {} wind mid awakening essence to 0.".format(monster)
                        updated = True
                    if 13003 not in essences and monster.awaken_mats_wind_high != 0:
                        monster.awaken_mats_wind_high = 0
                        print "Updated {} wind high awakening essence to 0.".format(monster)
                        updated = True
                    if 11004 not in essences and monster.awaken_mats_light_low != 0:
                        monster.awaken_mats_light_low = 0
                        print "Updated {} light low awakening essence to 0.".format(monster)
                        updated = True
                    if 12004 not in essences and monster.awaken_mats_light_mid != 0:
                        monster.awaken_mats_light_mid = 0
                        print "Updated {} light mid awakening essence to 0.".format(monster)
                        updated = True
                    if 13004 not in essences and monster.awaken_mats_light_high != 0:
                        monster.awaken_mats_light_high = 0
                        print "Updated {} light high awakening essence to 0.".format(monster)
                        updated = True
                    if 11005 not in essences and monster.awaken_mats_dark_low != 0:
                        monster.awaken_mats_dark_low = 0
                        print "Updated {} dark low awakening essence to 0.".format(monster)
                        updated = True
                    if 12005 not in essences and monster.awaken_mats_dark_mid != 0:
                        monster.awaken_mats_dark_mid = 0
                        print "Updated {} dark mid awakening essence to 0.".format(monster)
                        updated = True
                    if 13005 not in essences and monster.awaken_mats_dark_high != 0:
                        monster.awaken_mats_dark_high = 0
                        print "Updated {} dark high awakening essence to 0.".format(monster)
                        updated = True
                    if 11006 not in essences and monster.awaken_mats_magic_low != 0:
                        monster.awaken_mats_magic_low = 0
                        print "Updated {} magic low awakening essence to 0.".format(monster)
                        updated = True
                    if 12006 not in essences and monster.awaken_mats_magic_mid != 0:
                        monster.awaken_mats_magic_mid = 0
                        print "Updated {} magic mid awakening essence to 0.".format(monster)
                        updated = True
                    if 13006 not in essences and monster.awaken_mats_magic_high != 0:
                        monster.awaken_mats_magic_high = 0
                        print "Updated {} magic high awakening essence to 0.".format(monster)
                        updated = True

                    # Fill in values for the essences specified
                    for essence in awaken_materials:
                        if essence[0] == 11001 and monster.awaken_mats_water_low != essence[1]:
                            monster.awaken_mats_water_low = essence[1]
                            print "Updated {} water low awakening essence to {}".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 12001 and monster.awaken_mats_water_mid != essence[1]:
                            monster.awaken_mats_water_mid = essence[1]
                            print "Updated {} water mid awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 13001 and monster.awaken_mats_water_high != essence[1]:
                            monster.awaken_mats_water_high = essence[1]
                            print "Updated {} water high awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 11002 and monster.awaken_mats_fire_low != essence[1]:
                            monster.awaken_mats_fire_low = essence[1]
                            print "Updated {} fire low awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 12002 and monster.awaken_mats_fire_mid != essence[1]:
                            monster.awaken_mats_fire_mid = essence[1]
                            print "Updated {} fire mid awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 13002 and monster.awaken_mats_fire_high != essence[1]:
                            monster.awaken_mats_fire_high = essence[1]
                            print "Updated {} fire high awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 11003 and monster.awaken_mats_wind_low != essence[1]:
                            monster.awaken_mats_wind_low = essence[1]
                            print "Updated {} wind low awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 12003 and monster.awaken_mats_wind_mid != essence[1]:
                            monster.awaken_mats_wind_mid = essence[1]
                            print "Updated {} wind mid awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 13003 and monster.awaken_mats_wind_high != essence[1]:
                            monster.awaken_mats_wind_high = essence[1]
                            print "Updated {} wind high awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 11004 and monster.awaken_mats_light_low != essence[1]:
                            monster.awaken_mats_light_low = essence[1]
                            print "Updated {} light low awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 12004 and monster.awaken_mats_light_mid != essence[1]:
                            monster.awaken_mats_light_mid = essence[1]
                            print "Updated {} light mid awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 13004 and monster.awaken_mats_light_high != essence[1]:
                            monster.awaken_mats_light_high = essence[1]
                            print "Updated {} light high awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 11005 and monster.awaken_mats_dark_low != essence[1]:
                            monster.awaken_mats_dark_low = essence[1]
                            print "Updated {} dark low awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 12005 and monster.awaken_mats_dark_mid != essence[1]:
                            monster.awaken_mats_dark_mid = essence[1]
                            print "Updated {} dark mid awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 13005 and monster.awaken_mats_dark_high != essence[1]:
                            monster.awaken_mats_dark_high = essence[1]
                            print "Updated {} dark high awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 11006 and monster.awaken_mats_magic_low != essence[1]:
                            monster.awaken_mats_magic_low = essence[1]
                            print "Updated {} magic low awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 12006 and monster.awaken_mats_magic_mid != essence[1]:
                            monster.awaken_mats_magic_mid = essence[1]
                            print "Updated {} magic mid awakening essence to ".format(monster, essence[1])
                            updated = True
                        elif essence[0] == 13006 and monster.awaken_mats_magic_high != essence[1]:
                            monster.awaken_mats_magic_high = essence[1]
                            print "Updated {} magic high awakening essence to ".format(monster, essence[1])
                            updated = True

                    # Leader skill
                    # TODO

                    # Skills
                    # TODO

                    # Icon
                    icon_nums = json.loads(row['thumbnail'])
                    icon_filename = 'unit_icon_{0:04d}_{1}_{2}.png'.format(*icon_nums)
                    if monster.image_filename != icon_filename:
                        monster.image_filename = icon_filename
                        print "Updated {}'s icon filename".format(monster)
                        updated = True

                    if updated and not preview:
                        monster.save()
                        print 'Saved updates to {}'.format(monster)
        if preview:
            print 'No changes were saved.'


def crop_monster_images():
    # If the image is 102x102, we need to crop out the 1px white border.
    for im_path in iglob('herders/static/herders/images/monsters/*.png'):
        im = Image.open(im_path)

        if im.size == (102, 102):
            crop = im.crop((1, 1, 101, 101))
            im.close()
            crop.save(im_path)


def get_monster_names_by_id():
    return _get_strings_from_dat(0x7e * 8, 0x4f14 * 8)


def get_skill_names_by_id():
    return _get_strings_from_dat(0x2776d * 8, 0x3195c * 8)


def get_skill_descs_by_id():
    return _get_strings_from_dat(0x31983 * 8, 0x6b53d * 8)


def _get_strings_from_dat(start_pos, end_pos):
    text = ConstBitStream(filename='text_eng.dat', offset=start_pos, length=end_pos - start_pos)

    strings = dict()

    # Iterate through translations to avoid random pattern matching when ID is valid ASCII too
    try:
        while True:
            parsed_id, str_len = text.readlist('intle:32, intle:32')
            parsed_str = text.read('hex:{}'.format(str_len * 8))[:-4].decode('hex')
            strings[parsed_id] = parsed_str
    except ReadError:
        #EOF
        pass

    return strings

