from django.utils.timezone import get_current_timezone
from dateutil.parser import *
from django.db import transaction

from .tasks import com2us_data_import, swex_sync_monster_shrine
from .profile_parser import validate_sw_json, default_import_options, parse_rune_data, parse_rune_craft_data, parse_artifact_data, parse_artifact_craft_data
from .models import MaterialStorage, MonsterPiece, MonsterInstance, MonsterShrineStorage, RuneInstance, ArtifactInstance
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
            # TODO: think about adding it to the Model `save` method or `post_save` signal
            if mon.quantity == 0:
                mon.delete()
            else:
                mon.save()


def _create_new_monster(unit_info, summoner):
    if not unit_info:
        return

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

    return mon


def _create_new_rune(rune_info, summoner, assigned_to=None):
    if not rune_info:
        return

    reward_rune = parse_rune_data(rune_info, summoner)[0]
    reward_rune.owner = summoner
    if reward_rune.assigned_to != assigned_to:
        reward_rune.assigned_to = assigned_to
    reward_rune.save()


def _create_new_rune_craft(rune_craft_info, summoner):
    if not rune_craft_info:
        return

    reward_rune_craft = parse_rune_craft_data(rune_craft_info, summoner)[0]
    reward_rune_craft.owner = summoner
    reward_rune_craft.save()


def _create_new_artifact(artifact_info, summoner, assigned_to=None):
    if not artifact_info:
        return

    reward_artifact = parse_artifact_data(artifact_info, summoner)[0]
    reward_artifact.owner = summoner
    if reward_artifact.assigned_to != assigned_to:
        reward_artifact.assigned_to = assigned_to
    reward_artifact.save()


def _create_new_artifact_craft(artifact_craft_info, summoner):
    if not artifact_craft_info:
        return

    reward_artifact_craft = parse_artifact_craft_data(
        artifact_craft_info, summoner)[0]
    reward_artifact_craft.owner = summoner
    reward_artifact_craft.save()


def _sync_item(info, summoner):
    if not info:
        return

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
    if not info:
        return

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
    if not info:
        return

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
        # If there are not changed items, it's an empty list. Exit early since later code assumes a dict
        return

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
            _ = _create_new_monster(info, summoner)
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


def _parse_reward(reward, summoner):
    if not reward:
        return  # no reward

    for key, val in reward.items():
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
            _ = _create_new_monster(val, summoner)
        elif key == 'unit_infos':
            for unit in val:
                _ = _create_new_monster(unit, summoner)
        elif key == 'craft_stuff' and val['item_master_type'] == GameItem.CATEGORY_CRAFT_STUFF:
            _add_quantity_to_item(val, summoner)
        elif key == 'material':
            _add_quantity_to_item(val, summoner)


def sync_dungeon_reward(summoner, log_data):
    with transaction.atomic():
        _parse_changed_item_list(
            log_data['response'].get('changed_item_list', []),
            summoner
        )


