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

    import_options = summoner.preferences.get('import_options', default_import_options)
    com2us_data_import.delay(log_data['response'], summoner.pk, import_options)


def sync_monster_shrine(summoner, log_data, full_sync=True):
    if full_sync:
        swex_sync_monster_shrine.delay(log_data['response'], summoner.pk)
    else:
        monster_ids = [m['unit_master_id'] for m in log_data]
        monster_bases = {m.com2us_id: m for m in Monster.objects.filter(com2us_id__in=monster_ids)}
        for monster in log_data:
            item = monster_bases.get(monster['unit_master_id'])
            if not item:
                # Monster doesn't exist
                continue
            obj, _ = MonsterShrineStorage.objects.update_or_create(
                owner=summoner,
                item=item,
                defaults={
                    'quantity': monster['quantity'],
                }
            )
            if obj.quantity <= 0:
                obj.delete()


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
    mon.in_storage = unit_info.get('building_id') != 0
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

    reward_rune = parse_rune_data(rune_info, summoner)
    reward_rune.save()
    mon = reward_rune.assigned_to
    if mon:
        mon.default_build.runes.remove(reward_rune)
    if assigned_to:
        assigned_to.default_build.assign_rune(reward_rune)


def _create_new_rune_craft(rune_craft_info, summoner):
    if not rune_craft_info:
        return

    reward_rune_craft = parse_rune_craft_data(rune_craft_info, summoner)[0]
    reward_rune_craft.owner = summoner
    reward_rune_craft.save()


def _create_new_artifact(artifact_info, summoner, assigned_to=None):
    if not artifact_info:
        return

    reward_artifact = parse_artifact_data(artifact_info, summoner)
    reward_artifact.save()
    mon = reward_artifact.assigned_to
    if mon:
        mon.default_build.artifacts.remove(reward_artifact)
    if assigned_to:
        assigned_to.default_build.assign_artifact(reward_artifact)


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

    item = GameItem.objects.filter(
        category=info['item_master_type'], 
        com2us_id=info['item_master_id'],
    ).first()

    if not item:
        return
    MaterialStorage.objects.update_or_create(
        owner=summoner,
        item=item,
        defaults={
            'quantity': info['item_quantity'],
        },
    )


def _add_quantity_to_item(info, summoner):
    if not info:
        return

    idx = info.get('item_master_id', info.get('id'))
    quantity = info.get('item_quantity', info.get('quantity'))
    typex = info.get('item_master_type', info.get('type'))

    if idx is None or quantity is None or typex is None:
        return

    item = GameItem.objects.filter(category=typex, com2us_id=idx).first()

    if not item:
        return

    obj, created = MaterialStorage.objects.get_or_create(
        owner=summoner,
        item=item,
        defaults={
            'quantity': quantity,
        },
    )

    if not created:
        obj.quantity += quantity
        obj.save()


def _sync_monster_piece(info, summoner):
    if not info:
        return

    mon = Monster.objects.filter(com2us_id=info['item_master_id']).first()

    if not mon:
        return

    obj, _ = MonsterPiece.objects.update_or_create(
        owner=summoner,
        monster=mon,
        defaults={
            'pieces': info['item_quantity'],
        },
    )
    if obj.pieces <= 0:
        obj.delete()


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
        # parse HOH - monster pieces
        elif item_type == GameItem.CATEGORY_MONSTER_PIECE:
            _sync_monster_piece(info, summoner)


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
    _parse_changed_item_list(
        log_data['response'].get('changed_item_list', []),
        summoner
    )


def sync_secret_dungeon_reward(summoner, log_data):
    rewards = log_data['response'].get('item_list', [])
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
        elif reward['type'] in [GameItem.CATEGORY_RUNE, GameItem.CATEGORY_RUNE_CRAFT, GameItem.CATEGORY_MONSTER]:
            # rune, grind, enchant, rainbowmon
            changed_item_list.append(reward)

    _parse_changed_item_list(changed_item_list, summoner)


def sync_raid_reward(summoner, log_data):
    rewards = log_data['response'].get('reward', {})
    if not rewards:
        return

    _parse_reward(rewards.get('crate', {}), summoner)


