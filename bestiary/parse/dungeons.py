from celery import shared_task
from django.core.cache import cache

from bestiary.models import Dungeon, SecretDungeon, Level, Monster, Wave, Enemy
from bestiary.parse import game_data


# Game data parsing
def scenarios():
    # Extract names from world map strings by filtering out names that are not for scenarios
    scenario_names = {
        row['region id']: game_data.strings.WORLD_MAP_DUNGEON_NAMES[row['world id']] for row in game_data.tables.WORLD_MAP.values() if row['type'] == 3
    }

    for scenario_id, raw in game_data.tables.SCENARIO_LEVELS.items():
        region_id = raw['region id']
        dungeon, created = Dungeon.objects.update_or_create(
            com2us_id=region_id,
            category=Dungeon.CATEGORY_SCENARIO,
            defaults={
                'name': scenario_names.get(region_id, 'UNKNOWN')
            }
        )

        if created:
            print(f'Added new dungeon {dungeon}')

        level, created = Level.objects.update_or_create(
            dungeon=dungeon,
            difficulty=raw['difficulty'],
            floor=raw['stage no'],
            defaults={
                'energy_cost': raw['energy cost'],
                'frontline_slots': raw['player unit slot'],
                'backline_slots': None,
                'total_slots': raw['player unit slot'],
            }
        )

        if created:
            print(f'Added new level for {dungeon} - {level}')


def dimensional_hole():
    for dungeon_id, raw in game_data.tables.DIMENSIONAL_HOLE_DUNGEONS.items():
        try:
            dungeon_name = game_data.strings.DIMENSIONAL_HOLE_DUNGEON_NAMES[raw['dimension id'] * 10 + raw['dungeon type']]
        except KeyError:
            # Use the korean string
            dungeon_name = raw['desc']

        if raw['dungeon type'] == 2:
            # 2A dungeon - append monster name to dungeon name
            monster = Monster.objects.get(com2us_id=raw['limit text unitid'])
            dungeon_name += f' - {monster.name}'

        dungeon, created = Dungeon.objects.update_or_create(
            com2us_id=dungeon_id,
            category=Dungeon.CATEGORY_DIMENSIONAL_HOLE,
            defaults={
                'name': dungeon_name,
                'enabled': bool(raw['enable']),
                'icon': Monster.objects.get(com2us_id=raw['thumbnail iid']).image_filename,
            }
        )

        if created:
            print(f'Added new dungeon {dungeon}')

        level_ids = []
        for difficulty in range(len(raw['boss unit id'])):
            level, created = Level.objects.update_or_create(
                dungeon=dungeon,
                floor=difficulty + 1,
                defaults={
                    'energy_cost': 1,
                    'frontline_slots': 4,
                    'backline_slots': None,
                    'total_slots': 4,
                }
            )
            level_ids.append(level.pk)

            if created:
                print(f'Added new level for {dungeon} - {level}')

        Level.objects.filter(dungeon=dungeon).exclude(pk__in=level_ids).delete()


def rift_raids():
    for master_id, raw in game_data.tables.RIFT_RAIDS.items():
        dungeon, created = Dungeon.objects.update_or_create(
            com2us_id=raw['raid id'],
            category=Dungeon.CATEGORY_RIFT_OF_WORLDS_RAID,
            defaults={
                'name': 'Rift Raid',
            }
        )

        if created:
            print(f'Added new dungeon {dungeon.name} - {dungeon.slug}')

        level, created = Level.objects.update_or_create(
            dungeon=dungeon,
            floor=raw['stage id'],
            defaults={
                "energy_cost": raw['cost energy'],
                "frontline_slots": 4,
                "backline_slots": 4,
                "total_slots": 6,
            },
        )

        if created:
            print(
                f'Added new level for {dungeon.name} - {level.get_difficulty_display() if level.difficulty is not None else ""} B{1}')


def elemental_rifts():
    for master_id, raw in game_data.tables.ELEMENTAL_RIFT_DUNGEONS.items():
        if raw['enable']:
            # Dungeon name is name of the boss
            name = game_data.strings.MONSTER_NAMES[raw['unit id']]
            dungeon, created = Dungeon.objects.update_or_create(
                com2us_id=master_id,
                category=Dungeon.CATEGORY_RIFT_OF_WORLDS_BEASTS,
                defaults={
                    'name': name
                }
            )

            if created:
                print(f'Added new dungeon {dungeon.name} - {dungeon.slug}')

            # Create a single level referencing this dungeon
            level, created = Level.objects.update_or_create(
                dungeon=dungeon,
                floor=1,
                defaults={
                    'energy_cost': raw['cost energy'],
                    'frontline_slots': 4,
                    'backline_slots': 4,
                    'total_slots': 6,
                }
            )

            if created:
                print(
                    f'Added new level for {dungeon.name} - {level.get_difficulty_display() if level.difficulty is not None else ""} B{1}')