def sync_secret_dungeon_reward(summoner, log_data):
    rewards = log_data['response'].get('item_list', [])
    if not rewards:
        return

    with transaction.atomic():
        for reward in rewards:
            if reward['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                _sync_monster_piece(reward, summoner)


def sync_rift_reward(summoner, log_data):
    rewards = log_data['response'].get('item_list', [])
    changed_item_list = []

    with transaction.atomic():
        for reward in rewards:
            # material storage
            if reward['type'] == GameItem.CATEGORY_CRAFT_STUFF:
                _add_quantity_to_item(reward, summoner)
            else:
                # rune, grind, enchant
                changed_item_list.append(reward)

        _parse_changed_item_list(changed_item_list, summoner)


def sync_raid_reward(summoner, log_data):
    rewards = log_data['response'].get('reward', {})
    if not rewards:
        return

    with transaction.atomic():
        _parse_reward(rewards.get('crate', {}), summoner)


def sync_scenario_reward(summoner, log_data):
    rewards = log_data['response'].get('reward', {})
    if not rewards:
        return

    with transaction.atomic():
        _parse_reward(rewards.get('crate', {}), summoner)


def sync_labyrinth_reward(summoner, log_data):
    with transaction.atomic():
        for rune in log_data['response'].get('pick_rune_list', []):
            if rune['item_master_type'] == GameItem.CATEGORY_RUNE:
                _create_new_rune(rune['after'], summoner)

        # grinds, enchants
        for changestone in log_data['response'].get('pick_changestone_list', []):
            if changestone['item_master_type'] == GameItem.CATEGORY_RUNE_CRAFT:
                _create_new_rune_craft(changestone['after'], summoner)


def sync_buy_item(summoner, log_data):
    with transaction.atomic():
        # craft materials, MaterialStorage mostly
        for item in log_data['response'].get('item_list', []):
            if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
                _sync_item(item, summoner)
            if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                _sync_monster_piece(item, summoner)

        # monsters used to buy/craft something, i.e. Rainbowmons
        monster_list = log_data['response'].get('source_list', [])
        if monster_list:
            # delete all monsters from the list
            MonsterInstance.objects.filter(
                owner=summoner,
                com2us_id__in=[m['source_id'] for m in monster_list]
            ).delete()

        # Monsters taken from Monster Shrine
        sync_monster_shrine(summoner, log_data['response'].get(
            'unit_storage_list', []), full_sync=False)

        rewards = log_data['response'].get('reward', {})
        if rewards:
            # Bought item
            _parse_reward(rewards.get('crate', {}), summoner)

            # Random box
            _parse_reward(rewards.get('rune_random_box', {}), summoner)

        # Crafted monsters
        for mon in log_data['response'].get('unit_list', []):
            _ = _create_new_monster(mon, summoner)


def sync_toa_reward(summoner, log_data):
    with transaction.atomic():
        _parse_changed_item_list(
            log_data['response'].get('changed_item_list', []),
            summoner
        )


def sync_worldboss_reward(summoner, log_data):
    with transaction.atomic():
        rewards = log_data['response'].get('reward', {})
        if rewards:
            _parse_reward(rewards.get('crate', {}), summoner)

        for item in log_data['response'].get('item_list', []):
            if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
                _sync_item(item, summoner)


def sync_guild_black_market_buy(summoner, log_data):
    with transaction.atomic():
        for item in log_data['response'].get('item_list', []):
            if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                _sync_monster_piece(item, summoner)
            elif item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
                _sync_item(item, summoner)

        for rune in log_data['response'].get('rune_list', []):
            _create_new_rune(rune, summoner)

        for rune_craft in log_data['response'].get('runecraft_list', []):
            _create_new_rune_craft(rune_craft, summoner)


def sync_black_market_buy(summoner, log_data):
    with transaction.atomic():
        for rune in log_data['response'].get('runes', []):
            _create_new_rune(rune, summoner)

        _ = _create_new_monster(
            log_data['response'].get('unit_info', {}),
            summoner
        )


def sync_storage_monster_move(summoner, log_data):
    mons = log_data['response'].get('unit_list', [])
    if not mons:
        return

    mons_ids = [m['unit_id'] for m in mons]
    mons_to_update = {
        m.com2us_id: m for m in MonsterInstance.objects.filter(com2us_id__in=mons_ids, owner=summoner)
    }
    mons_updated = []

    for mon in mons:
        mons_updated.append(mons_to_update[mon['unit_id']])
        # there's no way of checking if it's storage or any other building (i.e. XP), so we assume it's storage
        # unless we add to Summoner new field, which stores storage `building_id`
        # TODO: Think about adding `storage` ID to `summoner`
        mons_updated[-1].in_storage = True if mon['building_id'] != 0 else False

    # we can omit `save` method, because it's only `in_storage` boolean field
    MonsterInstance.objects.bulk_update(mons_updated, ['in_storage'])


def sync_convert_monster_to_shrine(summoner, log_data):
    with transaction.atomic():
        ids_to_remove = log_data['response'].get('remove_unit_id_list', [])

        if not ids_to_remove:
            return

        MonsterInstance.objects.filter(
            owner=summoner,
            com2us_id__in=ids_to_remove
        ).delete()

        sync_monster_shrine(
            summoner,
            log_data['response'].get('unit_storage_list', []),
            full_sync=False
        )


def sync_convert_monster_from_shrine(summoner, log_data):
    with transaction.atomic():
        for mon in log_data['response'].get('add_unit_list', []):
            _ = _create_new_monster(mon, summoner)

        sync_monster_shrine(
            summoner,
            log_data['response'].get('unit_storage_list', []),
            full_sync=False
        )


def sync_convert_monster_to_material_storage(summoner, log_data):
    with transaction.atomic():
        ids_to_remove = log_data['response'].get('remove_unit_id_list', [])

        if not ids_to_remove:
            return

        MonsterInstance.objects.filter(
            owner=summoner,
            com2us_id__in=ids_to_remove
        ).delete()

        for item in log_data['response'].get('inventory_item_list', []):
            _sync_item(item, summoner)


def sync_convert_monster_from_material_storage(summoner, log_data):
    with transaction.atomic():
        for mon in log_data['response'].get('add_unit_list', []):
            _ = _create_new_monster(mon, summoner)

        for item in log_data['response'].get('inventory_item_list', []):
            _sync_item(item, summoner)


def sync_sell_inventory(summoner, log_data):
    _sync_item(log_data['response'].get('item_info', {}), summoner)


def sync_summon_unit(summoner, log_data):
    with transaction.atomic():
        for item in log_data['response'].get('item_list', []):
            if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
                _sync_item(item, summoner)

        for mon in log_data['response'].get('unit_list', []):
            _ = _create_new_monster(mon, summoner)


def sync_monster_from_pieces(summoner, log_data):
    with transaction.atomic():
        for item in log_data['response'].get('item_list', []):
            if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                _sync_monster_piece(item, summoner)

        _ = _create_new_monster(
            log_data['response'].get('unit_info', {}),
            summoner
        )


def sync_awaken_unit(summoner, log_data):
    mon = log_data['response'].get('unit_info', {})
    if not mon:
        return

    with transaction.atomic():
        for item in log_data['response'].get('item_list', []):
            if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                _sync_monster_piece(item, summoner)

        try:
            mon = MonsterInstance.objects.get(
                owner=summoner, com2us_id=mon['unit_id'])
            if mon.monster.awakens_to is not None:
                mon.monster = mon.monster.awakens_to
                mon.save()
        except MonsterInstance.DoesNotExist:
            # probably not synced data
            _ = _create_new_monster(mon, summoner)


def sync_sell_unit(summoner, log_data):
    mon = log_data['response'].get('unit_info', {})
    if not mon:
        return

    try:
        MonsterInstance.objects.get(
            owner=summoner, com2us_id=mon['unit_id']).delete()
    except MonsterInstance.DoesNotExist:
        # if monster doesn't exist in db, it means profile wasn't synced
        # even though it's not bad for `SellUnit`, we send a message informing about sync conflict
        return "monster"


def sync_upgrade_unit(summoner, log_data):
    # increase stars, skillups or level
    with transaction.atomic():
        # source_unit_list - inventory, storage, not available in response
        source_mon = log_data['request'].get('source_unit_list', [])
        if source_mon:
            MonsterInstance.objects.filter(
                owner=summoner,
                com2us_id__in=[m['unit_id'] for m in source_mon]
            ).delete()

        for item in log_data['response'].get('inventory_item_list', []):
            if item['item_master_type'] == GameItem.CATEGORY_MATERIAL_MONSTER:
                _sync_item(item, summoner)

        sync_monster_shrine(
            summoner,
            log_data['response'].get('unit_storage_list', []),
            full_sync=False
        )

        mon_data = log_data['response']['unit_info']
        try:
            mon = MonsterInstance.objects.get(
                owner=summoner, com2us_id=mon_data['unit_id'])
            to_update = False

            if mon.level != mon_data['unit_level']:
                to_update = True
                mon.level = mon_data['unit_level']

            if mon.stars != mon_data['class']:
                to_update = True
                mon.stars = mon_data['class']

            mon_skills = [s[1] for s in mon_data['skills']]
            if len(mon_skills) >= 1 and mon.skill_1_level != mon_skills[0]:
                to_update = True
                mon.skill_1_level = mon_skills[0]

            if len(mon_skills) >= 2 and mon.skill_2_level != mon_skills[1]:
                to_update = True
                mon.skill_2_level = mon_skills[1]

            if len(mon_skills) >= 3 and mon.skill_3_level != mon_skills[2]:
                to_update = True
                mon.skill_3_level = mon_skills[2]

            if len(mon_skills) >= 4 and mon.skill_4_level != mon_skills[3]:
                to_update = True
                mon.skill_4_level = mon_skills[3]

            if to_update:
                # if nothing has changed, there's no point of doing one more database call
                mon.save()
        except MonsterInstance.DoesNotExist:
            _ = _create_new_monster(mon_data, summoner)


def sync_lock_unit(summoner, log_data):
    try:
        mon = MonsterInstance.objects.get(
            owner=summoner,
            com2us_id=log_data['response']['unit_id']
        )
        mon.ignore_for_fusion = True
        mon.save()
    except MonsterInstance.DoesNotExist:
        # if monster doesn't exist in db, it means profile wasn't synced
        # we send a message informing about sync conflict
        return "monster"


def sync_unlock_unit(summoner, log_data):
    try:
        mon = MonsterInstance.objects.get(
            owner=summoner,
            com2us_id=log_data['response']['unit_id']
        )
        mon.ignore_for_fusion = False
        mon.save()
    except MonsterInstance.DoesNotExist:
        # if monster doesn't exist in db, it means profile wasn't synced
        # we send a message informing about sync conflict
        return "monster"


def _change_rune_substats(rune, rune_data, summoner):
    temp_substats = []
    temp_substat_values = []
    temp_substats_enchanted = []
    temp_substats_grind_value = []

    for substat in rune_data['sec_eff']:
        substat_type = RuneInstance.COM2US_STAT_MAP[substat[0]]
        substat_value = substat[1]
        enchanted = substat[2] == 1 if len(substat) >= 3 else 0
        grind_value = substat[3] if len(substat) >= 4 else 0

        temp_substats.append(substat_type)
        temp_substat_values.append(substat_value)
        temp_substats_enchanted.append(enchanted)
        temp_substats_grind_value.append(grind_value)

    rune.substats = temp_substats
    rune.substat_values = temp_substat_values
    rune.substats_enchanted = temp_substats_enchanted
    rune.substats_grind_value = temp_substats_grind_value


def sync_upgrade_rune(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})
    if not rune_data:
        return

    try:
        rune = RuneInstance.objects.get(
            owner=summoner,
            com2us_id=rune_data['rune_id']
        )
        if rune_data['upgrade_curr'] != rune.level:
            rune.level = rune_data['upgrade_curr']
            _change_rune_substats(rune, rune_data, summoner)
            rune.save()
    except RuneInstance.DoesNotExist:
        try:
            assigned_to = MonsterInstance.objects.get(
                owner=summoner,
                com2us_id=rune_data['occupied_id']
            ) if rune_data['occupied_id'] != 0 else None

            _create_new_rune(rune_data, summoner, assigned_to)
        except MonsterInstance.DoesNotExist:
            # data not synced
            return "monster"