def sync_scenario_reward(summoner, log_data):
    rewards = log_data['response'].get('reward', {})
    if not rewards:
        return

    _parse_reward(rewards.get('crate', {}), summoner)


def sync_labyrinth_reward(summoner, log_data):
    for rune in log_data['response'].get('pick_rune_list', []):
        if rune['item_master_type'] == GameItem.CATEGORY_RUNE:
            _create_new_rune(rune['after'], summoner)

    # grinds, enchants
    for changestone in log_data['response'].get('pick_changestone_list', []):
        if changestone['item_master_type'] == GameItem.CATEGORY_RUNE_CRAFT:
            _create_new_rune_craft(changestone['after'], summoner)


def sync_buy_item(summoner, log_data):
    # craft materials, MaterialStorage mostly
    for item in log_data['response'].get('item_list', []):
        if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
            _sync_item(item, summoner)
        elif item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
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
    _parse_changed_item_list(
        log_data['response'].get('changed_item_list', []),
        summoner
    )


def sync_worldboss_reward(summoner, log_data):
    rewards = log_data['response'].get('reward', {})
    if rewards:
        _parse_reward(rewards.get('crate', {}), summoner)

    for item in log_data['response'].get('item_list', []):
        if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
            _sync_item(item, summoner)


def sync_guild_black_market_buy(summoner, log_data):
    items = log_data['response'].get('item_list', [])
    if items:
        for item in items:
            if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                _sync_monster_piece(item, summoner)
            elif item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
                _sync_item(item, summoner)

    runes = log_data['response'].get('rune_list', [])
    if runes:
        for rune in runes:
            _create_new_rune(rune, summoner)

    rune_crafts = log_data['response'].get('runecraft_list', [])
    if rune_crafts:
        for rune_craft in rune_crafts:
            _create_new_rune_craft(rune_craft, summoner)


def sync_black_market_buy(summoner, log_data):
    runes = log_data['response'].get('runes', [])
    if runes:
        for rune in runes:
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
        if mon['unit_id'] in mons_to_update.keys():
            mons_updated.append(mons_to_update[mon['unit_id']])
            # there's no way of checking if it's storage or any other building (i.e. XP), so we assume it's storage
            # unless we add to Summoner new field, which stores storage `building_id`
            # TODO: Think about adding `storage` ID to `summoner`
            mons_updated[-1].in_storage = True if mon['building_id'] != 0 else False
        else:
            _ = _create_new_monster(mon, summoner)

    # we can omit `save` method, because it's only `in_storage` boolean field
    MonsterInstance.objects.bulk_update(mons_updated, ['in_storage'])


def sync_convert_monster_to_shrine(summoner, log_data):
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
    for mon in log_data['response'].get('add_unit_list', []):
        _ = _create_new_monster(mon, summoner)

    sync_monster_shrine(
        summoner,
        log_data['response'].get('unit_storage_list', []),
        full_sync=False
    )


def sync_convert_monster_to_material_storage(summoner, log_data):
    ids_to_remove = log_data['response'].get('remove_unit_id_list', [])

    if not ids_to_remove:
        return

    for mon in MonsterInstance.objects.filter(
        owner=summoner,
        com2us_id__in=ids_to_remove
    ):
        # explicitly delete rune builds, so we won't get unexpected 500
        if mon.default_build:
            mon.default_build.delete()
        if mon.rta_build:
            mon.rta_build.delete()
        mon.delete()

    for item in log_data['response'].get('inventory_item_list', []):
        _sync_item(item, summoner)


def sync_convert_monster_from_material_storage(summoner, log_data):
    for mon in log_data['response'].get('add_unit_list', []):
        _ = _create_new_monster(mon, summoner)

    for item in log_data['response'].get('inventory_item_list', []):
        _sync_item(item, summoner)


def sync_sell_inventory(summoner, log_data):
    _sync_item(log_data['response'].get('item_info', {}), summoner)


def sync_summon_unit(summoner, log_data):
    for item in log_data['response'].get('item_list', []):
        if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
            _sync_item(item, summoner)

    for mon in log_data['response'].get('unit_list', []):
        _ = _create_new_monster(mon, summoner)