def secret_dungeons():
    for instance_id, raw in game_data.tables.SECRET_DUNGEONS.items():
        monster_id = raw['summon pieces']
        monster = Monster.objects.get(com2us_id=monster_id)

        dungeon, created = SecretDungeon.objects.update_or_create(
            com2us_id=instance_id,
            category=SecretDungeon.CATEGORY_SECRET,
            defaults={
                'monster': monster,
                'name': f'{monster.get_element_display()} {monster.name} Secret Dungeon',
            }
        )

        if created:
            print(f'Added new secret dungeon {dungeon.name} - {dungeon.slug}')

        # Create a single level referencing this dungeon
        level, created = Level.objects.update_or_create(
            dungeon=dungeon,
            floor=1,
            defaults={
                'energy_cost': 3,
                'frontline_slots': 5,
                'backline_slots': None,
                'total_slots': 5,
            }
        )

        if created:
            print(f'Added new level for {dungeon.name} - {level.get_difficulty_display() if level.difficulty is not None else ""} B{1}')


# Scenario/dungeon enemy information from game API responses
def _parse_wave_data(level, data):
    waves = []
    for wave_idx, wave_data in enumerate(data):
        wave, _ = Wave.objects.update_or_create(
            order=wave_idx,
            level=level
        )
        waves.append(wave.pk)

        # Parse each enemy in the wave
        enemies = []
        for enemy_idx, enemy_data in enumerate(wave_data):
            enemy, _ = Enemy.objects.update_or_create(
                wave=wave,
                com2us_id=enemy_data.get('unit_id'),
                defaults={
                    'order': enemy_idx,
                    'monster': Monster.objects.get(com2us_id=enemy_data['unit_master_id']),
                    'stars': enemy_data['class'],
                    'level': enemy_data['unit_level'],
                    'hp': enemy_data['con'] * 15,
                    'attack': enemy_data['atk'],
                    'defense': enemy_data['def'],
                    'speed': enemy_data['spd'],
                    'resist': enemy_data['resist'],
                    'boss': bool(enemy_data.get('boss', False)),
                    'crit_bonus': enemy_data.get('critical_bonus', 0),
                    'crit_damage_reduction': enemy_data.get('crit_damage_reduction', 0),
                    'accuracy_bonus': enemy_data.get('hit_bonus', 0),
                }
            )
            enemies.append(enemy.pk)

        # Delete previously existing enemies for this wave that were not updated/created
        Enemy.objects.filter(wave=wave).exclude(pk__in=enemies).delete()

    # Delete previously existing waves for this level that were not updated/created
    Wave.objects.filter(level=level).exclude(pk__in=waves).delete()


@shared_task
def scenario_waves(log_data):
    level = Level.objects.get(
        dungeon__category=Dungeon.CATEGORY_SCENARIO,
        dungeon__com2us_id=log_data['request']['region_id'],
        floor=log_data['request']['stage_no'],
        difficulty=log_data['request']['difficulty'],
    )
    _parse_wave_data(level, log_data['response']['opp_unit_list'])


@shared_task
def dungeon_waves(log_data):
    level = Level.objects.get(
        dungeon__category=Dungeon.CATEGORY_CAIROS,
        dungeon__com2us_id=log_data['request']['dungeon_id'],
        floor=log_data['request']['stage_id'],
    )
    _parse_wave_data(level, log_data['response']['dungeon_unit_list'])


@shared_task
def dimensional_hole_waves(log_data):
    if (log_data['request']['dungeon_id'] / 100) % 10 == 3:
        return # Predator
    level = Level.objects.get(
        dungeon__category=Dungeon.CATEGORY_DIMENSIONAL_HOLE,
        dungeon__com2us_id=log_data['request']['dungeon_id'],
        floor=log_data['request']['difficulty'],
    )
    _parse_wave_data(level, log_data['response']['dungeon_units'])


command_map = {
    'BattleScenarioStart': {
        'fn': scenario_waves,
        'cache keys': [
            'region_id',
            'stage_no',
            'difficulty',
        ],
    },
    'BattleDungeonStart': {
        'fn': dungeon_waves,
        'cache keys': [
            'dungeon_id',
            'stage_id',
        ],
    },
    'BattleDimensionHoleDungeonStart': {
        'fn': dimensional_hole_waves,
        'cache keys': [
            'dungeon_id',
            'difficulty',
        ],
    },
}


def _get_command_cache_key(log_data):
    command = log_data['request']['command']
    keys = command_map[command]['cache keys']
    cache_key_elements = [command] + [
        str(log_data['request'][key]) for key in keys
    ]
    return '-'.join(cache_key_elements)


def _is_update_required(log_data):
    k = _get_command_cache_key(log_data)
    return


UPDATE_INTERVAL = 24 * 60 * 60  # One day


def dispatch_dungeon_wave_parse(summoner, log_data):
    k = _get_command_cache_key(log_data)
    if not cache.get(k):
        command = log_data['request']['command']
        command_map[command]['fn'].delay(log_data)
        cache.set(k, True, UPDATE_INTERVAL)

