import datetime
import json
import pytz

from django.core.exceptions import ValidationError
from django.core.mail import mail_admins

from herders.models import Summoner

from .models import *
from .com2us_parser import get_monster_from_id
from .com2us_mapping import inventory_type_map, timezone_server_map, summon_source_map, scenario_difficulty_map, \
    rune_stat_type_map, rune_set_map, drop_essence_map, drop_craft_map, drop_currency_map, \
    craft_type_map, craft_quality_map, secret_dungeon_map


def _get_summoner(wizard_id):
    return Summoner.objects.filter(com2us_id=wizard_id).order_by('-user__last_login').first()


def parse_summon_unit(log_data):
    if log_data['response']['unit_list'] is None:
        return

    for x in range(0, len(log_data['response']['unit_list'])):
        log_entry = SummonLog()

        log_entry.wizard_id = log_data['request']['wizard_id']
        log_entry.summoner = _get_summoner(log_entry.wizard_id)
        log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))
        log_entry.server = timezone_server_map.get(log_data['response']['tzone'])

        # Summon method
        if log_data['response']['item_info']:
            log_entry.summon_method = summon_source_map[log_data['response']['item_info']['item_master_id']]
        else:
            mode = log_data['request']['mode']
            if mode == 3:
                log_entry.summon_method = SummonLog.SUMMON_MYSTICAL
            elif mode == 5:
                log_entry.summon_method = SummonLog.SOCIAL_POINTS

        # Monster
        summoned_mon = MonsterDrop()
        monster_data = log_data['response']['unit_list'][x]
        summoned_mon.monster = get_monster_from_id(monster_data.get('unit_master_id'))
        summoned_mon.grade = monster_data['class']
        summoned_mon.level = monster_data['unit_level']

        summoned_mon.save()
        log_entry.monster = summoned_mon
        log_entry.save()


def parse_do_random_wish_item(log_data):
    log_entry = WishLog()

    log_entry.wizard_id = log_data['request']['wizard_id']
    log_entry.summoner = _get_summoner(log_entry.wizard_id)
    log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))
    log_entry.server = timezone_server_map.get(log_data['response']['tzone'])

    wish_info = log_data['response']['wish_info']
    log_entry.wish_id = wish_info['wish_id']
    log_entry.wish_sequence = wish_info['wish_sequence']
    log_entry.crystal_used = wish_info['cash_used']
    log_entry.save()

    drop_type = wish_info['item_master_type']
    drop_master_id = wish_info['item_master_id']

    wish_drop = None
    if drop_type == inventory_type_map['monster'] or drop_type == inventory_type_map['rainbowmon']:
        unit_info = log_data['response']['unit_info']
        wish_drop = WishMonsterDrop()
        wish_drop.monster = get_monster_from_id(unit_info['unit_master_id'])
        wish_drop.grade = unit_info['class']
        wish_drop.level = unit_info['unit_level']
    elif drop_type == inventory_type_map['currency']:
        wish_drop = WishItemDrop()
        wish_drop.item = drop_currency_map[drop_master_id]
        wish_drop.quantity = wish_info['amount']
    elif drop_type == inventory_type_map['scroll']:
        wish_drop = WishItemDrop()
        wish_drop.item = summon_source_map[drop_master_id]
        wish_drop.quantity = wish_info['amount']
    elif drop_type == inventory_type_map['rune']:
        rune_data = log_data['response']['rune']
        wish_drop = _parse_rune_log(rune_data, WishRuneDrop())
    else:
        mail_admins(
            subject='Unknown wish drop item type {}'.format(drop_type),
            message=json.dumps(log_data),
            fail_silently=True,
        )

    if wish_drop is not None:
        wish_drop.log = log_entry
        wish_drop.save()