def sync_blessing_choice(summoner, log_data):
    for mon in log_data['response'].get('unit_list', []):
        _ = _create_new_monster(mon, summoner)


def sync_monster_from_pieces(summoner, log_data):
    for item in log_data['response'].get('item_list', []):
        if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
            _sync_monster_piece(item, summoner)

    _ = _create_new_monster(
        log_data['response'].get('unit_info', {}),
        summoner
    )


def sync_awaken_unit(summoner, log_data):
    mon_data = log_data['response'].get('unit_info', {})
    if not mon_data:
        return

    items = log_data['response'].get('item_list', [])
    if items:
        for item in items:
            if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                _sync_monster_piece(item, summoner)
            elif item['item_master_type'] == GameItem.CATEGORY_ESSENCE:
                _sync_item(item, summoner)

    mon = MonsterInstance.objects.filter(
        owner=summoner, com2us_id=mon_data['unit_id']).first()

    if not mon:
        # probably not synced data
        _ = _create_new_monster(mon_data, summoner)
    else:
        if mon.monster.awakens_to is not None:
            mon.monster = mon.monster.awakens_to
            mon.save()


def sync_sell_unit(summoner, log_data):
    mon = log_data['response'].get('unit_info', {})
    if not mon:
        return

    MonsterInstance.objects.filter(owner=summoner, com2us_id=mon['unit_id']).delete()


def sync_upgrade_unit(summoner, log_data):
    # increase stars, skillups or level
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

    mon_data = log_data['response'].get('unit_info', {})
    if not mon_data:
        mon_data = log_data['response'].get('target_unit', {})

    mon = MonsterInstance.objects.filter(owner=summoner, com2us_id=mon_data['unit_id']).first()

    if not mon:
        _ = _create_new_monster(mon_data, summoner)
        return

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


def sync_lock_unit(summoner, log_data):
    mon = MonsterInstance.objects.filter(
        owner=summoner,
        com2us_id=log_data['response']['unit_id']
    ).first()
    
    if not mon:
        return "monster"

    mon.ignore_for_fusion = True
    mon.save()


def sync_unlock_unit(summoner, log_data):
    mon = MonsterInstance.objects.filter(
        owner=summoner,
        com2us_id=log_data['response']['unit_id']
    ).first()

    if not mon:
        return "monster"

    mon.ignore_for_fusion = False
    mon.save()


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

    rune = RuneInstance.objects.filter(
        owner=summoner,
        com2us_id=rune_data['rune_id']
    ).first()
    if rune:
        if rune_data['upgrade_curr'] != rune.level:
            rune.level = rune_data['upgrade_curr']
            rune.main_stat_value = rune_data['pri_eff'][1]
            _change_rune_substats(rune, rune_data, summoner)
            rune.save()
            # new substat/roll, recalculate build
            monster = rune.assigned_to
            if monster:
                monster.default_build.clear_cache_properties()
                monster.default_build.update_stats()
                monster.default_build.save()
    else:
        assigned_to = MonsterInstance.objects.filter(
            owner=summoner,
            com2us_id=rune_data['occupied_id']
        ).first() if rune_data['occupied_id'] != 0 else None

        if not assigned_to:
            return "monster"

        _create_new_rune(rune_data, summoner, assigned_to)


def sync_sell_rune(summoner, log_data):
    rune_ids = log_data['request'].get('rune_id_list', [])
    if not rune_ids:
        return

    runes = RuneInstance.objects.select_related('assigned_to').filter(
        owner=summoner,
        com2us_id__in=rune_ids
    )
    mons = {}
    for rune in runes:
        if not rune.assigned_to:
            continue
        if rune.assigned_to not in mons:
            mons[rune.assigned_to] = []
        mons[rune.assigned_to].append(rune)

    # recalculate builds
    for mon, mon_runes in mons.items():
        mon.default_build.runes.remove(*mon_runes)

    runes.delete()