def sync_sell_rune(summoner, log_data):
    rune_ids = [r['rune_id'] for r in log_data['response'].get('runes', [])]
    if not rune_ids:
        return

    with transaction.atomic():
        runes = RuneInstance.objects.select_related('assigned_to').filter(
            owner=summoner,
            com2us_id__in=rune_ids
        )
        mons = [rune.assigned_to for rune in runes if rune.assigned_to]
        runes.delete()

        # recalculate stats
        for mon in mons:
            mon.save()


def sync_grind_rune(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})
    rune_craft_data = log_data['response'].get('rune_craft_item', {})

    if not rune_data or not rune_craft_data:
        return

    with transaction.atomic():
        try:
            rune = RuneInstance.objects.get(
                owner=summoner,
                com2us_id=rune_data['rune_id']
            )
            _change_rune_substats(rune, rune_data, summoner)
            rune.save()
        except RuneInstance.DoesNotExist:
            try:
                assigned_to = MonsterInstance.objects.get(
                    owner=summoner,
                    com2us_id=rune_data['occupied_id']
                ) if rune_data['occupied_id'] != 0 else None

                _create_new_rune(rune_data, summoner, assigned_to)
            except MonsterInstance.DoesNotExist:
                # data not synced
                return "monster"

        # make sure rune & assigned_to monster data is synced, then change grinds
        rune_craft = parse_rune_craft_data(rune_craft_data, summoner)[0]
        if rune_craft.quantity == 0:
            rune_craft.delete()
        else:
            if not rune_craft.owner:
                rune_craft.owner = summoner
            rune_craft.save()


