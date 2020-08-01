from dateutil.parser import *
from django.utils.timezone import get_current_timezone
from jsonschema.exceptions import best_match

from bestiary.models import Monster, Building, GameItem
from herders.models import MonsterInstance, RuneInstance, RuneCraftInstance, MonsterPiece, BuildingInstance, ArtifactInstance, ArtifactCraftInstance
from herders.profile_schema import HubUserLoginValidator, VisitFriendValidator

# Game ID to field mappings
inventory_enhance_monster_map = {
    142110115: 'water_angelmon',
    142120115: 'fire_angelmon',
    142130115: 'wind_angelmon',
    142140115: 'light_angelmon',
    142150115: 'dark_angelmon',
    182110115: 'water_king_angelmon',
    182120115: 'fire_king_angelmon',
    182130115: 'wind_king_angelmon',
    182140115: 'light_king_angelmon',
    182150115: 'dark_king_angelmon',
    143140220: 'rainbowmon_2_20',
    143140301: 'rainbowmon_3_1',
    143140325: 'rainbowmon_3_25',
    143140401: 'rainbowmon_4_1',
    143140430: 'rainbowmon_4_30',
    143140501: 'rainbowmon_5_1',
    151050101: 'devilmon',
    217140115: 'super_angelmon,'
}


inventory_essence_map = {
    11006: "storage_magic_low",
    12006: "storage_magic_mid",
    13006: "storage_magic_high",
    11001: "storage_water_low",
    12001: "storage_water_mid",
    13001: "storage_water_high",
    11002: "storage_fire_low",
    12002: "storage_fire_mid",
    13002: "storage_fire_high",
    11003: "storage_wind_low",
    12003: "storage_wind_mid",
    13003: "storage_wind_high",
    11004: "storage_light_low",
    12004: "storage_light_mid",
    13004: "storage_light_high",
    11005: "storage_dark_low",
    12005: "storage_dark_mid",
    13005: "storage_dark_high",
}