def sync_grind_enchant_rune(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})
    rune_craft_data = log_data['response'].get('rune_craft_item', {})

    if not rune_data or not rune_craft_data:
        return

    rune = RuneInstance.objects.filter(
        owner=summoner,
        com2us_id=rune_data['rune_id']
    ).first()

    if rune:
        _change_rune_substats(rune, rune_data, summoner)
        rune.save()
        monster = rune.assigned_to
        if monster:
            monster.default_build.clear_cache_properties()
            monster.default_build.update_stats()
            monster.default_build.save()
    else:
        assigned_to = MonsterInstance.objects.filter(
            owner=summoner,
            com2us_id=rune_data['occupied_id']
        ).first() if rune_data['occupied_id'] != 0 else None

        _create_new_rune(rune_data, summoner, assigned_to)

    # make sure rune & assigned_to monster data is synced, then change grinds
    rune_craft = parse_rune_craft_data(rune_craft_data, summoner)[0]
    if rune_craft.quantity == 0:
        rune_craft.delete()
    else:
        if not rune_craft.owner:
            rune_craft.owner = summoner
        rune_craft.save()


def sync_reapp_rune(summoner, log_data):
    if log_data['request'].get('rollback', False):
        return

    rune_data = log_data['response'].get('rune', {})

    rune = RuneInstance.objects.filter(
        owner=summoner,
        com2us_id=rune_data['rune_id']
    ).first()

    if rune:
        _change_rune_substats(rune, rune_data, summoner)
        rune.save()
        monster = rune.assigned_to
        if monster:
            monster.default_build.clear_cache_properties()
            monster.default_build.update_stats()
            monster.default_build.save()
    else:
        assigned_to = MonsterInstance.objects.filter(
            owner=summoner,
            com2us_id=rune_data['occupied_id']
        ).first() if rune_data['occupied_id'] != 0 else None

        _create_new_rune(rune_data, summoner, assigned_to)


def sync_equip_rune(summoner, log_data):
    removed_rune = log_data['response'].get('removed_rune', {})
    rune_id = log_data['response'].get('rune_id', 0)
    mon_data = log_data['response'].get('unit_info', {})

    if not rune_id or not mon_data:
        return

    mon = MonsterInstance.objects.filter(
        owner=summoner,
        com2us_id=mon_data['unit_id'],
    ).first()

    if not mon:
        return "monster"
    
    if removed_rune:
        runes_to_remove = RuneInstance.objects.filter(
            owner=summoner,
            com2us_id=removed_rune['rune_id']
        )
        # it should be fetched by Signal
        # mon.default_build.runes.remove(*runes_to_remove)
        runes_to_remove.delete()

    rune = RuneInstance.objects.filter(
        owner=summoner,
        com2us_id=rune_id,
    ).first()

    if not rune:
        return "rune"

    mon.default_build.assign_rune(rune)


def sync_change_runes_in_rune_management(summoner, log_data):
    mon_data = log_data['response'].get('unit_info', {})
    unequip_rune_ids = log_data['response'].get('unequip_rune_id_list', [])
    equip_rune_ids = log_data['response'].get('equip_rune_id_list', [])

    if not mon_data:
        return

    mon = MonsterInstance.objects.filter(
        owner=summoner,
        com2us_id=mon_data['unit_id'],
    ).first()
    if not mon:
        return "monster"

    runes_to_unassign = RuneInstance.objects.select_related('assigned_to').filter(
        owner=summoner,
        com2us_id__in=unequip_rune_ids,
    )
    runes_to_equip = RuneInstance.objects.select_related('assigned_to').filter(
        owner=summoner,
        com2us_id__in=equip_rune_ids,
    )
    unequip = {}

    for rune in runes_to_unassign:
        if not rune.assigned_to:
            continue # don't try to unequipp already unequipped rune
        if rune.assigned_to not in unequip:
            unequip[rune.assigned_to] = []
        unequip[rune.assigned_to].append(rune)
    
    for monster, runes in unequip.items():
        monster.default_build.runes.remove(*runes)

    for rune in runes_to_equip:
        mon.default_build.assign_rune(rune)