def sync_enchant_rune(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})
    rune_craft_data = log_data['response'].get('rune_craft_item', {})

    if not rune_data or not rune_craft_data:
        return

    with transaction.atomic():
        try:
            rune = RuneInstance.objects.get(
                owner=summoner,
                com2us_id=rune_data['rune_id']
            )
            _change_rune_substats(rune, rune_data, summoner)
            rune.save()
        except RuneInstance.DoesNotExist:
            try:
                assigned_to = MonsterInstance.objects.get(
                    owner=summoner,
                    com2us_id=rune_data['occupied_id']
                ) if rune_data['occupied_id'] != 0 else None

                _create_new_rune(rune_data, summoner, assigned_to)
            except MonsterInstance.DoesNotExist:
                # data not synced
                return "monster"

        # make sure rune & assigned_to monster data is synced, then change grinds
        rune_craft = parse_rune_craft_data(rune_craft_data, summoner)[0]
        if rune_craft.quantity == 0:
            rune_craft.delete()
        else:
            if not rune_craft.owner:
                rune_craft.owner = summoner
            rune_craft.save()


def sync_reapp_rune(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})

    try:
        rune = RuneInstance.objects.get(
            owner=summoner,
            com2us_id=rune_data['rune_id']
        )
        _change_rune_substats(rune, rune_data, summoner)
        rune.save()
    except RuneInstance.DoesNotExist:
        try:
            assigned_to = MonsterInstance.objects.get(
                owner=summoner,
                com2us_id=rune_data['occupied_id']
            ) if rune_data['occupied_id'] != 0 else None

            _create_new_rune(rune_data, summoner, assigned_to)
        except MonsterInstance.DoesNotExist:
            # data not synced
            return "monster"


