from datetime import datetime, timedelta

import pytz
from django.contrib.postgres.fields import JSONField
from django.db import models

from bestiary.models import Monster, Dungeon, Level, GameItem, Rune, RuneCraft
from herders.models import Summoner


# Abstract models for encapsulating common data like drops and log entry metadata
class LogEntry(models.Model):
    # Abstract model with basic fields required for logging anything

    TIMEZONE_SERVER_MAP = {
        'America/Los_Angeles': Summoner.SERVER_GLOBAL,
        'Europe/Berlin': Summoner.SERVER_EUROPE,
        'Asia/Seoul': Summoner.SERVER_KOREA,
        'Asia/Shanghai': Summoner.SERVER_ASIA,
    }

    wizard_id = models.BigIntegerField()
    summoner = models.ForeignKey(Summoner, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    server = models.IntegerField(choices=Summoner.SERVER_CHOICES, null=True, blank=True)

    class Meta:
        abstract = True

    def parse_common_log_data(self, log_data):
        self.wizard_id = log_data['request']['wizard_id']
        self.server = LogEntry.TIMEZONE_SERVER_MAP.get(log_data['response']['tzone'])
        self.timestamp = datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))


class ItemDrop(models.Model):
    PARSE_KEYS = (
        'mana',
        'energy',
        'crystal',
        'random_scroll',
        'material',
        'craft_stuff',
    )

    item = models.ForeignKey(GameItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.item} x{self.quantity}'

    @classmethod
    def parse(cls, key, val):
        if key == 'mana':
            log_item = cls(
                item=GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Mana'),
                quantity=val,
            )
        elif key == 'energy':
            log_item = cls(
                item=GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Energy'),
                quantity=val
            )
        elif key == 'crystal':
            log_item = cls(
                item=GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Crystal'),
                quantity=val
            )
        elif key == 'random_scroll':
            log_item = cls(
                item=GameItem.objects.get(category=GameItem.CATEGORY_SUMMON_SCROLL, com2us_id=val['item_master_id']),
                quantity=val['item_quantity'],
            )
        elif key == 'material':
            log_item = cls(
                item=GameItem.objects.get(category=GameItem.CATEGORY_ESSENCE, com2us_id=val['item_master_id']),
                quantity=val['item_quantity'],
            )
        elif key == 'craft_stuff':
            log_item = cls(
                item=GameItem.objects.get(category=GameItem.CATEGORY_CRAFT_STUFF, com2us_id=val['item_master_id']),
                quantity=val['item_quantity'],
            )
        else:
            # TODO: Implement parsing of: `costume_point`, `rune_upgrade_stone`, `summon_pieces`, `event_item`
            raise NotImplementedError(f"Can't parse item type {key} with {cls.__name__}")

        return log_item


class MonsterDrop(models.Model):
    PARSE_KEYS = (
        'unit_info',
    )
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    grade = models.IntegerField()
    level = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.monster} {self.grade}* lv.{self.level}'

    @classmethod
    def parse(cls, key, val):
        if key != 'unit_info':
            raise NotImplementedError(f"Can't parse item type {key} with {cls.__name__}")

        return cls(
            monster=Monster.objects.get(com2us_id=val['unit_master_id']),
            grade=val['class'],
            level=val['unit_level'],
        )


class MonsterPieceDrop(models.Model):
    PARSE_KEYS = (

    )

    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.monster} x{self.quantity}'


class RuneDrop(Rune):
    PARSE_KEYS = (
        'rune',
    )

    class Meta:
        abstract = True

    @classmethod
    def parse(cls, key, val):
        if key != 'rune':
            raise NotImplementedError(f"Can't parse item type {key} with {cls.__name__}")

        rune_set = cls.COM2US_TYPE_MAP[val['set_id']]
        original_quality = cls.COM2US_QUALITY_MAP[val['extra']]
        main_stat = cls.COM2US_STAT_MAP[val['pri_eff'][0]]
        main_stat_value = val['pri_eff'][1]
        innate_stat = cls.COM2US_STAT_MAP.get(val['prefix_eff'][0])
        innate_stat_value = val['prefix_eff'][1] if innate_stat else None

        substats = []
        substat_values = []

        for sub, sub_val in val['sec_eff']:
            substats.append(cls.COM2US_STAT_MAP[sub])
            substat_values.append(sub_val)

        return cls(
            type=rune_set,
            stars=val['class'],
            level=val['upgrade_curr'],
            slot=val['slot_no'],
            original_quality=original_quality,
            value=val['sell_value'],
            main_stat=main_stat,
            main_stat_value=main_stat_value,
            innate_stat=innate_stat,
            innate_stat_value=innate_stat_value,
            substats=substats,
            substat_values=substat_values,
        )


class RuneCraftDrop(RuneCraft):
    PARSE_KEYS = (

    )

    class Meta:
        abstract = True

    @classmethod
    def parse(cls, key, val):
        raise NotImplementedError()


# Data gathering model to store game API data for development and debugging purposes
class FullLog(LogEntry):
    command = models.TextField(max_length=150, db_index=True)
    request = JSONField()
    response = JSONField()


