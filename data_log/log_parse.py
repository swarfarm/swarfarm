import datetime

import pytz

from bestiary.models import GameItem, Monster
from herders.models import Summoner
from .models import SummonLog


def parse_summon_unit(summoner, log_data):
    if log_data['response']['unit_list'] is None:
        return

    for x in range(0, len(log_data['response']['unit_list'])):
        log_entry = _parse_common_log_data(SummonLog(), summoner, log_data)

        # Summon method
        if len(log_data['response'].get('item_list', [])) > 0:
            item_info = log_data['response']['item_list'][0]

            log_entry.item = GameItem.objects.get(
                category=item_info['item_master_type'],
                com2us_id=item_info['item_master_id']
            )
        else:
            mode = log_data['request']['mode']
            if mode == 3:
                # Crystal summon
                log_entry.item = GameItem.objects.get(
                    category=GameItem.CATEGORY_CURRENCY,
                    com2us_id=1,
                )
            elif mode == 5:
                # Social summon
                log_entry.item = GameItem.objects.get(
                    category=GameItem.CATEGORY_CURRENCY,
                    com2us_id=2,
                )

        # Monster
        monster_data = log_data['response']['unit_list'][x]
        log_entry.monster = Monster.objects.get(com2us_id=monster_data.get('unit_master_id'))
        log_entry.grade = monster_data['class']
        log_entry.level = monster_data['unit_level']
        log_entry.save()


_timezone_server_map = {
    'America/Los_Angeles': Summoner.SERVER_GLOBAL,
    'Europe/Berlin': Summoner.SERVER_EUROPE,
    'Asia/Seoul': Summoner.SERVER_KOREA,
    'Asia/Shanghai': Summoner.SERVER_ASIA,
}


def _parse_common_log_data(log, summoner, log_data):
    log.wizard_id = log_data['request']['wizard_id']
    log.summoner = summoner
    log.server = _timezone_server_map.get(log_data['response']['tzone'])
    log.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))

    return log

accepted_api_params = {
    'SummonUnit': {
        'request': [
            'wizard_id',
            'command',
            'mode',
        ],
        'response': [
            'tzone',
            'tvalue',
            'unit_list',
            'item_list',
        ],
    },
    'DoRandomWishItem': {
        'request': [
            'wizard_id',
            'command',
        ],
        'response': [
            'tzone',
            'tvalue',
            'wish_info',
            'unit_info',
            'rune',
        ]
    },
    'BattleDungeonResult': {
        'request': [
            'wizard_id',
            'command',
            'dungeon_id',
            'stage_id',
            'clear_time',
            'win_lose',
        ],
        'response': [
            'tzone',
            'tvalue',
            'unit_list',
            'reward',
            'instance_info',
        ]
    },
    'BattleScenarioStart': {
        'request': [
            'wizard_id',
            'command',
            'region_id',
            'stage_no',
            'difficulty',
        ],
        'response': [
            'battle_key'
        ]
    },
    'BattleScenarioResult': {
        'request': [
            'wizard_id',
            'command',
            'battle_key',
            'win_lose',
            'clear_time',
        ],
        'response': [
            'tzone',
            'tvalue',
            'reward',
        ]
    },
    'BattleWorldBossStart': {
        'request': [
            'wizard_id',
            'command',
        ],
        'response': [
            'tzone',
            'tvalue',
            'battle_key',
            'worldboss_battle_result',
            'reward_info',
        ]
    },
    'BattleWorldBossResult': {
        'request': [
            'wizard_id',
            'command',
            'battle_key',
        ],
        'response': [
            'reward',
        ]
    },
    'BattleRiftDungeonResult': {
        'request': [
            'wizard_id',
            'command',
            'battle_result',
            'dungeon_id'
        ],
        'response': [
            'tvalue',
            'tzone',
            'item_list',
            'rift_dungeon_box_id',
            'total_damage',
        ]
    },
    'BattleRiftOfWorldsRaidStart': {
        'request': [
            'wizard_id',
            'command',
            'battle_key',
        ],
        'response': [
            'tzone',
            'tvalue',
            'battle_info',
        ]
    },
    'BattleRiftOfWorldsRaidResult': {
        'request': [
            'wizard_id',
            'command',
            'battle_key',
            'clear_time',
            'win_lose',
            'user_status_list',
        ],
        'response': [
            'tzone',
            'tvalue',
            'battle_reward_list',
            'reward',
        ]
    },
    'BuyShopItem': {
        'request': [
            'wizard_id',
            'command',
            'item_id',
        ],
        'response': [
            'tzone',
            'tvalue',
            'reward',
            'view_item_list',
        ]
    },
    'GetBlackMarketList': {
        'request': [
            'wizard_id',
            'command',
        ],
        'response': [
            'tzone',
            'tvalue',
            'market_info',
            'market_list',
        ],
    },
}

log_parse_dispatcher = {
    'SummonUnit': parse_summon_unit,
    # 'DoRandomWishItem': parse_do_random_wish_item,
    # 'BattleDungeonResult': parse_battle_dungeon_result,
    # 'BattleScenarioStart': parse_battle_scenario_start,
    # 'BattleScenarioResult': parse_battle_scenario_result,
    # 'BattleWorldBossStart': parse_battle_worldboss_start,
    # 'BattleWorldBossResult': parse_battle_worldboss_result,
    # 'BattleRiftDungeonResult': parse_battle_rift_dungeon_result,
    # 'BattleRiftOfWorldsRaidStart': parse_battle_rift_of_worlds_raid_start,
    # 'BattleRiftOfWorldsRaidResult': parse_battle_rift_of_worlds_raid_end,
    # 'BuyShopItem': parse_buy_shop_item,
    # 'GetBlackMarketList': parse_get_black_market_list,
}