def sync_equip_rune(summoner, log_data):
    removed_rune = log_data['response'].get('removed_rune', {})
    rune_id = log_data['response'].get('rune_id', 0)
    mon_data = log_data['response'].get('unit_info', {})

    if not rune_id or not mon_data:
        return

    with transaction.atomic():
        try:
            mon = MonsterInstance.objects.get(
                owner=summoner,
                com2us_id=mon_data['unit_id'],
            )
            rune = RuneInstance.objects.get(
                owner=summoner,
                com2us_id=rune_id,
            )
        except (RuneInstance.DoesNotExist, MonsterInstance.DoesNotExist):
            return "rune|monster"

        if removed_rune:
            try:
                RuneInstance.objects.get(
                    owner=summoner,
                    com2us_id=removed_rune['rune_id']
                ).delete()
            except RuneInstance.DoesNotExist:
                # rune didn't exist in db, profile probably not sync
                return "rune"

        # it also recalculates monster stats, saves changes to DB only when everything else is synced
        rune.assigned_to = mon
        rune.save()


def sync_change_runes_in_rune_management(summoner, log_data):
    mon_data = log_data['response'].get('unit_info', {})
    unequip_rune_ids = log_data['response'].get('unequip_rune_id_list', [])
    equip_rune_ids = log_data['response'].get('equip_rune_id_list', [])

    if not mon_data:
        return

    with transaction.atomic():
        try:
            mon = MonsterInstance.objects.get(
                owner=summoner,
                com2us_id=mon_data['unit_id'],
            )
        except MonsterInstance.DoesNotExist:
            return "monster"

        runes_to_unassign = RuneInstance.objects.select_related('assigned_to').filter(
            owner=summoner,
            com2us_id__in=unequip_rune_ids,
        )
        runes_to_equip = RuneInstance.objects.select_related('assigned_to').filter(
            owner=summoner,
            com2us_id__in=equip_rune_ids,
        )
        mons_to_update = {mon.id: mon}
        runes_to_update = dict()

        for rune in runes_to_unassign:
            if rune.id not in runes_to_update:
                runes_to_update[rune.id] = rune
            if rune.assigned_to is not None and rune.assigned_to.id not in mons_to_update:
                mons_to_update[rune.assigned_to.id] = rune.assigned_to
            rune.assigned_to = None

        for rune in runes_to_equip:
            if rune.id not in runes_to_update:
                runes_to_update[rune.id] = rune
            rune.assigned_to = mon

        # omiting `save` method from `RuneInstance` because we'll force save
        # every `MonsterInstance` used in this transaction
        RuneInstance.objects.bulk_update(
            runes_to_update.values(), ['assigned_to'])

        # recalc stats of every monster used in this transaction
        for mon in mons_to_update.values():
            mon.save()