def parse_battle_dungeon_result(log_data):
    # Check if battle key already exists. If so, skip it.
    battle_key = log_data['response'].get('battle_key')
    dungeon_id = log_data['request'].get('dungeon_id')

    if battle_key and RunLog.objects.filter(battle_key=battle_key).exists():
        return

    # Don't log HoH dungeons, which have IDs starting from 10000 and increments by 1 each new HoH.
    if 10000 <= dungeon_id < 11000:
        return

    log_entry = RunLog()

    # Common results
    log_entry.wizard_id = log_data['request']['wizard_id']
    log_entry.summoner = _get_summoner(log_entry.wizard_id)
    log_entry.success = log_data['request']['win_lose'] == 1
    log_entry.clear_time = datetime.timedelta(milliseconds=log_data['request']['clear_time'])
    log_entry.server = timezone_server_map.get(log_data['response']['tzone'])
    log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))

    try:
        log_entry.dungeon = Dungeon.objects.get(pk=dungeon_id)
    except Dungeon.DoesNotExist:
        log_entry.dungeon = Dungeon.objects.create(pk=dungeon_id, name='UNKNOWN DUNGEON')

    log_entry.stage = log_data['request']['stage_id']
    log_entry = _parse_battle_reward(log_entry, log_data['response'].get('reward'), log_data['response'].get('instance_info'))
    log_entry.save()


def parse_battle_scenario_start(log_data):
    # Check if battle key already exists. If so, skip it.
    battle_key = log_data['response'].get('battle_key')

    if battle_key and RunLog.objects.filter(battle_key=battle_key).exists():
        return

    log_entry = RunLog()

    # Common results
    log_entry.wizard_id = log_data['request']['wizard_id']
    log_entry.battle_key = battle_key
    log_entry.summoner = _get_summoner(log_entry.wizard_id)

    try:
        log_entry.dungeon = Dungeon.objects.get(pk=log_data['request']['region_id'])
    except Dungeon.DoesNotExist:
        log_entry.dungeon = Dungeon.objects.create(pk=log_data['request']['region_id'], name='UNKNOWN SCENARIO')

    log_entry.stage = log_data['request']['stage_no']
    log_entry.difficulty = scenario_difficulty_map[log_data['request']['difficulty']]
    log_entry.save()

    return log_entry


def parse_battle_scenario_result(log_data):
    # Check if it's a scenario from an old plugin that includes all the data
    if 'scenario_info' in log_data:
        log_entry = parse_battle_scenario_start(log_data)
    else:
        try:
            log_entry = RunLog.objects.get(wizard_id=log_data['request']['wizard_id'], battle_key=log_data['request']['battle_key'])
        except (RunLog.DoesNotExist, RunLog.MultipleObjectsReturned):
            return

    log_entry.battle_key = None  # Remove battle key now that it has been processed.
    log_entry.server = timezone_server_map.get(log_data['response']['tzone'])
    log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))
    log_entry.success = log_data['request']['win_lose'] == 1
    log_entry.clear_time = datetime.timedelta(milliseconds=log_data['request']['clear_time'])
    log_entry = _parse_battle_reward(log_entry, log_data['response'].get('reward'))
    log_entry.save()


def parse_battle_worldboss_start(log_data):
    # Check if battle key already exists. If so, skip it.
    battle_key = log_data['response'].get('battle_key')

    if battle_key and RunLog.objects.filter(battle_key=battle_key).exists():
        return

    log_entry = WorldBossLog()

    # Common results
    log_entry.wizard_id = log_data['request']['wizard_id']
    log_entry.summoner = _get_summoner(log_entry.wizard_id)
    log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))

    # World Boss Specific
    log_entry.battle_key = battle_key
    log_entry.grade = log_data['response']['reward_info']['box_id']
    log_entry.damage = log_data['response']['worldboss_battle_result']['total_damage']
    log_entry.battle_points = log_data['response']['worldboss_battle_result']['total_battle_point']
    log_entry.bonus_battle_points = log_data['response']['worldboss_battle_result']['bonus_battle_point']
    log_entry.avg_monster_level = log_data['response']['worldboss_battle_result']['unit_avg_level']
    log_entry.monster_count = log_data['response']['worldboss_battle_result']['unit_count']
    log_entry.save()

    # Parse the item drops (not runes)
    for item in log_data['response']['reward_info']['reward_list']:
        log_drop = None
        if item['item_master_type'] == inventory_type_map['essences']:
            log_drop = WorldBossItemDrop()
            log_drop.log = log_entry
            log_drop.item = drop_essence_map[item['item_master_id']]
            log_drop.quantity = item['amount']
        elif item['item_master_type'] == inventory_type_map['currency']:
            log_drop = WorldBossItemDrop()
            log_drop.log = log_entry
            log_drop.item = drop_currency_map[item['item_master_id']]
            log_drop.quantity = item['amount']
        elif item['item_master_type'] == inventory_type_map['scroll']:
            log_drop = WorldBossItemDrop()
            log_drop.log = log_entry
            log_drop.item = summon_source_map[item['item_master_id']]
            log_drop.quantity = item['amount']
        elif item['item_master_type'] == inventory_type_map['monster']:
            log_drop = WorldBossMonsterDrop()
            log_drop.log = log_entry
            log_drop.monster = Monster.objects.get(com2us_id=int(item['item_master_id']))
            log_drop.level = int(item['unit_level'])
            log_drop.grade = int(item['unit_class'])
        elif item['item_master_type'] == inventory_type_map['rune']:
            # Will be parsed in the worldboss result request
            pass
        else:
            mail_admins(
                subject='Unknown world boss drop item type {}'.format(item['item_master_type']),
                message=json.dumps(log_data),
                fail_silently=True,
            )
        if log_drop:
            log_drop.save()


