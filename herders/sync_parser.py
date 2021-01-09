from django.utils.timezone import get_current_timezone
from dateutil.parser import *

from .tasks import com2us_data_import, swex_sync_monster_shrine
from .profile_parser import validate_sw_json, default_import_options, parse_rune_data, parse_rune_craft_data, parse_artifact_data, parse_artifact_craft_data
from .models import MaterialStorage, MonsterPiece, MonsterInstance, MonsterShrineStorage
from bestiary.models import GameItem, Rune, Monster


def sync_profile(summoner, log_data):
    schema_errors, validation_errors = validate_sw_json(
        log_data['response'], summoner)
    if schema_errors or validation_errors:
        return

    import_options = summoner.preferences.get(
        'import_options', default_import_options)
    com2us_data_import.delay(log_data['response'], summoner.pk, import_options)


def sync_monster_shrine(summoner, log_data, full_sync=True):
    if full_sync:
        swex_sync_monster_shrine.delay(log_data['response'], summoner.pk)
    else:
        for monster in log_data:
            try:
                mon = MonsterShrineStorage.objects.get(
                    owner=summoner, item__com2us_id=monster['unit_master_id'])
                mon.quantity = monster['quantity']
            except MonsterShrineStorage.DoesNotExist:
                base = Monster.objects.get(com2us_id=monster['unit_master_id'])
                mon = MonsterShrineStorage(
                    owner=summoner,
                    item=base,
                    quantity=monster['quantity'],
                )
            mon.save()


def _create_new_monster(unit_info, summoner):
    com2us_id = unit_info.get('unit_id')
    monster_type_id = str(unit_info.get('unit_master_id'))
    mon = MonsterInstance()
    mon.owner = summoner
    mon.com2us_id = com2us_id

    try:
        mon.monster = Monster.objects.get(com2us_id=monster_type_id)
    except Monster.DoesNotExist:
        # Unable to find a matching monster in the database - either crap data or brand new monster. Don't parse it.
        return

    # skill ups
    skills = unit_info.get('skills', [])
    if len(skills) >= 1:
        mon.skill_1_level = skills[0][1]
    if len(skills) >= 2:
        mon.skill_1_level = skills[1][1]
    if len(skills) >= 3:
        mon.skill_1_level = skills[2][1]
    if len(skills) >= 4:
        mon.skill_1_level = skills[3][1]

    try:
        created_date = get_current_timezone().localize(
            parse(unit_info.get('create_time')), is_dst=False)
        mon.created = created_date
    except (ValueError, TypeError):
        mon.created = None

    mon.stars = unit_info.get('class')
    mon.level = unit_info.get('unit_level')
    mon.in_storage = False
    mon.ignore_for_fusion = False

    if mon.monster.archetype == Monster.ARCHETYPE_MATERIAL:
        mon.fodder = True
        mon.priority = MonsterInstance.PRIORITY_DONE

    # Set custom name if homunculus
    custom_name = unit_info.get('homunculus_name')
    if unit_info.get('homunculus') and custom_name:
        mon.custom_name = custom_name

    mon.save()


def _create_new_rune(rune_info, summoner):
    reward_rune = parse_rune_data(rune_info, summoner)[0]
    reward_rune.owner = summoner
    reward_rune.save()


def _create_new_rune_craft(rune_craft_info, summoner):
    reward_rune_craft = parse_rune_craft_data(rune_craft_info, summoner)[0]
    reward_rune_craft.owner = summoner
    reward_rune_craft.save()


def _create_new_artifact(artifact_info, summoner):
    reward_artifact = parse_artifact_data(artifact_info, summoner)[0]
    reward_artifact.owner = summoner
    reward_artifact.save()


def _create_new_artifact_craft(artifact_craft_info, summoner):
    reward_artifact_craft = parse_artifact_craft_data(
        artifact_craft_info, summoner)[0]
    reward_artifact_craft.owner = summoner
    reward_artifact_craft.save()


def _sync_item(info, summoner):
    try:
        reward_item = MaterialStorage.objects.get(
            owner=summoner, item__com2us_id=info['item_master_id'])
        reward_item.quantity = info['item_quantity']
    except MaterialStorage.DoesNotExist:
        item = GameItem.objects.get(
            category__isnull=False, com2us_id=info['item_master_id'])
        reward_item = MaterialStorage(
            owner=summoner,
            item=item,
            quantity=info['item_quantity'],
        )
    reward_item.save()


def _add_quantity_to_item(info, summoner):
    idx = info.get('id', info.get('item_master_id', None))
    quantity = info.get('quantity', info.get('item_quantity', None))

    if idx is None or quantity is None:
        return

    try:
        reward_item = MaterialStorage.objects.get(
            owner=summoner, item__com2us_id=idx)
        reward_item.quantity += quantity
    except MaterialStorage.DoesNotExist:
        item = GameItem.objects.get(
            category__isnull=False, com2us_id=idx)
        reward_item = MaterialStorage(
            owner=summoner,
            item=item,
            quantity=quantity,
        )
    reward_item.save()