inventory_craft_map = {
    1001: 'wood',
    1002: 'leather',
    1003: 'rock',
    1004: 'ore',
    1005: 'mithril',
    1006: 'cloth',
    2001: 'rune_piece',
    3001: 'powder',
    4001: 'symbol_harmony',
    4002: 'symbol_transcendance',
    4003: 'symbol_chaos',
    5001: 'crystal_water',
    5002: 'crystal_fire',
    5003: 'crystal_wind',
    5004: 'crystal_light',
    5005: 'crystal_dark',
    6001: 'crystal_magic',
    7001: 'crystal_pure',
}


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
    parsed_artifacts = []
    parsed_artifact_crafts = []
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
    artifact_info = data.get('artifacts')  # Optional
    artifact_craft_info = data.get('artifact_crafts')  # Optional

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
            if item['item_master_type'] == GameItem.CATEGORY_ESSENCE:
                essence = inventory_essence_map.get(item['item_master_id'])
                quantity = item.get('item_quantity')

                if essence and quantity:
                    parsed_inventory[essence] = quantity
            elif item['item_master_type'] == GameItem.CATEGORY_CRAFT_STUFF:
                craft = inventory_craft_map.get(item['item_master_id'])
                quantity = item.get('item_quantity')

                if craft and quantity:
                    parsed_inventory[craft] = quantity
            elif item['item_master_type'] == GameItem.CATEGORY_MONSTER_PIECE:
                quantity = item.get('item_quantity')
                if quantity > 0:
                    mon = get_monster_from_id(item['item_master_id'])

                    if mon:
                        parsed_monster_pieces.append(MonsterPiece(
                            monster=mon,
                            pieces=quantity,
                            owner=owner,
                        ))
            elif item['item_master_type'] == GameItem.CATEGORY_MATERIAL_MONSTER:
                monster = inventory_enhance_monster_map.get(item['item_master_id'])
                quantity = item.get('item_quantity')

                if monster and quantity:
                    parsed_inventory[monster] = quantity
            elif item['item_master_type'] == GameItem.CATEGORY_ARTIFACT_CRAFT:
                quantity = item.get('item_quantity')
                if quantity:
                    parsed_inventory['conversion_stone'] = quantity

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

        if mon.monster.archetype == Monster.ARCHETYPE_MATERIAL:
            mon.fodder = True
            mon.priority = MonsterInstance.PRIORITY_DONE

        # Lock a monster if it's locked in game
        if options['lock_monsters']:
            mon.ignore_for_fusion = locked_mons is not None and mon.com2us_id in locked_mons

        # Equipped runes and artifacts
        equipped_runes = unit_info.get('runes')
        equipped_artifacts = unit_info.get('artifacts')

        # Check import options to determine if monster should be saved
        level_ignored = mon.stars < options['minimum_stars']
        silver_ignored = options['ignore_silver'] and not mon.monster.can_awaken
        material_ignored = options['ignore_material'] and mon.monster.archetype == Monster.ARCHETYPE_MATERIAL
        allow_due_to_runes = options['except_with_runes'] and (len(equipped_runes) > 0 or len(equipped_artifacts) > 0)
        allow_due_to_ld = options['except_light_and_dark'] and mon.monster.element in [Monster.ELEMENT_DARK, Monster.ELEMENT_LIGHT] and mon.monster.archetype != Monster.ARCHETYPE_MATERIAL
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

        for artifact_data in equipped_artifacts:
            artifact = parse_artifact_data(artifact_data, owner)
            if artifact:
                artifact.owner = owner
                artifact.assigned_to = mon
                parsed_artifacts.append(artifact)

    # Extract grindstones/enchant gems
    if craft_info:
        for craft_data in craft_info:
            craft = parse_rune_craft_data(craft_data, owner)
            if craft:
                craft.owner = owner
                parsed_rune_crafts.append(craft)

    # Extract artifact inventory
    if artifact_info:
        for artifact_data in artifact_info:
            artifact = parse_artifact_data(artifact_data, owner)
            if artifact:
                artifact.owner = owner
                artifact.assigned_to = None
                parsed_artifacts.append(artifact)

    if artifact_craft_info:
        for craft_data in artifact_craft_info:
            craft = parse_artifact_craft_data(craft_data, owner)
            if craft:
                craft.owner = owner
                parsed_artifact_crafts.append(craft)

    import_results = {
        'wizard_id': wizard_id,
        'monsters': parsed_mons,
        'monster_pieces': parsed_monster_pieces,
        'runes': parsed_runes,
        'rune_crafts': parsed_rune_crafts,
        'artifacts': parsed_artifacts,
        'artifact_crafts': parsed_artifact_crafts,
        'inventory': parsed_inventory,
        'buildings': parsed_buildings,
        'rta_assignments': data['world_arena_rune_equip_list']
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
    rune.type = RuneInstance.COM2US_TYPE_MAP[rune_data['set_id']]
    rune.com2us_id = com2us_id
    rune.value = rune_data.get('sell_value')
    rune.slot = rune_data.get('slot_no')
    stars = rune_data.get('class')
    if stars > 10:
        stars -= 10
        rune.ancient = True
    rune.stars = stars
    rune.level = rune_data.get('upgrade_curr')
    rune.original_quality = RuneInstance.COM2US_QUALITY_MAP.get(rune_data.get('extra'))

    # Rune stats
    main_stat = rune_data.get('pri_eff')
    if main_stat:
        rune.main_stat = RuneInstance.COM2US_STAT_MAP[main_stat[0]]
        rune.main_stat_value = main_stat[1]

    innate_stat = rune_data.get('prefix_eff')
    if innate_stat:
        rune.innate_stat = RuneInstance.COM2US_STAT_MAP.get(innate_stat[0])
        rune.innate_stat_value = innate_stat[1]

    substats = rune_data.get('sec_eff', [])
    rune.substats = []
    rune.substat_values = []
    rune.substats_enchanted = []
    rune.substats_grind_value = []

    for substat in substats:
        substat_type = RuneInstance.COM2US_STAT_MAP[substat[0]]
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
    # [-1:] = quality
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
    craft.quantity = craft_data.get('amount', 1)
    craft.value = craft_data['sell_value']

    return craft


def parse_artifact_data(artifact_data, owner):
    com2us_id = artifact_data.get('rid')

    artifact = ArtifactInstance.objects.filter(com2us_id=com2us_id, owner=owner).first()

    if not artifact:
        artifact = ArtifactInstance(owner=owner)

    # Basic artifact data
    artifact.slot = artifact.COM2US_SLOT_MAP[artifact_data['type']]
    if artifact.slot == artifact.SLOT_ELEMENTAL:
        artifact.archetype = None
        artifact.element = artifact.COM2US_ELEMENT_MAP[artifact_data['attribute']]
    else:
        artifact.element = None
        artifact.archetype = artifact.COM2US_ARCHETYPE_MAP[artifact_data['unit_style']]

    artifact.quality = artifact.COM2US_QUALITY_MAP[artifact_data['rank']]
    artifact.original_quality = artifact.COM2US_QUALITY_MAP[artifact_data['natural_rank']]
    artifact.level = artifact_data['level']

    # Stats and effects
    main_eff = artifact_data['pri_effect']
    artifact.main_stat = artifact.COM2US_MAIN_STAT_MAP[main_eff[0]]
    artifact.main_stat_value = main_eff[1]

    artifact.effects = []
    artifact.effects_value = []
    artifact.effects_upgrade_count = []
    artifact.effects_reroll_count = []
    for sec_eff in artifact_data['sec_effects']:
        artifact.effects.append(sec_eff[0])
        artifact.effects_value.append(sec_eff[1])
        artifact.effects_upgrade_count.append(sec_eff[2])
        artifact.effects_reroll_count.append(sec_eff[4])

    return artifact


def parse_artifact_craft_data(craft_data, owner):
    # master_id = 12 digit number
    # Digits:
    #   [0] = always 1, skip
    #   [1:3] = artifact type
    #   [3:5] = element
    #   [5:7] = unit archetype
    #   [7:9] = quality
    #   [9:] = effect

    com2us_id = craft_data['rid']
    craft = ArtifactCraftInstance.objects.filter(com2us_id=com2us_id, owner=owner).first()

    if not craft:
        craft = ArtifactCraftInstance(com2us_id=com2us_id, owner=owner)

    craft_type_id = str(craft_data['master_id'])
    artifact_type = int(craft_type_id[1:3])
    unit_element = int(craft_type_id[3:5])
    unit_archetype = int(craft_type_id[5:7])
    quality = int(craft_type_id[7:9])
    effect = int(craft_type_id[9:])

    craft.slot = ArtifactCraftInstance.COM2US_SLOT_MAP.get(artifact_type)
    craft.element = ArtifactCraftInstance.COM2US_ELEMENT_MAP.get(unit_element) if unit_element else None
    craft.archetype = ArtifactCraftInstance.COM2US_ARCHETYPE_MAP.get(unit_archetype) if unit_archetype else None
    craft.quality = ArtifactCraftInstance.COM2US_QUALITY_MAP.get(quality)
    craft.effect = ArtifactCraftInstance.COM2US_EFFECT_MAP.get(effect)
    craft.quantity = craft_data.get('amount', 1)

    return craft