def parse_battle_worldboss_result(log_data):
    try:
        log_entry = WorldBossLog.objects.get(wizard_id=log_data['request']['wizard_id'], battle_key=log_data['request']['battle_key'])
    except (WorldBossLog.DoesNotExist, WorldBossLog.MultipleObjectsReturned):
        return

    log_entry.battle_key = None
    log_entry.save()

    # Process runes and/or monsters
    for reward_type, contents in log_data['response']['reward']['crate'].items():
        if reward_type == 'runes':
            for rune_data in contents:
                rune_drop = WorldBossRuneDrop()
                rune_drop.log = log_entry
                rune_drop = _parse_rune_log(rune_data, rune_drop)
                rune_drop.save()
        elif reward_type in ['material', 'random_scroll', 'unit_infos']:
            # These reward types have already been accounted for in parse_battle_worldboss_start
            pass
        else:
            mail_admins(
                subject='Unknown world boss reward {}'.format(reward_type),
                message=json.dumps(log_data),
                fail_silently=True,
            )


def parse_battle_rift_dungeon_result(log_data):
    log_entry = RiftDungeonLog()

    # Common results
    log_entry.wizard_id = log_data['request']['wizard_id']
    log_entry.summoner = _get_summoner(log_entry.wizard_id)
    log_entry.server = timezone_server_map.get(log_data['response']['tzone'])
    log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))

    # Raid specific results
    log_entry.dungeon = log_data['request']['dungeon_id']
    log_entry.success = log_data['request']['battle_result'] == 1
    log_entry.grade = log_data['response']['rift_dungeon_box_id']
    log_entry.total_damage = log_data['response']['total_damage']

    try:
        log_entry.full_clean()
    except ValidationError:
        return

    log_entry.save()

    # Item drops
    if log_data['response']['item_list']:
        for drop in log_data['response']['item_list']:
            if int(drop['type']) == 6:
                # Mana
                log_entry.mana = drop['quantity']
                log_entry.save()
            else:
                rift_drop = None

                if int(drop['type']) == inventory_type_map['craft_stuff']:
                    rift_drop = RiftDungeonItemDrop()
                    rift_drop.item = drop_craft_map[int(drop['id'])]
                    rift_drop.quantity = drop['quantity']
                elif int(drop['type']) == inventory_type_map['rune']:
                    rift_drop = _parse_rune_log(drop['info'], RiftDungeonRuneDrop())
                else:
                    mail_admins(
                        subject='Unparsed elemental raid drop item type {}'.format(drop['item_master_type']),
                        message=json.dumps(log_data),
                        fail_silently=True,
                    )
                if rift_drop:
                    rift_drop.log = log_entry
                    rift_drop.save()

    # Monster drops
    if log_data['response']['unit_list']:
        for monster_data in log_data['response']['unit_list']:
            monster_drop = RiftDungeonMonsterDrop()
            monster_drop.log = log_entry
            monster_drop.monster = get_monster_from_id(monster_data.get('unit_master_id'))
            monster_drop.grade = monster_data['class']
            monster_drop.level = monster_data['unit_level']
            monster_drop.save()


def parse_battle_rift_of_worlds_raid_start(log_data):
    # Check if battle key already exists. If so, skip it.
    battle_key = log_data['request'].get('battle_key')

    if battle_key and RiftRaidLog.objects.filter(battle_key=battle_key).exists():
        return

    log_entry = RiftRaidLog()

    # Common log info
    log_entry.wizard_id = log_data['request']['wizard_id']
    log_entry.battle_key = battle_key
    log_entry.summoner = _get_summoner(log_entry.wizard_id)

    # Raid info
    log_entry.raid = log_data['response']['battle_info']['raid_id']
    log_entry.action_item = log_data['response']['battle_info']['action_item_id']
    log_entry.difficulty = log_data['response']['battle_info']['stage_id']

    log_entry.save()