# Magic Shop
class ShopRefreshLog(LogEntry):
    slots_available = models.IntegerField(blank=True, null=True)


class ShopRefreshDrop(models.Model):
    log = models.ForeignKey(ShopRefreshLog, on_delete=models.CASCADE)
    cost = models.IntegerField()

    class Meta:
        abstract = True


class ShopRefreshItemDrop(ItemDrop, ShopRefreshDrop):
    pass


class ShopRefreshRuneDrop(RuneDrop, ShopRefreshDrop):
    pass


class ShopRefreshMonsterDrop(MonsterDrop, ShopRefreshDrop):
    pass


# Wishes
class WishLog(LogEntry):
    wish_id = models.IntegerField()
    wish_sequence = models.IntegerField()
    crystal_used = models.BooleanField()


class WishLogDrop(models.Model):
    log = models.ForeignKey(WishLog, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class WishLogItemDrop(ItemDrop, WishLogDrop):
    pass


class WishLogMonsterDrop(MonsterDrop, WishLogDrop):
    pass


class WishLogRuneDrop(RuneDrop, WishLogDrop):
    pass


# Rune Crafting
class CraftRuneLog(LogEntry, RuneDrop):
    CRAFT_LOW = 0
    CRAFT_MID = 1
    CRAFT_HIGH = 2

    CRAFT_CHOICES = [
        (CRAFT_LOW, 'Low'),
        (CRAFT_MID, 'Mid'),
        (CRAFT_HIGH, 'High'),
    ]

    craft_level = models.IntegerField(choices=CRAFT_CHOICES)


# Magic Box Crafting
class MagicBoxCraft(LogEntry):
    BOX_UNKNOWN_MAGIC = 0
    BOX_MYSTICAL_MAGIC = 1
    BOX_LEGENDARY_MAGIC = 2

    BOX_CHOICES = [
        (BOX_UNKNOWN_MAGIC, 'Unknown Magic Box'),
        (BOX_MYSTICAL_MAGIC, 'Mystical Magic Box'),
        (BOX_LEGENDARY_MAGIC, 'Legendary Magic Box'),
    ]

    box_type = models.IntegerField(choices=BOX_CHOICES)


class MagicBoxCraftDrop(models.Model):
    log = models.ForeignKey(MagicBoxCraft, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class MagicBoxCraftRuneDrop(RuneDrop, MagicBoxCraftDrop):
    pass


class MagicBoxCraftItemDrop(ItemDrop, MagicBoxCraftDrop):
    pass


class MagicBoxCraftRuneCraftDrop(RuneCraftDrop, MagicBoxCraftDrop):
    pass


# Summons
class SummonLog(LogEntry, MonsterDrop):
    item = models.ForeignKey(GameItem, on_delete=models.CASCADE, help_text='Item or currency used to summon')

    def __str__(self):
        return f'SummonLog - {self.item} - {self.monster} {self.grade}*'

    @classmethod
    def parse_summon_log(cls, summoner, log_data):
        if log_data['response']['unit_list'] is None:
            return

        for unit_info in log_data['response']['unit_list']:
            log_entry = cls.parse('unit_info', unit_info)
            log_entry.parse_common_log_data(log_data)
            log_entry.summoner = summoner

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

            log_entry.save()


# Dungeons
class DungeonLog(LogEntry):
    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    success = models.NullBooleanField(help_text='Null indicates that run was not completed')
    clear_time = models.DurationField(blank=True, null=True)

    @classmethod
    def parse_scenario_start(cls, summoner, log_data):
        log_entry = cls(summoner=summoner)

        # Partially fill common log data
        log_entry.wizard_id = log_data['request']['wizard_id']
        log_entry.battle_key = log_data['response'].get('battle_key')

        log_entry.level = Level.objects.get(
            dungeon__category=Dungeon.CATEGORY_SCENARIO,
            dungeon__pk=log_data['request']['region_id'],
            difficulty=log_data['request']['difficulty'],
            floor=log_data['request']['stage_no'],
        )

        # Remainder of information comes from BattleScenarioResult
        log_entry.save()

    @classmethod
    def parse_scenario_result(cls, summoner, log_data):
        log_entry = cls.objects.get(
            wizard_id=log_data['request']['wizard_id'],
            battle_key=log_data['request']['battle_key']
        )

        log_entry.parse_common_log_data(log_data)
        log_entry.success = log_data['request']['win_lose'] == 1
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.save()
        log_entry.parse_rewards(log_data['response']['reward'])

    @classmethod
    def parse_dungeon_result(cls, summoner, log_data):
        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        log_entry.level = Level.objects.get(
            dungeon__category=Dungeon.CATEGORY_CAIROSS,
            dungeon__pk=log_data['request']['dungeon_id'],
            floor=log_data['request']['stage_id'],
        )
        log_entry.success = log_data['request']['win_lose'] == 1
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.save()
        log_entry.parse_rewards(log_data['response']['reward'])

    def parse_rewards(self, rewards):
        for key, val in rewards.items():
            reward = None

            if key in DungeonItemDrop.PARSE_KEYS:
                reward = DungeonItemDrop.parse(key, val)
            elif key in DungeonRuneDrop.PARSE_KEYS:
                reward = DungeonRuneDrop.parse(key, val)
            elif key in DungeonMonsterDrop.PARSE_KEYS:
                reward = DungeonMonsterDrop.parse(key, val)
            elif key == 'crate':
                self.parse_rewards(val)

            if reward:
                reward.log = self
                reward.save()


class DungeonLogDrop(models.Model):
    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class DungeonItemDrop(ItemDrop, DungeonLogDrop):
    pass


class DungeonMonsterDrop(MonsterDrop, DungeonLogDrop):
    pass


class DungeonMonsterPieceDrop(MonsterPieceDrop, DungeonLogDrop):
    pass


class DungeonRuneDrop(RuneDrop, DungeonLogDrop):
    pass


class DungeonSecretDungeonDrop(DungeonLogDrop):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)


# Rift dungeon
class RiftDungeonLog(LogEntry):
    GRADE_F = 1
    GRADE_D = 2
    GRADE_C = 3
    GRADE_B_MINUS = 4
    GRADE_B = 5
    GRADE_B_PLUS = 6
    GRADE_A_MINUS = 7
    GRADE_A = 8
    GRADE_A_PLUS = 9
    GRADE_S = 10
    GRADE_SS = 11
    GRADE_SSS = 12

    GRADE_CHOICES = [
        (GRADE_F, 'F'),
        (GRADE_D, 'D'),
        (GRADE_C, 'C'),
        (GRADE_B_MINUS, 'B-'),
        (GRADE_B, 'B'),
        (GRADE_B_PLUS, 'B+'),
        (GRADE_A_MINUS, 'A-'),
        (GRADE_A, 'A'),
        (GRADE_A_PLUS, 'A+'),
        (GRADE_S, 'S'),
        (GRADE_SS, 'SS'),
        (GRADE_SSS, 'SSS'),
    ]

    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    total_damage = models.IntegerField()
    success = models.BooleanField()

    def __str__(self):
        return f'RiftDungeonLog {self.level} {self.grade}'


class RiftDungeonLogDrop(models.Model):
    log = models.ForeignKey(RiftDungeonLog, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class RiftDungeonItemDrop(ItemDrop, RiftDungeonLogDrop):
    pass


class RiftDungeonMonsterDrop(MonsterDrop, RiftDungeonLogDrop):
    pass


class RiftDungeonRuneDrop(RuneDrop, RiftDungeonLogDrop):
    pass


class RiftDungeonRuneCraftDrop(RuneCraftDrop, RiftDungeonLogDrop):
    pass


# Rift of Worlds Raid
class RiftRaidLog(LogEntry):
    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    success = models.NullBooleanField(help_text='Null indicates that run was not completed')
    contribution_amount = models.IntegerField(blank=True, null=True)


class RiftRaidLogDrop(models.Model):
    log = models.ForeignKey(RiftRaidLog, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class RiftRaidItemDrop(ItemDrop, RiftRaidLogDrop):
    pass


class RiftRaidMonsterDrop(ItemDrop, RiftRaidLogDrop):
    pass


class RiftRaidRuneCraftDrop(ItemDrop, RiftRaidLogDrop):
    pass


# World Boss
class WorldBossLog(LogEntry):
    GRADE_F = 1
    GRADE_D = 2
    GRADE_C = 3
    GRADE_B_MINUS = 4
    GRADE_B = 5
    GRADE_B_PLUS = 6
    GRADE_A_MINUS = 7
    GRADE_A = 8
    GRADE_A_PLUS = 9
    GRADE_S = 10
    GRADE_SS = 11
    GRADE_SSS = 12

    GRADE_CHOICES = [
        (GRADE_F, 'F'),
        (GRADE_D, 'D'),
        (GRADE_C, 'C'),
        (GRADE_B_MINUS, 'B-'),
        (GRADE_B, 'B'),
        (GRADE_B_PLUS, 'B+'),
        (GRADE_A_MINUS, 'A-'),
        (GRADE_A, 'A'),
        (GRADE_A_PLUS, 'A+'),
        (GRADE_S, 'S'),
        (GRADE_SS, 'SS'),
        (GRADE_SSS, 'SSS'),
    ]

    battle_key = models.BigIntegerField(null=True, blank=True)
    grade = models.IntegerField(choices=GRADE_CHOICES)
    damage = models.IntegerField()
    battle_points = models.IntegerField()
    bonus_battle_points = models.IntegerField()
    avg_monster_level = models.FloatField()
    monster_count = models.IntegerField()


class WorldBossLogDrop(models.Model):
    log = models.ForeignKey(WorldBossLog, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class WorldBossLogMonsterDrop(MonsterDrop, WorldBossLogDrop):
    pass


class WorldBossLogItemDrop(ItemDrop, WorldBossLogDrop):
    pass


class WorldBossLogRuneDrop(RuneDrop, WorldBossLogDrop):
    pass
