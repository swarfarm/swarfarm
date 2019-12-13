
import json

import dpkt
from dateutil.parser import *
from django.utils.timezone import get_current_timezone
from jsonschema.exceptions import best_match

from bestiary import com2us_mapping
from bestiary.com2us_data_parser import decrypt_response
from bestiary.models import Monster, Building
from herders.models import MonsterInstance, RuneInstance, RuneCraftInstance, MonsterPiece, BuildingInstance
from herders.profile_schema import HubUserLoginValidator, VisitFriendValidator


def validate_sw_json(data, summoner):
    validation_errors = []

    # Determine if it's a friend visit or a personal data file
    if 'friend' in data:
        validator = VisitFriendValidator
    else:
        validator = HubUserLoginValidator

    # Check the submitted data against a schema and return any errors in human readable format
    schema_error = best_match(validator.iter_errors(data))

    if schema_error:
        schema_error = 'Error in field {}:\n{}'.format(
            '[%s]' % ']['.join(repr(index) for index in schema_error.path),
            schema_error.message
        )
    else:
        # Do some supplementary checking
        if 'friend' in data:
            wizard_id = data['friend']['unit_list'][0]['wizard_id']
        else:
            wizard_id = data['wizard_info']['wizard_id']

        # Check that the com2us ID matches previously imported value
        if summoner.com2us_id is not None and summoner.com2us_id != wizard_id:
            validation_errors.append('Uploaded data does not match account from previous import. Are you sure you want to upload this file?')

    return schema_error, validation_errors