def parse_battle_rift_of_worlds_raid_end(log_data):
    wizard_id = log_data['request']['wizard_id']
    battle_key = log_data['request']['battle_key']

    try:
        log_entry = RiftRaidLog.objects.get(wizard_id=wizard_id, battle_key=log_data['request']['battle_key'])
    except (RunLog.DoesNotExist, RunLog.MultipleObjectsReturned):
        return

    log_entry.server = timezone_server_map.get(log_data['response']['tzone'])
    log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))

    user_status = None

    # Raid results contains the data for all 3 participants. Find the one for this user.
    for status in log_data['request']['user_status_list']:
        if status['wizard_id'] == wizard_id:
            user_status = status
            break

    log_entry.battle_key = None
    log_entry.success = log_data['request']['win_lose'] == 1
    log_entry.contribution = user_status['damage']
    log_entry.save()

    # Parse rewards
    # We parse all 3 drops for all participants, but double-check that it hasn't been logged already by another user.
    # If it has, we reassign it to this log instead.
    for drop_info in log_data['response']['battle_reward_list']:
        drop_wizard_id = drop_info['wizard_id']

        for drop_item_info in drop_info['reward_list']:
            raid_drop = None
            created = None

            if drop_item_info['item_master_type'] == inventory_type_map['monster']:
                raid_drop, created = RiftRaidMonsterDrop.objects.get_or_create(
                    battle_key=battle_key, wizard_id=drop_wizard_id,
                    defaults={
                        'log': log_entry,
                        'monster': get_monster_from_id(drop_item_info['item_master_id']),
                        'grade': drop_item_info['unit_class'],
                        'level': drop_item_info['unit_level'],
                    }
                )
            elif drop_item_info['item_master_type'] == inventory_type_map['currency']:
                raid_drop, created = RiftRaidItemDrop.objects.get_or_create(
                    battle_key=battle_key, wizard_id=drop_wizard_id,
                    defaults={
                        'log': log_entry,
                        'item': drop_currency_map[drop_item_info['item_master_id']],
                        'quantity': drop_item_info['item_quantity']
                    }
                )
            elif drop_item_info['item_master_type'] == inventory_type_map['scroll']:
                raid_drop = RiftRaidItemDrop.objects.get_or_create(
                    battle_key=battle_key, wizard_id=drop_wizard_id,
                    defaults={
                        'log': log_entry,
                        'item': summon_source_map[drop_item_info['item_master_id']],
                        'quantity': drop_item_info['item_quantity']
                    }
                )
            elif drop_item_info['item_master_type'] == inventory_type_map['rune_craft']:
                craft_type_id = str(drop_item_info['runecraft_item_id'])
                quality = int(craft_type_id[-1:])
                stat = int(craft_type_id[-4:-2])
                rune_set = int(craft_type_id[:-4])

                raid_drop = RiftRaidRuneCraftDrop.objects.get_or_create(
                    battle_key=battle_key, wizard_id=drop_wizard_id,
                    defaults={
                        'log': log_entry,
                        'type': craft_type_map[drop_item_info['runecraft_type']],
                        'quality': craft_quality_map[quality],
                        'rune': rune_set_map[rune_set],
                        'stat': rune_stat_type_map[stat],
                    }
                )
            else:
                mail_admins(
                    subject='Unknown raid drop item type {}'.format(drop_item_info['item_master_type']),
                    message=json.dumps(log_data),
                    fail_silently=True,
                )

            # Check if the reported of this log owns the item
            if created is False and log_entry.wizard_id == drop_wizard_id:
                # Reassign ownership to this log
                raid_drop.log = log_entry
                raid_drop.save()


