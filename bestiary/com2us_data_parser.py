import base64
import binascii
import csv
import json
import zlib
from enum import IntEnum

from Crypto.Cipher import AES
from bitstring import ConstBitStream, ReadError
from django.conf import settings

from bestiary.com2us_mapping import *
from .models import Dungeon, SecretDungeon, Level


def _decrypt(msg):
    obj = AES.new(
        bytes(settings.SUMMONERS_WAR_SECRET_KEY, encoding='latin-1'),
        AES.MODE_CBC,
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    )
    decrypted = obj.decrypt(msg)
    return decrypted[:-decrypted[-1]]


def decrypt_response(msg):
    decoded = base64.b64decode(msg)
    decrypted = _decrypt(decoded)
    decompressed = zlib.decompress(decrypted)
    return decompressed


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