def parse_sw_json(data, owner, options):
    wizard_id = None
    parsed_runes = []
    parsed_rune_crafts = []
    parsed_mons = []
    parsed_inventory = {}
    parsed_monster_pieces = []
    parsed_buildings = []

    # Grab the friend
    if data.get('command') == 'VisitFriend':
        data = data['friend']

    if 'wizard_info' in data:
        wizard_id = data['wizard_info'].get('wizard_id')

    building_list = data['building_list']
    deco_list = data['deco_list']
    inventory_info = data.get('inventory_info')  # Optional
    unit_list = data['unit_list']
    runes_info = data.get('runes')  # Optional
    locked_mons = data.get('unit_lock_list')  # Optional
    craft_info = data.get('rune_craft_item_list')  # Optional

    # Buildings
    storage_building_id = None
    for building in building_list:
        if building:
            # Find which one is the storage building
            if building.get('building_master_id') == 25:
                storage_building_id = building.get('building_id')
                break

    for deco in deco_list:
        try:
            base_building = Building.objects.get(com2us_id=deco['master_id'])
        except Building.DoesNotExist:
            continue

        level = deco['level']

        try:
            building_instance = BuildingInstance.objects.get(owner=owner, building=base_building)
        except BuildingInstance.DoesNotExist:
            building_instance = BuildingInstance(owner=owner, building=base_building)
        except BuildingInstance.MultipleObjectsReturned:
            # Should only be 1 ever - use the first and delete the others.
            building_instance = BuildingInstance.objects.filter(owner=owner, building=base_building).first()
            BuildingInstance.objects.filter(owner=owner, building=base_building).exclude(pk=building_instance.pk).delete()

        building_instance.level = level
        parsed_buildings.append(building_instance)

    # Inventory - essences and summoning pieces
    if inventory_info:
        for item in inventory_info:
            # Essence Inventory
            if item['item_master_type'] == com2us_mapping.inventory_type_map['essences']:
                essence = com2us_mapping.inventory_essence_map.get(item['item_master_id'])
                quantity = item.get('item_quantity')

                if essence and quantity:
                    parsed_inventory[essence] = quantity
            elif item['item_master_type'] == com2us_mapping.inventory_type_map['craft_stuff']:
                craft = com2us_mapping.inventory_craft_map.get(item['item_master_id'])
                quantity = item.get('item_quantity')

                if craft and quantity:
                    parsed_inventory[craft] = quantity
            elif item['item_master_type'] == com2us_mapping.inventory_type_map['monster_piece']:
                quantity = item.get('item_quantity')
                if quantity > 0:
                    mon = get_monster_from_id(item['item_master_id'])

                    if mon:
                        parsed_monster_pieces.append(MonsterPiece(
                            monster=mon,
                            pieces=quantity,
                            owner=owner,
                        ))
            elif item['item_master_type'] == com2us_mapping.inventory_type_map['enhancing_monster']:
                monster = com2us_mapping.inventory_enhance_monster_map.get(item['item_master_id'])
                quantity = item.get('item_quantity')

                if monster and quantity:
                    parsed_inventory[monster] = quantity

    # Extract Rune Inventory (unequipped runes)
    if runes_info:
        for rune_data in runes_info:
            rune = parse_rune_data(rune_data, owner)
            if rune:
                rune.owner = owner
                rune.assigned_to = None
                parsed_runes.append(rune)

    # Extract monsters
    for unit_info in unit_list:
        # Get base monster type
        com2us_id = unit_info.get('unit_id')
        monster_type_id = str(unit_info.get('unit_master_id'))
        mon = None

        if not options['clear_profile']:
            mon = MonsterInstance.objects.filter(com2us_id=com2us_id, owner=owner).first()

        if not mon:
            mon = MonsterInstance()
            is_new = True
        else:
            is_new = False

        mon.com2us_id = com2us_id

        # Base monster
        try:
            mon.monster = Monster.objects.get(com2us_id=monster_type_id)
        except Monster.DoesNotExist:
            # Unable to find a matching monster in the database - either crap data or brand new monster. Don't parse it.
            continue

        mon.stars = unit_info.get('class')
        mon.level = unit_info.get('unit_level')

        skills = unit_info.get('skills', [])
        if len(skills) >= 1:
            mon.skill_1_level = skills[0][1]
        if len(skills) >= 2:
            mon.skill_2_level = skills[1][1]
        if len(skills) >= 3:
            mon.skill_3_level = skills[2][1]
        if len(skills) >= 4:
            mon.skill_4_level = skills[3][1]

        try:
            created_date = get_current_timezone().localize(parse(unit_info.get('create_time')), is_dst=False)
            mon.created = created_date
        except (ValueError, TypeError):
            mon.created = None

        mon.owner = owner
        mon.in_storage = unit_info.get('building_id') == storage_building_id

        # Set priority levels
        if options['default_priority'] and is_new:
            mon.priority = options['default_priority']

        if mon.monster.archetype == Monster.TYPE_MATERIAL:
            mon.fodder = True
            mon.priority = MonsterInstance.PRIORITY_DONE

        # Lock a monster if it's locked in game
        if options['lock_monsters']:
            mon.ignore_for_fusion = locked_mons is not None and mon.com2us_id in locked_mons

        # Equipped runes
        equipped_runes = unit_info.get('runes')

        # Check import options to determine if monster should be saved
        level_ignored = mon.stars < options['minimum_stars']
        silver_ignored = options['ignore_silver'] and not mon.monster.can_awaken
        material_ignored = options['ignore_material'] and mon.monster.archetype == Monster.TYPE_MATERIAL
        allow_due_to_runes = options['except_with_runes'] and len(equipped_runes) > 0
        allow_due_to_ld = options['except_light_and_dark'] and mon.monster.element in [Monster.ELEMENT_DARK, Monster.ELEMENT_LIGHT] and mon.monster.archetype != Monster.TYPE_MATERIAL
        allow_due_to_fusion = options['except_fusion_ingredient'] and mon.monster.fusion_food

        should_be_skipped = any([level_ignored, silver_ignored, material_ignored])
        import_anyway = any([allow_due_to_runes, allow_due_to_ld, allow_due_to_fusion])

        if should_be_skipped and not import_anyway:
            continue

        # Set custom name if homunculus
        custom_name = unit_info.get('homunculus_name')
        if unit_info.get('homunculus') and custom_name:
            mon.custom_name = custom_name

        parsed_mons.append(mon)

        # Sometimes the runes are a dict or a list in the json. Convert to list.
        if isinstance(equipped_runes, dict):
            equipped_runes = equipped_runes.values()

        for rune_data in equipped_runes:
            rune = parse_rune_data(rune_data, owner)
            if rune:
                rune.owner = owner
                rune.assigned_to = mon
                parsed_runes.append(rune)

    # Extract grindstones/enchant gems
    if craft_info:
        for craft_data in craft_info:
            craft = parse_rune_craft_data(craft_data, owner)
            if craft:
                craft.owner = owner
                parsed_rune_crafts.append(craft)

    import_results = {
        'wizard_id': wizard_id,
        'monsters': parsed_mons,
        'monster_pieces': parsed_monster_pieces,
        'runes': parsed_runes,
        'crafts': parsed_rune_crafts,
        'inventory': parsed_inventory,
        'buildings': parsed_buildings,
    }

    return import_results