def parse_buy_shop_item(log_data):
    item_id = str(log_data['request'].get('item_id'))
    if item_id and item_id[:3] == '140' \
            and 'reward' in log_data['response'] \
            and 'crate' in log_data['response']['reward'] \
            and 'runes' in log_data['response']['reward']['crate']:
        log_entry = RuneCraftLog()

        # Common results
        log_entry.wizard_id = log_data['request']['wizard_id']
        log_entry.summoner = _get_summoner(log_entry.wizard_id)
        log_entry.server = timezone_server_map.get(log_data['response']['tzone'])
        log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))

        # RuneCraft specific
        log_entry.craft_level = int(item_id[3]) - 1
        log_entry.save()

        # Parse and save each rune
        # Right now runes is always a 1 element array. Doing it this way in case that changes later.
        for rune_data in log_data['response']['reward']['crate']['runes']:
            rune = RuneCraft()
            rune.log = log_entry
            rune = _parse_rune_log(rune_data, rune)
            rune.save()


def parse_get_black_market_list(log_data):
    if log_data['response'].get('market_list') is None or log_data['response'].get('market_info') is None:
        return

    # Only log real refreshes where the remaining time is 1hr.
    if log_data['response']['market_info']['update_remained'] == 3600:
        log_entry = ShopRefreshLog()
        log_entry.wizard_id = log_data['request']['wizard_id']
        log_entry.summoner = _get_summoner(log_entry.wizard_id)
        log_entry.server = timezone_server_map.get(log_data['response']['tzone'])
        log_entry.timestamp = datetime.datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))

        # ShopRefresh specific
        log_entry.slots_available = log_data['response']['market_info']['open_slots']
        log_entry.save()

        # Parse all the items available in the refresh
        for sale_item in log_data['response']['market_list']:
            sale_entry = None
            if sale_item['item_master_type'] == inventory_type_map['monster']:
                sale_entry = ShopRefreshMonster()
                sale_entry.log = log_entry
                sale_entry.cost = sale_item['buy_mana']
                sale_entry.monster = get_monster_from_id(sale_item['item_master_id'])
                sale_entry.grade = sale_item['class']
                sale_entry.level = 1
            elif sale_item['item_master_type'] == inventory_type_map['scroll']:
                sale_entry = ShopRefreshItem()
                sale_entry.log = log_entry
                sale_entry.cost = sale_item['buy_mana']
                sale_entry.item = summon_source_map[sale_item['item_master_id']]
                sale_entry.quantity = sale_item['amount']
            elif sale_item['item_master_type'] == inventory_type_map['rune']:
                sale_entry = ShopRefreshRune()
                sale_entry.log = log_entry
                sale_entry.cost = sale_item['buy_mana']
                sale_entry = _parse_rune_log(sale_item['runes'][0], sale_entry)
            else:
                mail_admins(
                    subject='Unknown shop item type {}'.format(sale_item['item_master_type']),
                    message=json.dumps(log_data),
                    fail_silently=True,
                )

            if sale_entry:
                sale_entry.save()


def _parse_rune_log(rune_data, rune_drop):
    rune_drop.type = rune_set_map.get(rune_data.get('set_id'))
    rune_drop.value = rune_data.get('sell_value')
    rune_drop.slot = rune_data.get('slot_no')
    rune_drop.stars = rune_data.get('class')

    main_stat = rune_data.get('pri_eff')
    if main_stat:
        rune_drop.main_stat = rune_stat_type_map.get(main_stat[0])
        rune_drop.main_stat_value = main_stat[1]

    innate_stat = rune_data.get('prefix_eff')
    if innate_stat:
        rune_drop.innate_stat = rune_stat_type_map.get(innate_stat[0])
        rune_drop.innate_stat_value = innate_stat[1]

    substats = rune_data.get('sec_eff', [])
    if len(substats) >= 1:
        rune_drop.substat_1 = rune_stat_type_map.get(substats[0][0])
        rune_drop.substat_1_value = substats[0][1]

    if len(substats) >= 2:
        rune_drop.substat_2 = rune_stat_type_map.get(substats[1][0])
        rune_drop.substat_2_value = substats[1][1]

    if len(substats) >= 3:
        rune_drop.substat_3 = rune_stat_type_map.get(substats[2][0])
        rune_drop.substat_3_value = substats[2][1]

    if len(substats) >= 4:
        rune_drop.substat_4 = rune_stat_type_map.get(substats[3][0])
        rune_drop.substat_4_value = substats[3][1]

    return rune_drop