def sync_unequip_rune(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})
    mon_data = log_data['response'].get('unit_info', {})

    if not rune_data or not mon_data:
        return

    with transaction.atomic():
        try:
            mon = MonsterInstance.objects.get(
                owner=summoner,
                com2us_id=mon_data['unit_id'],
            )
            rune = RuneInstance.objects.get(
                owner=summoner,
                com2us_id=rune_data['rune_id'],
            )
        except (RuneInstance.DoesNotExist, MonsterInstance.DoesNotExist):
            return "rune|monster"

        rune.assigned_to = None
        rune.save()
        # recalculate monster stats after unequipping rune
        mon.save()


def _change_artifact_substats(artifact, artifact_data, summoner):
    temp_effects = []
    temp_effects_value = []
    temp_effects_upgrade_count = []
    temp_effects_reroll_count = []
    for sec_eff in artifact_data['sec_effects']:
        effect = artifact.COM2US_EFFECT_MAP[sec_eff[0]]
        value = sec_eff[1]
        upgrade_count = sec_eff[2]
        reroll_count = sec_eff[4]

        temp_effects.append(effect)
        temp_effects_value.append(value)
        temp_effects_upgrade_count.append(upgrade_count)
        temp_effects_reroll_count.append(reroll_count)

    artifact.effects = temp_effects
    artifact.effects_value = temp_effects_value
    artifact.effects_upgrade_count = temp_effects_upgrade_count
    artifact.effects_reroll_count = temp_effects_reroll_count


def sync_upgrade_artifact(summoner, log_data):
    artifact_data = log_data['response'].get('artifact', {})

    if not artifact_data:
        return

    try:
        artifact = ArtifactInstance.objects.get(
            owner=summoner,
            com2us_id=artifact_data['rid']
        )
        if artifact_data['level'] != artifact.level:
            artifact.level = artifact_data['level']
            _change_artifact_substats(artifact, artifact_data, summoner)
            artifact.save()
    except ArtifactInstance.DoesNotExist:
        try:
            assigned_to = MonsterInstance.objects.get(
                owner=summoner,
                com2us_id=artifact_data['occupied_id']
            ) if artifact_data['occupied_id'] != 0 else None

            _create_new_artifact(artifact_data, summoner, assigned_to)
        except MonsterInstance.DoesNotExist:
            # data not synced
            return "monster"