def get_monster_from_id(com2us_id):
    try:
        return Monster.objects.get(com2us_id=com2us_id)
    except (TypeError, ValueError):
        raise ValueError('Unable to find monster matching ID ' + str(com2us_id))
    except Monster.DoesNotExist:
        return None


def parse_rune_data(rune_data, owner):
    com2us_id = rune_data.get('rune_id')

    rune = RuneInstance.objects.filter(com2us_id=com2us_id, owner=owner).first()

    if not rune:
        rune = RuneInstance()

    # Basic rune info
    rune.type = com2us_mapping.rune_set_map.get(rune_data.get('set_id'))

    rune.com2us_id = com2us_id
    rune.value = rune_data.get('sell_value')
    rune.slot = rune_data.get('slot_no')
    stars = rune_data.get('class')
    if stars > 10:
        stars -= 10
        rune.ancient = True
    rune.stars = stars
    rune.level = rune_data.get('upgrade_curr')
    original_quality = rune_data.get('extra')

    if original_quality:
        if original_quality > 10:
            original_quality -= 10

        rune.original_quality = com2us_mapping.rune_quality_map[original_quality]

    # Rune stats
    main_stat = rune_data.get('pri_eff')
    if main_stat:
        rune.main_stat = com2us_mapping.rune_stat_type_map.get(main_stat[0])
        rune.main_stat_value = main_stat[1]

    innate_stat = rune_data.get('prefix_eff')
    if innate_stat:
        rune.innate_stat = com2us_mapping.rune_stat_type_map.get(innate_stat[0])
        rune.innate_stat_value = innate_stat[1]

    substats = rune_data.get('sec_eff', [])
    rune.substats = []
    rune.substat_values = []
    rune.substats_enchanted = []
    rune.substats_grind_value = []

    for substat in substats:
        substat_type = com2us_mapping.rune_stat_type_map.get(substat[0])
        substat_value = substat[1]
        enchanted = substat[2] == 1
        grind_value = substat[3]

        rune.substats.append(substat_type)
        rune.substat_values.append(substat_value)
        rune.substats_enchanted.append(enchanted)
        rune.substats_grind_value.append(grind_value)

    return rune


def parse_rune_craft_data(craft_data, owner):
    # craft_type_id = 5 digit number
    # Work backwards to figure it out
    # [:-1] = quality
    # [-4:-2] = stat
    # [:-4] = rune set

    com2us_id = craft_data['craft_item_id']
    craft = RuneCraftInstance.objects.filter(com2us_id=com2us_id, owner=owner).first()

    if not craft:
        craft = RuneCraftInstance(com2us_id=com2us_id, owner=owner)

    craft_type_id = str(craft_data['craft_type_id'])

    quality = int(craft_type_id[-1:])
    stat = int(craft_type_id[-4:-2])
    rune_set = int(craft_type_id[:-4])

    craft.type = RuneCraftInstance.COM2US_CRAFT_TYPE_MAP.get(craft_data['craft_type'])
    craft.quality = RuneCraftInstance.COM2US_QUALITY_MAP.get(quality)
    craft.stat = RuneCraftInstance.COM2US_STAT_MAP.get(stat)
    craft.rune = RuneCraftInstance.COM2US_TYPE_MAP.get(rune_set)
    craft.value = craft_data['sell_value']

    return craft