def _parse_battle_reward(log_entry, reward, instance_info=None):
    # Rewards
    if reward:
        log_entry.mana = reward.get('mana', 0)
        log_entry.energy = reward.get('energy', 0)
        log_entry.crystal = reward.get('crystal', 0)

        # Determine reward object
        if 'crate' in reward:
            crate = reward['crate']

            if 'mana' in crate:
                log_entry.mana += crate['mana']

            if 'energy' in crate:
                log_entry.energy += crate['energy']

            if 'crystal' in crate:
                log_entry.crystal += crate['crystal']

            if 'random_scroll' in crate:
                log_entry.drop_type = summon_source_map[crate['random_scroll']['item_master_id']]
                log_entry.drop_quantity = crate['random_scroll']['item_quantity']

            if 'unit_info' in crate:
                log_entry.drop_type = RunLog.DROP_MONSTER
                log_entry.drop_quantity = 1

                drop_mon = MonsterDrop()
                drop_mon.monster = get_monster_from_id(crate['unit_info']['unit_master_id'])
                drop_mon.grade = crate['unit_info']['class']
                drop_mon.level = crate['unit_info']['unit_level']

                drop_mon.save()
                log_entry.drop_monster = drop_mon

            if 'rune' in crate:
                log_entry.drop_type = RunLog.DROP_RUNE
                log_entry.drop_quantity = 1
                drop_rune = _parse_rune_log(crate['rune'], RuneDrop())
                drop_rune.save()
                log_entry.drop_rune = drop_rune

            if 'material' in crate:
                log_entry.drop_type = drop_essence_map[crate['material']['item_master_id']]
                log_entry.drop_quantity = crate['material']['item_quantity']

            if 'costume_point' in crate:
                log_entry.drop_type = RunLog.DROP_COSTUME_POINT
                log_entry.drop_quantity = crate['costume_point']

            if 'rune_upgrade_stone' in crate:
                log_entry.drop_type = RunLog.DROP_UPGRADE_STONE
                log_entry.drop_quantity = crate['rune_upgrade_stone']['item_quantity']

            if 'summon_pieces' in crate:
                log_entry.drop_type = RunLog.DROP_SUMMON_PIECES
                log_entry.drop_quantity = crate['summon_pieces']['item_quantity']

                drop_mon = MonsterDrop()
                drop_mon.monster = get_monster_from_id(crate['summon_pieces']['item_master_id'])
                drop_mon.grade = drop_mon.monster.base_stars
                drop_mon.level = 1
                drop_mon.save()
                log_entry.drop_monster = drop_mon

            if 'craft_stuff' in crate:
                log_entry.drop_type = drop_craft_map[crate['craft_stuff']['item_master_id']]
                log_entry.drop_quantity = crate['craft_stuff']['item_quantity']

            if 'event_item' in crate:
                log_entry.drop_type = RunLog.DROP_EVENT_ITEM
                log_entry.drop_quantity = crate['event_item']['item_quantity']
    else:
        # Failed runs with 0 enemy kills have no reward crate
        log_entry.mana = 0
        log_entry.energy = 0
        log_entry.crystal = 0

    # Secret Dungeons
    if instance_info:
        log_entry.drop_type = RunLog.DROP_SECRET_DUNGEON
        if instance_info['instance_id'] in secret_dungeon_map:
            drop_mon = MonsterDrop()
            drop_mon.monster = get_monster_from_id(secret_dungeon_map[instance_info['instance_id']])
            drop_mon.grade = drop_mon.monster.base_stars
            drop_mon.level = 1
            drop_mon.save()
            log_entry.drop_monster = drop_mon

    return log_entry


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
            'item_info',
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
            'unit_list',
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
            'reward'
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
    'DoRandomWishItem': parse_do_random_wish_item,
    'BattleDungeonResult': parse_battle_dungeon_result,
    'BattleScenarioStart': parse_battle_scenario_start,
    'BattleScenarioResult': parse_battle_scenario_result,
    'BattleWorldBossStart': parse_battle_worldboss_start,
    'BattleWorldBossResult': parse_battle_worldboss_result,
    'BattleRiftDungeonResult': parse_battle_rift_dungeon_result,
    'BattleRiftOfWorldsRaidStart': parse_battle_rift_of_worlds_raid_start,
    'BattleRiftOfWorldsRaidResult': parse_battle_rift_of_worlds_raid_end,
    'BuyShopItem': parse_buy_shop_item,
    'GetBlackMarketList': parse_get_black_market_list,
}