def sync_change_artifact_assignment(summoner, log_data):
    artifact_assignments = {}
    monster_ids = []

    with transaction.atomic():
        for artifact in log_data['response'].get('updated_artifacts', []):
            artifact_assignments[artifact['rid']] = artifact
            if artifact['occupied_id'] > 0:
                monster_ids.append(artifact['occupied_id'])

        artifacts = {a.com2us_id: a for a in ArtifactInstance.objects.select_related('assigned_to').filter(
            owner=summoner,
            com2us_id__in=artifact_assignments.keys(),
        )}
        monsters = {m.com2us_id: m for m in MonsterInstance.objects.filter(
            owner=summoner,
            com2us_id__in=monster_ids,
        )}

        mons_updated = dict()

        for artifact_id, artifact_assignment in artifact_assignments.items():
            artifact = artifacts.get(artifact_id, None)
            if not artifact:
                # data not synced
                return "artifact"

            if artifact.assigned_to is not None and artifact.assigned_to.id not in mons_updated:
                mons_updated[artifact.assigned_to.id] = artifact.assigned_to

            if artifact_assignment > 0:
                mon = monsters.get(artifact_assignment, None)
                if artifact_assignment not in mons_updated and mon:
                    mons_updated[artifact_assignment] = mon
                artifact.assigned_to = mon
            else:
                artifact.assigned_to = None

        # `bulk_update` to prevent `ArtifactInstance` from calling `save` method and recalc monster stats
        ArtifactInstance.objects.bulk_update(
            artifacts.values(),
            ['assigned_to']
        )

        # recalc stats for every monster updated
        for monster in mons_updated.values():
            monster.save()


def sync_sell_artifacts(summoner, log_data):
    artifact_ids = log_data['response'].get('artifact_ids', [])

    if not artifact_ids:
        return

    with transaction.atomic():
        artifacts = ArtifactInstance.objects.select_related('assigned_to').filter(
            owner=summoner,
            com2us_id__in=artifact_ids,
        )
        mons = [artifact.assigned_to for artifact in artifacts if artifact.assigned_to]
        artifacts.delete()

        # recalculate stats
        for mon in mons:
            mon.save()


def sync_artifact_pre_enchant(summoner, log_data):
    for item in log_data['response'].get('inventory_info', []):
        _create_new_artifact_craft(item, summoner)


def sync_artifact_post_enchant(summoner, log_data):
    artifact_data = log_data['response'].get('artifact', {})

    if not artifact_data:
        return

    try:
        artifact = ArtifactInstance.objects.get(
            owner=summoner,
            com2us_id=artifact_data['rid'],
        )
        _change_artifact_substats(artifact, artifact_data, summoner)
    except ArtifactInstance.DoesNotExist:
        try:
            assigned_to = MonsterInstance.objects.get(
                owner=summoner,
                com2us_id=artifact_data['occupied_id']
            ) if artifact_data['occupied_id'] != 0 else None

            _create_new_artifact(artifact_data, summoner, assigned_to)
        except MonsterInstance.DoesNotExist:
            return "monster"


def sync_daily_reward(summoner, log_data):
    items = log_data['response'].get('item_list', [])
    runes = log_data['response'].get('rune_list', [])

    for item in items:
        if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
            _sync_item(item, summoner)
        if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
            _sync_monster_piece(item, summoner)

    for rune in runes:
        _create_new_rune(rune, summoner)


def sync_receive_mail(summoner, log_data):
    runes = log_data['response'].get('rune_list', [])
    monsters = log_data['response'].get('unit_list', [])

    for rune in runes:
        _create_new_rune(rune, summoner)

    for mon in monsters:
        _ = _create_new_monster(mon, summoner)


def sync_wish_reward(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})
    monster_data = log_data['response'].get('unit_info', {})

    _create_new_rune(rune_data, summoner)
    _ = _create_new_monster(monster_data, summoner)


def sync_siege_crate_reward(summoner, log_data):
    selected_crate_id = log_data['request'].get('crate_index', 0)
    crates = log_data['response'].get('crate_list', [])
    selected_crate = {}

    if not selected_crate or not crates:
        return

    with transaction.atomic():
        for crate in crates:
            if crate['crate_index'] == selected_crate_id and isinstance(crate['reward_list'], dict):
                selected_crate = crate['reward_list']
                break

        _parse_reward(selected_crate, summoner)
