import base64
import binascii
import json
import zlib

from Crypto.Cipher import AES
from bitstring import ConstBitStream, ReadError
from django.conf import settings


def _decrypt(msg):
    obj = AES.new(
        bytes(settings.SUMMONERS_WAR_SECRET_KEY, encoding='latin-1'),
        AES.MODE_CBC,
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    )
    decrypted = obj.decrypt(base64.b64decode(msg))
    return decrypted[:-decrypted[-1]]


def decrypt_request(msg):
    return _decrypt(msg)


def decrypt_response(msg):
    # Responses are compressed with zlib
    return zlib.decompress(_decrypt(msg))


def try_json(value):
    try:
        return json.loads(value)
    except json.decoder.JSONDecodeError:
        return value


class _TableDefs:
    # Known table definitions
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


class _LocalValueData:
    filename = 'bestiary/parse/com2us_data/localvalue.dat'
    _tables = {}
    _num_tables = None
    _table_offsets = {}
    _decrypted_data = None

    # Byte offsets for key locations in file
    TABLE_COUNT_POS = 0x24 * 8
    TABLE_DEFS_POS = 0x34 * 8
    TABLE_START_POS = None  # Must be processed after loading table definitions

    def __getattr__(self, item):
        # Allows access to tables by name instead of index.
        value = getattr(_TableDefs, item)
        return self[value]

    def __getitem__(self, key):
        if key not in _LocalValueData._tables:
            _LocalValueData._tables[key] = _LocalValueData._get_table(key)

        return _LocalValueData._tables[key]

    def __len__(self):
        return _LocalValueData._get_num_tables()

    @staticmethod
    def _get_num_tables():
        if _LocalValueData._num_tables is None:
            file = _LocalValueData._get_decrypted_data()
            file.pos = _LocalValueData.TABLE_COUNT_POS
            _LocalValueData._num_tables = file.read(f'intle:32') - 1

        return _LocalValueData._num_tables

    @staticmethod
    def _get_table(key):
        if key not in _LocalValueData._tables:
            f = _LocalValueData._get_decrypted_data()
            start, end = _LocalValueData._get_table_offsets(key)

            # Set bitstream to start of table data
            f.pos = _LocalValueData.TABLE_START_POS + start * 8

            # Read in the table. It's a tab-delimited text format.
            entire_table = f.read(f'bytes:{end - start}').decode('utf-8').strip().split('\r\n')
            column_headers = entire_table[0].split('\t')

            # Store table data
            _LocalValueData._tables[key] = {}
            for row_string in entire_table[1:]:
                row = row_string.split('\t')
                row_key = json.loads(row[0])
                _LocalValueData._tables[key][row_key] = {
                    column_headers[col]: try_json(value) for col, value in enumerate(row)
                    # column_headers[col]: json.loads(value) for col, value in enumerate(row)
                }

        return _LocalValueData._tables[key]

    @staticmethod
    def _get_table_offsets(key):
        if not _LocalValueData._table_offsets:
            # Store all table offsets
            f = _LocalValueData._get_decrypted_data()
            f.pos = _LocalValueData.TABLE_DEFS_POS

            for x in range(_LocalValueData._get_num_tables()):
                table_num, start, end = f.readlist(['intle:32'] * 3)
                _LocalValueData._table_offsets[table_num] = (start, end)

            _LocalValueData.TABLE_START_POS = f.pos

        return _LocalValueData._table_offsets[key]

    @staticmethod
    def _get_decrypted_data():
        if _LocalValueData._decrypted_data is None:
            with open(_LocalValueData.filename) as f:
                _LocalValueData._decrypted_data = decrypt_response(f.read().strip('\0'))

        return ConstBitStream(_LocalValueData._decrypted_data)



class _Strings:
    filename = 'bestiary/parse/com2us_data/text_eng.dat'
    version = None
    _tables = []
    _num_tables = 0

    def __init__(self, *args, **kwargs):
        if not _Strings._tables:
            f = _Strings._get_file()

            _Strings.version = f.read('intle:32')

            try:
                while True:
                    table_len = f.read('intle:32')
                    tbl = {}

                    for _ in range(table_len):
                        str_id, str_len = f.readlist('intle:32, intle:32')
                        parsed_str = binascii.a2b_hex(f.read('hex:{}'.format(str_len * 8))[:-4])
                        tbl[str_id] = parsed_str.decode("utf-8").strip()

                    _Strings._tables.append(tbl)

            except ReadError:
                # EOF
                pass

    def __getitem__(self, key):
        return _Strings._tables[key]

    def __len__(self):
        return _Strings._num_tables

    @staticmethod
    def _get_file():
        return ConstBitStream(filename=_Strings.filename)

    # Known table definitions
    ISLAND_NAMES = 1
    MONSTER_NAMES = 2
    SUMMON_METHODS = 10
    SKILL_NAMES = 20
    SKILL_DESCRIPTIONS = 21
    AWAKEN_STAT_BONUSES = 24
    LEADER_SKILL_DESCRIPTIONS = 25
    WORLD_MAP_DUNGEON_NAMES = 29
    CAIROS_DUNGEON_NAMES = 30


tables = _LocalValueData()
strings = _Strings()
