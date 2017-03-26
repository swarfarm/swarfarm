import dpkt
import json
from jsonschema import ErrorTree
from jsonschema.exceptions import best_match
from dateutil.parser import *
import pytz
import datetime

from django.utils.timezone import get_current_timezone

from bestiary.models import Monster
from herders.models import Building, MonsterPiece, MonsterInstance, RuneInstance, BuildingInstance

from .models import *
from .com2us_mapping import *
from com2us_json_schema import HubUserLoginValidator, VisitFriendValidator
from .smon_decryptor import decrypt_response


def parse_pcap(pcap_file):
    pcap = dpkt.pcap.Reader(pcap_file)
    streams = dict()

    # Assemble the TCP streams
    for ts, buf in pcap:
        eth = dpkt.ethernet.Ethernet(buf)
        try:
            ip = eth.data
            tcp = ip.data

            if type(tcp) == dpkt.tcp.TCP and tcp.sport == 80 and len(tcp.data) > 0:
                if tcp.ack in streams:
                    streams[tcp.ack] += tcp.data
                else:
                    streams[tcp.ack] = tcp.data
        except:
            continue

    # Find the summoner's war command somewhere in there
    for stream in streams.values():
        try:
            resp = dpkt.http.Response(stream)
            resp_data = json.loads(decrypt_response(resp.body, 2))
        except:
            continue
        else:
            if resp_data.get('command') == 'HubUserLogin' and 'unit_list' in resp_data:
                return resp_data


def validate_sw_json(data):
    # Determine if it's a friend visit or a personal data file
    if 'friend' in data:
        validator = VisitFriendValidator
    else:
        validator = HubUserLoginValidator

    # Check the submitted data against a schema and return any errors in human readable format
    error = best_match(validator.iter_errors(data))

    if error:
        return 'Error in field {}:\n{}'.format(
            '[%s]' % ']['.join(repr(index) for index in error.path),
            error.message
        )
    else:
        return None


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

        building_instance.level = level
        parsed_buildings.append(building_instance)

    # Inventory - essences and summoning pieces
    if inventory_info:
        for item in inventory_info:
            # Essence Inventory
            if item['item_master_type'] == inventory_type_map['essences']:
                essence = inventory_essence_map.get(item['item_master_id'])
                quantity = item.get('item_quantity')

                if essence and quantity:
                    parsed_inventory[essence] = quantity
            elif item['item_master_type'] == inventory_type_map['craft_stuff']:
                craft = inventory_craft_map.get(item['item_master_id'])
                quantity = item.get('item_quantity')

                if craft and quantity:
                    parsed_inventory[craft] = quantity
            elif item['item_master_type'] == inventory_type_map['monster_piece']:
                quantity = item.get('item_quantity')
                if quantity > 0:
                    mon = get_monster_from_id(item['item_master_id'])

                    if mon:
                        parsed_monster_pieces.append(MonsterPiece(
                            monster=mon,
                            pieces=quantity,
                            owner=owner,
                        ))

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

        if (level_ignored or silver_ignored or material_ignored) and not (allow_due_to_runes or allow_due_to_ld):
            continue

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
    rune.type = rune_set_map.get(rune_data.get('set_id'))

    rune.com2us_id = com2us_id
    rune.value = rune_data.get('sell_value')
    rune.slot = rune_data.get('slot_no')
    rune.stars = rune_data.get('class')
    rune.level = rune_data.get('upgrade_curr')
    original_quality = rune_data.get('extra')

    if original_quality:
        rune.original_quality = rune_quality_map[original_quality]

    # Rune stats
    main_stat = rune_data.get('pri_eff')
    if main_stat:
        rune.main_stat = rune_stat_type_map.get(main_stat[0])
        rune.main_stat_value = main_stat[1]

    innate_stat = rune_data.get('prefix_eff')
    if innate_stat:
        rune.innate_stat = rune_stat_type_map.get(innate_stat[0])
        rune.innate_stat_value = innate_stat[1]

    substats = rune_data.get('sec_eff', [])
    if len(substats) >= 1:
        rune.substat_1 = rune_stat_type_map.get(substats[0][0])
        rune.substat_1_value = substats[0][1] + substats[0][3]
        if substats[0][3]:
            rune.substat_1_craft = RuneInstance.CRAFT_GRINDSTONE
        elif substats[0][2]:
            rune.substat_1_craft = RuneInstance.CRAFT_ENCHANT_GEM

    if len(substats) >= 2:
        rune.substat_2 = rune_stat_type_map.get(substats[1][0])
        rune.substat_2_value = substats[1][1] + substats[1][3]
        if substats[1][3]:
            rune.substat_2_craft = RuneInstance.CRAFT_GRINDSTONE
        elif substats[1][2]:
            rune.substat_2_craft = RuneInstance.CRAFT_ENCHANT_GEM

    if len(substats) >= 3:
        rune.substat_3 = rune_stat_type_map.get(substats[2][0])
        rune.substat_3_value = substats[2][1] + substats[2][3]
        if substats[2][3]:
            rune.substat_3_craft = RuneInstance.CRAFT_GRINDSTONE
        elif substats[2][2]:
            rune.substat_3_craft = RuneInstance.CRAFT_ENCHANT_GEM

    if len(substats) >= 4:
        rune.substat_4 = rune_stat_type_map.get(substats[3][0])
        rune.substat_4_value = substats[3][1] + substats[3][3]
        if substats[3][3]:
            rune.substat_4_craft = RuneInstance.CRAFT_GRINDSTONE
        elif substats[3][2]:
            rune.substat_4_craft = RuneInstance.CRAFT_ENCHANT_GEM

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
        craft = RuneCraftInstance()

    craft_type_id = str(craft_data['craft_type_id'])

    quality = int(craft_type_id[-1:])
    stat = int(craft_type_id[-4:-2])
    rune_set = int(craft_type_id[:-4])

    craft.type = craft_type_map.get(craft_data['craft_type'])
    craft.quality = craft_quality_map.get(quality)
    craft.stat = rune_stat_type_map.get(stat)
    craft.rune = rune_set_map.get(rune_set)
    craft.value = craft_data['sell_value']

    return craft