def _sync_monster_piece(info, summoner):
    try:
        mon_piece = MonsterPiece.objects.get(
            owner=summoner, monster__com2us_id=info['item_master_id'])
        mon_piece.pieces = info['item_quantity']
    except MonsterPiece.DoesNotExist:
        mon_piece = MonsterPiece(
            owner=summoner,
            pieces=info['item_quantity'],
            monster=Monster.objects.get(
                com2us_id=info['item_master_id']),
        )
    mon_piece.save()


def _parse_changed_item_list(changed_item_list, summoner):
    if not changed_item_list:
        # If there are changed items, it's an empty list. Exit early since later code assumes a dict
        return []

    # Parse each reward
    for obj in changed_item_list:
        # check if all required keys exist in the dict
        for k in ("type", "info"):
            if k not in obj:
                raise ValueError(f"missing key {k}")

        item_type = obj["type"]
        info = obj["info"]

        # parse common item drop
        if item_type in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
            _sync_item(info, summoner)
        # parse unit monster drop
        elif item_type == GameItem.CATEGORY_MONSTER:
            _create_new_monster(info, summoner)
        # parse rune drop
        elif item_type == GameItem.CATEGORY_RUNE:
            _create_new_rune(info, summoner)
        # parse rune craft drop - grinds, echants
        elif item_type == GameItem.CATEGORY_RUNE_CRAFT:
            _create_new_rune_craft(info, summoner)
        # parse artifact drop
        elif item_type == GameItem.CATEGORY_ARTIFACT:
            _create_new_artifact(info, summoner)
        # parse artifact craft drop - enchants
        elif item_type == GameItem.CATEGORY_ARTIFACT_CRAFT:
            _create_new_artifact_craft(info, summoner)


def sync_dungeon_reward(summoner, log_data):
    _parse_changed_item_list(
        log_data['response']['changed_item_list'], summoner)


def sync_secret_dungeon_reward(summoner, log_data):
    rewards = log_data['response']['item_list']
    if not rewards:
        return

    for reward in rewards:
        if reward['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
            _sync_monster_piece(reward, summoner)


def sync_rift_reward(summoner, log_data):
    rewards = log_data['response'].get('item_list', [])
    changed_item_list = []

    for reward in rewards:
        # material storage
        if reward['type'] == GameItem.CATEGORY_CRAFT_STUFF:
            _add_quantity_to_item(reward, summoner)
        else:
            # rune, grind, enchant
            changed_item_list.append(reward)

    _parse_changed_item_list(changed_item_list, summoner)


def _parse_crate_reward(reward, summoner):
    if not reward or not reward.get('crate', None):
        return  # no reward

    for key, val in reward['crate'].items():
        # grinds, enchants
        if key == 'changestones':
            for craft in val:
                _create_new_rune_craft(craft, summoner)
        elif key == 'rune':
            _create_new_rune(val, summoner)
        elif key == 'runes':
            for rune in val:
                _create_new_rune(rune, summoner)
        elif key == 'unit_info':
            _create_new_monster(val, summoner)
        elif key == 'craft_stuff' and val['item_master_type'] == GameItem.CATEGORY_CRAFT_STUFF:
            _add_quantity_to_item(val, summoner)


def sync_raid_reward(summoner, log_data):
    _parse_crate_reward(log_data['response']['reward'], summoner)


def sync_scenario_reward(summoner, log_data):
    _parse_crate_reward(log_data['response']['reward'], summoner)


def sync_labyrinth_reward(summoner, log_data):
    for rune in log_data['response']['pick_rune_list']:
        if rune['item_master_type'] == GameItem.CATEGORY_RUNE:
            _create_new_rune(rune['after'], summoner)
    # grinds, enchants
    for changestone in log_data['response']['pick_changestone_list']:
        if changestone['item_master_type'] == GameItem.CATEGORY_RUNE_CRAFT:
            _create_new_rune_craft(changestone['after'], summoner)


def sync_buy_item(summoner, log_data):
    # craft materials, MaterialStorage mostly
    for item in log_data['response'].get('item_list', []):
        if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
            _sync_item(item, summoner)

    # monsters used to buy/craft something, i.e. Rainbowmons
    monster_list = log_data['response'].get('source_list', [])
    if monster_list:
        # delete all monsters from the list
        MonsterInstance.objects.filter(owner=summoner, com2us_id__in=[
                                       m['source_id'] for m in monster_list]).delete()

    # Monsters taken from Monster Shrine
    sync_monster_shrine(summoner, log_data['response'].get(
        'unit_storage_list', []), full_sync=False)

    # Bought item
    _parse_crate_reward(log_data['response'].get('reward', []), summoner)

    # Crafted monsters
    for mon in log_data['response'].get('unit_list', []):
        _create_new_monster(mon, summoner)