def sync_unequip_rune(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})
    mon_data = log_data['response'].get('unit_info', {})

    if not rune_data or not mon_data:
        return

    mon = MonsterInstance.objects.filter(
        owner=summoner,
        com2us_id=mon_data['unit_id'],
    ).first()

    if not mon:
        return "monster"

    rune = RuneInstance.objects.filter(
        owner=summoner,
        com2us_id=rune_data['rune_id'],
    ).first()

    if not rune:
        return "rune"

    mon.default_build.runes.remove(rune)


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

    artifact = ArtifactInstance.objects.filter(
        owner=summoner,
        com2us_id=artifact_data['rid']
    ).first()

    if artifact:
        if artifact_data['level'] != artifact.level:
            artifact.level = artifact_data['level']
            _change_artifact_substats(artifact, artifact_data, summoner)
            artifact.save()
            monster = artifact.assigned_to
            if monster:
                monster.default_build.clear_cache_properties()
                monster.default_build.update_stats()
                monster.default_build.save()
    else:
        assigned_to = MonsterInstance.objects.filter(
            owner=summoner,
            com2us_id=artifact_data['occupied_id']
        ).first() if artifact_data['occupied_id'] != 0 else None

        if not assigned_to:
            return "monster"

        _create_new_artifact(artifact_data, summoner, assigned_to)


def sync_change_artifact_assignment(summoner, log_data):
    log_artifacts = log_data['response'].get('updated_artifacts', [])
    artifact_unequip = {}
    artifact_equip = {}
    mons_id = []
    artifacts_id = []

    for artifact_data in log_artifacts:
        artifacts_id.append(artifact_data['rid'])
        if artifact_data['occupied_id'] > 0:
            mons_id.append(artifact_data['occupied_id'])

    artifacts = {a.com2us_id: a for a in ArtifactInstance.objects.select_related('assigned_to').filter(
        owner=summoner,
        com2us_id__in=artifacts_id,
    )}
    monsters = {m.com2us_id: m for m in MonsterInstance.objects.select_related('default_build').filter(
        owner=summoner,
        com2us_id__in=mons_id,
    )}

    for artifact_data in log_artifacts:
        artifact = artifacts[artifact_data['rid']]
        if artifact_data['occupied_id'] > 0:
            monster = monsters.get(artifact_data['occupied_id'], None)
            if not monster:
                return "monster" # don't try to equip rune on non-existing monster
            if monster not in artifact_equip:
                artifact_equip[monster] = []
            artifact_equip[monster].append(artifact)
        else:
            if not artifact.assigned_to:
                continue # don't try to unequipp already unequipped artifact
            if artifact.assigned_to not in artifact_unequip:
                artifact_unequip[artifact.assigned_to] = []
            artifact_unequip[artifact.assigned_to].append(artifact)

    for mon, artifacts in artifact_unequip.items():
        mon.default_build.artifacts.remove(*artifacts)

    for mon, artifacts in artifact_equip.items():
        for artifact in artifacts:
            mon.default_build.assign_artifact(artifact)


def sync_sell_artifacts(summoner, log_data):
    artifact_ids = log_data['request'].get('artifact_ids', [])
    if not artifact_ids:
        return

    artifacts = ArtifactInstance.objects.select_related('assigned_to').filter(
        owner=summoner,
        com2us_id__in=artifact_ids,
    )
    mons = {}
    for artifact in artifacts:
        if not artifact.assigned_to:
            continue
        if artifact.assigned_to not in mons:
            mons[artifact.assigned_to] = []
        mons[artifact.assigned_to].append(artifact)

    # recalculate builds
    for mon, mon_artifacts in mons.items():
        mon.default_build.artifacts.remove(*mon_artifacts)

    artifacts.delete()


def sync_artifact_pre_enchant(summoner, log_data):
    for item in log_data['response'].get('inventory_info', []):
        if item['item_master_type'] == GameItem.CATEGORY_ARTIFACT_CRAFT:
            _sync_item(item, summoner)


