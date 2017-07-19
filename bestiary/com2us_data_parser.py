from enum import IntEnum
from glob import iglob
from PIL import Image
import binascii
import csv
import json
from sympy import simplify
from bitstring import ConstBitStream, ReadError

from .models import *
from sw_parser.com2us_mapping import *
from sw_parser.com2us_parser import decrypt_response


def parse_skill_data(preview=False):
    skill_table = _get_localvalue_tables(LocalvalueTables.SKILLS)
    skill_names = get_skill_names_by_id()
    skill_descriptions = get_skill_descs_by_id()

    scaling_stats = ScalingStat.objects.all()
    ignore_def_effect = Effect.objects.get(name='Ignore DEF')

    for skill_data in skill_table['rows']:
        # Get matching skill in DB
        master_id = int(skill_data['master id'])

        try:
            skill = Skill.objects.get(com2us_id=master_id)
        except Skill.DoesNotExist:
            continue
        else:
            updated = False

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
            cooltime = int(skill_data['cool time']) + 1 if int(skill_data['cool time']) > 0 else None

            if skill.cooltime != cooltime:
                skill.cooltime = cooltime
                print('Updated cooltime to {}'.format(skill.cooltime))
                updated = True

            # Max Level
            max_lv = int(skill_data['max level'])
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

            formula = ''
            fixed = False
            formula_array = [''.join(map(str, scale)) for scale in json.loads(skill_data['fun data'])]
            plain_operators = '+-*/'
            if len(formula_array):
                for operation in formula_array:
                    # Remove any multiplications by 1 beforehand. It makes the simplifier function happier.
                    operation = operation.replace('*1.0', '')
                    operation = operation.replace('ATTACK_DEF', 'DEF')
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
                    print('Updated multiplier formula to {}'.format(skill.multiplier_formula))
                    updated = True

            # Finally save it if required
            if updated:
                print('Updated skill {}\n'.format(str(skill)))
                if not preview:
                    skill.save()

    if preview:
        print('No changes were saved.')


def parse_monster_data(preview=False):
    monster_table = _get_localvalue_tables(LocalvalueTables.MONSTERS)
    monster_names = get_monster_names_by_id()

    for row in monster_table['rows']:
        master_id = int(row['unit master id'])

        if (master_id < 40000 and row['unit master id'][3] != '2') or (1000101 <= master_id <= 1000300):
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
                    print('Updated {} master ID to {}'.format(monster, master_id))
                    updated = True

                if monster.family_id != monster_family:
                    monster.family_id = monster_family
                    print('Updated {} family ID to {}'.format(monster, monster_family))
                    updated = True

                # Name
                if monster.name != monster_names[master_id]:
                    print("Updated {} name to {}".format(monster, monster_names[master_id]))
                    monster.name = monster_names[master_id]
                    updated = True

                # Archetype
                archetype = row['style type']

                if archetype == 1 and monster.archetype != Monster.TYPE_ATTACK:
                    monster.archetype = Monster.TYPE_ATTACK
                    print('Updated {} archetype to attack'.format(monster))
                    updated = True
                elif archetype == 2 and monster.archetype != Monster.TYPE_DEFENSE:
                    monster.archetype = Monster.TYPE_DEFENSE
                    print("Updated {} archetype to defense".format(monster))
                    updated = True
                elif archetype == 3 and monster.archetype != Monster.TYPE_HP:
                    monster.archetype = Monster.TYPE_HP
                    print("Updated {} archetype to hp".format(monster))
                    updated = True
                elif archetype == 4 and monster.archetype != Monster.TYPE_SUPPORT:
                    monster.archetype = Monster.TYPE_SUPPORT
                    print("Updated {} archetype to support".format(monster))
                    updated = True
                elif archetype == 5 and monster.archetype != Monster.TYPE_MATERIAL:
                    monster.archetype = Monster.TYPE_MATERIAL
                    print("Updated {} archetype to material".format(monster))
                    updated = True

                # Stats
                if monster.base_stars != int(row['base class']):
                    monster.base_stars = int(row['base class'])
                    print('Updated {} base stars to {}'.format(monster, monster.base_stars))
                    updated = True

                if monster.raw_hp != int(row['base con']):
                    monster.raw_hp = int(row['base con'])
                    print('Updated {} raw HP to {}'.format(monster, monster.raw_hp))
                    updated = True

                if monster.raw_attack != int(row['base atk']):
                    monster.raw_attack = int(row['base atk'])
                    print('Updated {} raw attack to {}'.format(monster, monster.raw_attack))
                    updated = True

                if monster.raw_defense != int(row['base def']):
                    monster.raw_defense = int(row['base def'])
                    print('Updated {} raw defense to {}'.format(monster, monster.raw_defense))
                    updated = True

                if monster.resistance != int(row['resistance']):
                    monster.resistance = int(row['resistance'])
                    print('Updated {} resistance to {}'.format(monster, monster.resistance))
                    updated = True

                if monster.accuracy != int(row['accuracy']):
                    monster.accuracy = int(row['accuracy'])
                    print('Updated {} accuracy to {}'.format(monster, monster.accuracy))
                    updated = True

                if monster.speed != int(row['base speed']):
                    monster.speed = int(row['base speed'])
                    print('Updated {} speed to {}'.format(monster, monster.speed))
                    updated = True

                if monster.crit_rate != int(row['critical rate']):
                    monster.crit_rate = int(row['critical rate'])
                    print('Updated {} critical rate to {}'.format(monster, monster.crit_rate))
                    updated = True

                if monster.crit_damage != int(row['critical damage']):
                    monster.crit_damage = int(row['critical damage'])
                    print('Updated {} critical damage to {}'.format(monster, monster.crit_damage))
                    updated = True

                # Awaken materials
                awaken_materials = json.loads(row['awaken materials'])
                essences = [x[0] for x in awaken_materials]  # Extract the essences actually used.

                # Set the essences not used to 0
                if 11001 not in essences and monster.awaken_mats_water_low != 0:
                    monster.awaken_mats_water_low = 0
                    print("Updated {} water low awakening essence to 0.".format(monster))
                    updated = True
                if 12001 not in essences and monster.awaken_mats_water_mid != 0:
                    monster.awaken_mats_water_mid = 0
                    print("Updated {} water mid awakening essence to 0.".format(monster))
                    updated = True
                if 13001 not in essences and monster.awaken_mats_water_high != 0:
                    monster.awaken_mats_water_high = 0
                    print("Updated {} water high awakening essence to 0.".format(monster))
                    updated = True
                if 11002 not in essences and monster.awaken_mats_fire_low != 0:
                    monster.awaken_mats_fire_low = 0
                    print("Updated {} fire low awakening essence to 0.".format(monster))
                    updated = True
                if 12002 not in essences and monster.awaken_mats_fire_mid != 0:
                    monster.awaken_mats_fire_mid = 0
                    print("Updated {} fire mid awakening essence to 0.".format(monster))
                    updated = True
                if 13002 not in essences and monster.awaken_mats_fire_high != 0:
                    monster.awaken_mats_fire_high = 0
                    print("Updated {} fire high awakening essence to 0.".format(monster))
                    updated = True
                if 11003 not in essences and monster.awaken_mats_wind_low != 0:
                    monster.awaken_mats_wind_low = 0
                    print("Updated {} wind low awakening essence to 0.".format(monster))
                    updated = True
                if 12003 not in essences and monster.awaken_mats_wind_mid != 0:
                    monster.awaken_mats_wind_mid = 0
                    print("Updated {} wind mid awakening essence to 0.".format(monster))
                    updated = True
                if 13003 not in essences and monster.awaken_mats_wind_high != 0:
                    monster.awaken_mats_wind_high = 0
                    print("Updated {} wind high awakening essence to 0.".format(monster))
                    updated = True
                if 11004 not in essences and monster.awaken_mats_light_low != 0:
                    monster.awaken_mats_light_low = 0
                    print("Updated {} light low awakening essence to 0.".format(monster))
                    updated = True
                if 12004 not in essences and monster.awaken_mats_light_mid != 0:
                    monster.awaken_mats_light_mid = 0
                    print("Updated {} light mid awakening essence to 0.".format(monster))
                    updated = True
                if 13004 not in essences and monster.awaken_mats_light_high != 0:
                    monster.awaken_mats_light_high = 0
                    print("Updated {} light high awakening essence to 0.".format(monster))
                    updated = True
                if 11005 not in essences and monster.awaken_mats_dark_low != 0:
                    monster.awaken_mats_dark_low = 0
                    print("Updated {} dark low awakening essence to 0.".format(monster))
                    updated = True
                if 12005 not in essences and monster.awaken_mats_dark_mid != 0:
                    monster.awaken_mats_dark_mid = 0
                    print("Updated {} dark mid awakening essence to 0.".format(monster))
                    updated = True
                if 13005 not in essences and monster.awaken_mats_dark_high != 0:
                    monster.awaken_mats_dark_high = 0
                    print("Updated {} dark high awakening essence to 0.".format(monster))
                    updated = True
                if 11006 not in essences and monster.awaken_mats_magic_low != 0:
                    monster.awaken_mats_magic_low = 0
                    print("Updated {} magic low awakening essence to 0.".format(monster))
                    updated = True
                if 12006 not in essences and monster.awaken_mats_magic_mid != 0:
                    monster.awaken_mats_magic_mid = 0
                    print("Updated {} magic mid awakening essence to 0.".format(monster))
                    updated = True
                if 13006 not in essences and monster.awaken_mats_magic_high != 0:
                    monster.awaken_mats_magic_high = 0
                    print("Updated {} magic high awakening essence to 0.".format(monster))
                    updated = True

                # Fill in values for the essences specified
                for essence in awaken_materials:
                    if essence[0] == 11001 and monster.awaken_mats_water_low != essence[1]:
                        monster.awaken_mats_water_low = essence[1]
                        print("Updated {} water low awakening essence to {}".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 12001 and monster.awaken_mats_water_mid != essence[1]:
                        monster.awaken_mats_water_mid = essence[1]
                        print("Updated {} water mid awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 13001 and monster.awaken_mats_water_high != essence[1]:
                        monster.awaken_mats_water_high = essence[1]
                        print("Updated {} water high awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 11002 and monster.awaken_mats_fire_low != essence[1]:
                        monster.awaken_mats_fire_low = essence[1]
                        print("Updated {} fire low awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 12002 and monster.awaken_mats_fire_mid != essence[1]:
                        monster.awaken_mats_fire_mid = essence[1]
                        print("Updated {} fire mid awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 13002 and monster.awaken_mats_fire_high != essence[1]:
                        monster.awaken_mats_fire_high = essence[1]
                        print("Updated {} fire high awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 11003 and monster.awaken_mats_wind_low != essence[1]:
                        monster.awaken_mats_wind_low = essence[1]
                        print("Updated {} wind low awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 12003 and monster.awaken_mats_wind_mid != essence[1]:
                        monster.awaken_mats_wind_mid = essence[1]
                        print("Updated {} wind mid awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 13003 and monster.awaken_mats_wind_high != essence[1]:
                        monster.awaken_mats_wind_high = essence[1]
                        print("Updated {} wind high awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 11004 and monster.awaken_mats_light_low != essence[1]:
                        monster.awaken_mats_light_low = essence[1]
                        print("Updated {} light low awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 12004 and monster.awaken_mats_light_mid != essence[1]:
                        monster.awaken_mats_light_mid = essence[1]
                        print("Updated {} light mid awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 13004 and monster.awaken_mats_light_high != essence[1]:
                        monster.awaken_mats_light_high = essence[1]
                        print("Updated {} light high awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 11005 and monster.awaken_mats_dark_low != essence[1]:
                        monster.awaken_mats_dark_low = essence[1]
                        print("Updated {} dark low awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 12005 and monster.awaken_mats_dark_mid != essence[1]:
                        monster.awaken_mats_dark_mid = essence[1]
                        print("Updated {} dark mid awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 13005 and monster.awaken_mats_dark_high != essence[1]:
                        monster.awaken_mats_dark_high = essence[1]
                        print("Updated {} dark high awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 11006 and monster.awaken_mats_magic_low != essence[1]:
                        monster.awaken_mats_magic_low = essence[1]
                        print("Updated {} magic low awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 12006 and monster.awaken_mats_magic_mid != essence[1]:
                        monster.awaken_mats_magic_mid = essence[1]
                        print("Updated {} magic mid awakening essence to ".format(monster, essence[1]))
                        updated = True
                    elif essence[0] == 13006 and monster.awaken_mats_magic_high != essence[1]:
                        monster.awaken_mats_magic_high = essence[1]
                        print("Updated {} magic high awakening essence to ".format(monster, essence[1]))
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
                        print('Updated {} leader skill to {}'.format(monster, matching_skill))
                        updated = True
                else:
                    if monster.leader_skill is not None:
                        monster.leader_skill = None
                        print('Removed leader skill from {}'.format(monster))
                        updated = True

                # Skills
                existing_skills = monster.skills.all()
                skill_set = Skill.objects.filter(com2us_id__in=json.loads(row['base skill']))

                if set(existing_skills) != set(skill_set):
                    if not preview:
                        monster.skills.clear()
                        monster.skills.add(*skill_set)
                    print("Updated {} skill set".format(monster))
                    # No need for updated = True because .add() immediately takes effect

                # Icon
                icon_nums = json.loads(row['thumbnail'])
                icon_filename = 'unit_icon_{0:04d}_{1}_{2}.png'.format(*icon_nums)
                if monster.image_filename != icon_filename:
                    monster.image_filename = icon_filename
                    print("Updated {} icon filename".format(monster))
                    updated = True

                if updated:
                    print('Updated {}\n'.format(monster))
                    if not preview:
                        monster.save()
    if preview:
        print('No changes were saved.')


def crop_monster_images():
    # If the image is 102x102, we need to crop out the 1px white border.
    for im_path in iglob('herders/static/herders/images/monsters/*.png'):
        im = Image.open(im_path)

        if im.size == (102, 102):
            crop = im.crop((1, 1, 101, 101))
            im.close()
            crop.save(im_path)


class TranslationTables(IntEnum):
    MONSTER_NAME_TABLE = 1
    SKILL_NAME_TABLE = 19
    SKILL_DESCRIPTION_TABLE = 20


def get_monster_names_by_id():
    return _get_translation_tables()[TranslationTables.MONSTER_NAME_TABLE]


def get_skill_names_by_id():
    return _get_translation_tables()[TranslationTables.SKILL_NAME_TABLE]


def get_skill_descs_by_id():
    return _get_translation_tables()[TranslationTables.SKILL_DESCRIPTION_TABLE]


def save_translation_tables():
    tables = _get_translation_tables()
    with open('bestiary/com2us_data/text_eng.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['table_num', 'id', 'text'])
        for table_idx, table in enumerate(tables):
            for key, text in table.items():
                writer.writerow([table_idx, key, text])


def _get_translation_tables():
    raw = ConstBitStream(filename='bestiary/com2us_data/text_eng.dat', offset=0x8 * 8)
    tables = []

    try:
        while True:
            table_len = raw.read('intle:32')
            table = {}

            for _ in range(table_len):
                parsed_id, str_len = raw.readlist('intle:32, intle:32')
                parsed_str = binascii.a2b_hex(raw.read('hex:{}'.format(str_len * 8))[:-4])
                table[parsed_id] = parsed_str.decode("utf-8")

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
    # Unknown table 7 - wizard level related
    # Unknown table 8 - some sort of effect mapping
    SKILL_EFFECTS = 9
    SKILLS = 10
    SUMMON_METHODS = 11
    RUNE_SET_DEFINITIONS = 12
    NPC_ARENA_RIVALS = 13
    ACHIEVEMENTS = 14
    TUTORIALS = 15
    SCENARIO_BOSSES = 16
    SCENARIOS = 17
    CAIROS_BOSSES = 18
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
    SCENARIOS2 = 39
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


def _decrypt_localvalue_dat():
    with open('bestiary/com2us_data/localvalue.dat') as f:
        return decrypt_response(f.read().strip('\0'))


def _get_localvalue_tables(table_id):
    tables = {}
    decrypted_localvalue = _decrypt_localvalue_dat()

    raw = ConstBitStream(decrypted_localvalue)
    raw.read('pad:{}'.format(0x24 * 8))
    num_tables = raw.read('intle:32') - 1
    raw.read('pad:{}'.format(0xc * 8))

    if num_tables > int(max(LocalvalueTables)):
        print('WARNING! Found {} tables in localvalue.dat. There are only {} tables defined!'.format(num_tables, int(max(LocalvalueTables))))

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

    return table_data