def sync_artifact_post_enchant(summoner, log_data):
    artifact_data = log_data['response'].get('artifact', {})

    if not artifact_data or log_data['request'].get('before_after', 1) == 1:
        return

    artifact = ArtifactInstance.objects.filter(
        owner=summoner,
        com2us_id=artifact_data['rid'],
    ).first()

    if artifact:
        _change_artifact_substats(artifact, artifact_data, summoner)
        artifact.save()
        monster = artifact.assigned_to
        if monster:
            monster.default_build.clear_cache_properties()
            monster.default_build.update_stats()
            monster.default_build.save()
    else:
        assigned_to = MonsterInstance.objects.filter(
            owner=summoner,
            com2us_id=artifact_data['occupied_id']
        ).first() if artifact_data['occupied_id'] != 0 else None

        if not assigned_to:
            return "monster"

        _create_new_artifact(artifact_data, summoner, assigned_to)


def sync_artifact_enchant_craft(summoner, log_data):
    artifact_craft = log_data['response'].get('artifact_craft', {})
    artifact_data = log_data['response'].get('artifact_confirmed', {})

    _create_new_artifact_craft(artifact_craft, summoner)
    _create_new_artifact(artifact_data, summoner)


def sync_daily_reward(summoner, log_data):
    items = log_data['response'].get('item_list', [])
    runes = log_data['response'].get('rune_list', [])

    if items:
        for item in items:
            if item['item_master_type'] in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
                _sync_item(item, summoner)
            if item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                _sync_monster_piece(item, summoner)

    if runes:
        for rune in runes:
            _create_new_rune(rune, summoner)


def sync_receive_mail(summoner, log_data):
    runes = log_data['response'].get('rune_list', [])
    monsters = log_data['response'].get('unit_list', [])

    if runes:
        for rune in runes:
            _create_new_rune(rune, summoner)

    if monsters:
        for mon in monsters:
            _ = _create_new_monster(mon, summoner)


def sync_wish_reward(summoner, log_data):
    rune_data = log_data['response'].get('rune', {})
    monster_data = log_data['response'].get('unit_info', {})

    _create_new_rune(rune_data, summoner)
    _ = _create_new_monster(monster_data, summoner)


def sync_siege_crate_reward(summoner, log_data):
    selected_crate_id = log_data['request'].get('crate_index', None)
    crates = log_data['response'].get('crate_list', [])
    selected_crate = {}

    if selected_crate_id is None or not crates:
        return

    if crates:
        for crate in crates:
            if crate['crate_index'] == selected_crate_id and isinstance(crate['reward_list'], dict):
                selected_crate = crate['reward_list']
                break

        _parse_reward(selected_crate, summoner)


def sync_lab_crate_reward(summoner, log_data):
    crate = log_data['response'].get('reward_crate', {})

    if not crate:
        return

    for reward in crate.get('reward_list', []):
        item_type = reward.get('item_master_type')
        infos = reward.get('item_info_list', [])
        # parse common item drop
        if item_type in [GameItem.CATEGORY_ESSENCE, GameItem.CATEGORY_CRAFT_STUFF, GameItem.CATEGORY_ARTIFACT_CRAFT, GameItem.CATEGORY_MATERIAL_MONSTER]:
            for info in infos:
                _sync_item(info, summoner)
        # parse unit monster drop
        elif item_type == GameItem.CATEGORY_MONSTER:
            for info in infos:
                _ = _create_new_monster(info, summoner)
        # parse rune drop
        elif item_type == GameItem.CATEGORY_RUNE:
            for info in infos:
                _create_new_rune(info, summoner)
        # parse rune craft drop - grinds, echants
        elif item_type == GameItem.CATEGORY_RUNE_CRAFT:
            for info in infos:
                _create_new_rune_craft(info, summoner)


def sync_update_unit_exp_gained(summoner, log_data):
    for mon_data in log_data['response'].get('unit_list', []):
        mon = MonsterInstance.objects.filter(
            owner=summoner, 
            com2us_id=mon_data['unit_id']
        ).first()

        if not mon:
            _ = _create_new_monster(mon_data, summoner)
            return

        if mon.level != mon_data['unit_level']:
            mon.level = mon_data['unit_level']
            mon.save()


def sync_change_material(summoner, log_data):
    removed_item = log_data['response'].get('removed_item', {})
    added_item = log_data['response'].get('added_item', {})

    _sync_item(removed_item, summoner)
    _sync_item(added_item, summoner)