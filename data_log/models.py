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
        # For when drops are in a key: value format from game API
        'mana',
        'energy',
        'crystal',
    )

    PARSE_ITEM_TYPES = (
        # For when drops have a master_item_id and master_item_type specified
        GameItem.CATEGORY_CURRENCY,
        GameItem.CATEGORY_SUMMON_SCROLL,
        GameItem.CATEGORY_ESSENCE,
        GameItem.CATEGORY_CRAFT_STUFF,
    )

    item = models.ForeignKey(GameItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.item} x{self.quantity}'

    @classmethod
    def parse(cls, **kwargs):
        key = kwargs.get('key')
        val = kwargs.get('val')
        master_type = kwargs.get('item_master_type') or kwargs.get('type')
        master_id = kwargs.get('item_master_id') or kwargs.get('id')

        if key and val is not None:
            # Dungeon drop parsing
            if key == 'mana':
                item = GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Mana')
                quantity = val
            elif key == 'energy':
                item = GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Energy')
                quantity = val
            elif key == 'crystal':
                item = GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Crystal')
                quantity = val
            else:
                raise ValueError(f"Can't parse item type {key} with {cls.__name__}")
        elif master_type and master_id:
            # type and ID parsing
            quantity = kwargs.get('amount') or kwargs.get('item_quantity') or kwargs.get('quantity')

            if quantity is None:
                raise ValueError('Quantity not found')

            if master_type not in cls.PARSE_ITEM_TYPES:
                raise ValueError(f"Can't parse item type {master_type} with {cls.__name__}")

            item = GameItem.objects.get(category=master_type, com2us_id=master_id)
        else:
            raise ValueError('Must specify either (key, val) kwargs or (item_master_type, item_master_id, quantity) kwargs')

        if item and quantity:
            log_item = cls(
                item=item,
                quantity=quantity,
            )
            return log_item


class MonsterDrop(models.Model):
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_MONSTER,
    )

    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    grade = models.IntegerField()
    level = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.monster} {self.grade}* lv.{self.level}'

    @classmethod
    def parse(cls, **monster_info):
        com2us_id = monster_info.get('unit_master_id') or monster_info.get('item_master_id')
        return cls(
                monster=Monster.objects.get(com2us_id=com2us_id),
                grade=monster_info['class'],
                level=monster_info.get('unit_level', 1),
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
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_RUNE,
    )

    class Meta:
        abstract = True

    @classmethod
    def parse(cls, **rune_data):
        rune_set = cls.COM2US_TYPE_MAP[rune_data['set_id']]
        original_quality = cls.COM2US_QUALITY_MAP[rune_data['extra']]
        main_stat = cls.COM2US_STAT_MAP[rune_data['pri_eff'][0]]
        main_stat_value = rune_data['pri_eff'][1]
        innate_stat = cls.COM2US_STAT_MAP.get(rune_data['prefix_eff'][0])
        innate_stat_value = rune_data['prefix_eff'][1] if innate_stat else None

        substats = []
        substat_values = []

        for sub, sub_val, *rest in rune_data['sec_eff']:
            substats.append(cls.COM2US_STAT_MAP[sub])
            substat_values.append(sub_val)

        return cls(
            type=rune_set,
            stars=rune_data['class'],
            level=rune_data['upgrade_curr'],
            slot=rune_data['slot_no'],
            original_quality=original_quality,
            value=rune_data['sell_value'],
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
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_RUNE_CRAFT,
    )

    class Meta:
        abstract = True

    @classmethod
    def parse(cls, **craft_data):
        craft_type_id = str(craft_data['craft_type_id'])
        craft_type = craft_data['craft_type']

        return cls(
            type=cls.COM2US_CRAFT_TYPE_MAP[craft_type],
            rune=cls.COM2US_TYPE_MAP[int(craft_type_id[:-4])],
            quality=cls.COM2US_QUALITY_MAP[int(craft_type_id[-1:])],
            stat=cls.COM2US_STAT_MAP[int(craft_type_id[-4:-2])],
        )


# Data gathering model to store game API data for development and debugging purposes
class FullLog(LogEntry):
    command = models.TextField(max_length=150, db_index=True)
    request = JSONField()
    response = JSONField()


# Magic Shop
class ShopRefreshLog(LogEntry):
    slots_available = models.IntegerField(blank=True, null=True)

    @classmethod
    def parse_shop_refresh(cls, summoner, log_data):
        if log_data['response']['market_info']['update_remained'] != 3600:
            # Ignore any log that does not have the full hour of refresh time indicating it is brand new.
            return

        log = cls(summoner=summoner)
        log.parse_common_log_data(log_data)
        log.slots_available = log_data['response']['market_info']['open_slots']
        log.save()

        log.parse_items_for_sale(log_data['response']['market_list'])

    def parse_items_for_sale(self, sale_items):
        for item in sale_items:
            master_type = item['item_master_type']

            if master_type in ShopRefreshItemDrop.PARSE_ITEM_TYPES:
                item_log = ShopRefreshItemDrop.parse(**item)
            elif master_type in ShopRefreshRuneDrop.PARSE_ITEM_TYPES:
                item_log = ShopRefreshRuneDrop.parse(**item)
            elif master_type in ShopRefreshMonsterDrop.PARSE_ITEM_TYPES:
                item_log = ShopRefreshMonsterDrop.parse(**item)
            else:
                raise ValueError(f"Don't know how to parse {master_type} in {self.__class__.__name__}")

            if item_log:
                item_log.log = self
                item_log.save()


class ShopRefreshDrop(models.Model):
    log = models.ForeignKey(ShopRefreshLog, on_delete=models.CASCADE)
    cost = models.IntegerField()

    class Meta:
        abstract = True


class ShopRefreshItemDrop(ItemDrop, ShopRefreshDrop):
    @classmethod
    def parse(cls, **kwargs):
        log = super().parse(**kwargs)
        log.cost = kwargs.get('buy_mana', 0)
        return log


class ShopRefreshRuneDrop(RuneDrop, ShopRefreshDrop):
    @classmethod
    def parse(cls, **kwargs):
        log = super().parse(**kwargs['runes'][0])
        log.cost = kwargs.get('buy_mana', 0)
        return log


class ShopRefreshMonsterDrop(MonsterDrop, ShopRefreshDrop):
    @classmethod
    def parse(cls, **kwargs):
        log = super().parse(**kwargs)
        log.cost = kwargs.get('buy_mana', 0)
        return log


# Wishes
class WishLog(LogEntry):
    wish_id = models.IntegerField()
    wish_sequence = models.IntegerField()
    crystal_used = models.BooleanField()

    @classmethod
    def parse_wish_log(cls, summoner, log_data):
        log = cls(summoner=summoner)
        log.parse_common_log_data(log_data)
        log.wish_id = log_data['response']['wish_info']['wish_id']
        log.wish_sequence = log_data['response']['wish_info']['wish_sequence']
        log.crystal_used = log_data['response']['wish_info']['cash_used']
        log.save()

        # Wish reward
        master_type = log_data['response']['wish_info']['item_master_type']

        if master_type in [GameItem.CATEGORY_MONSTER, GameItem.CATEGORY_RAINBOWMON]:
            reward = WishLogMonsterDrop.parse(**log_data['response']['unit_info'])
        elif master_type == GameItem.CATEGORY_RUNE:
            reward = WishLogRuneDrop.parse(**log_data['response']['rune'])
        else:
            reward = WishLogItemDrop.parse(**log_data['response']['wish_info'])

        if reward:
            reward.log = log
            reward.save()


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
    PARSE_IDS = list(range(1401001, 1401022)) + list(range(1402001, 1402022)) + list(range(1403001, 1403022))

    CRAFT_LOW = 1
    CRAFT_MID = 2
    CRAFT_HIGH = 3

    CRAFT_CHOICES = [
        (CRAFT_LOW, 'Low'),
        (CRAFT_MID, 'Mid'),
        (CRAFT_HIGH, 'High'),
    ]

    craft_level = models.IntegerField(choices=CRAFT_CHOICES)

    @staticmethod
    def get_craft_level(com2us_item_id):
        # Craft level is in 1000s digit
        return (com2us_item_id - 1400000) // 1000

    @classmethod
    def parse_buy_shop_item(cls, summoner, log_data):
        for rune_data in log_data['response']['reward']['crate']['runes']:
            log_entry = cls.parse(**rune_data)
            log_entry.summoner = summoner
            log_entry.parse_common_log_data(log_data)
            log_entry.craft_level = CraftRuneLog.get_craft_level(log_data['request']['item_id'])
            log_entry.save()


# Magic Box Crafting
class MagicBoxCraft(LogEntry):
    PARSE_IDS = [1300008, 1300009, 1300012]

    BOX_UNKNOWN_MAGIC = 8
    BOX_MYSTICAL_MAGIC = 9
    BOX_LEGENDARY_MAGIC = 12

    BOX_CHOICES = [
        (BOX_UNKNOWN_MAGIC, 'Unknown Magic Box'),
        (BOX_MYSTICAL_MAGIC, 'Mystical Magic Box'),
        (BOX_LEGENDARY_MAGIC, 'Legendary Magic Box'),
    ]

    box_type = models.IntegerField(choices=BOX_CHOICES)

    @staticmethod
    def get_box_type(com2us_item_id):
        return com2us_item_id - 1300000

    @classmethod
    def parse_buy_shop_item(cls, summoner, log_data):
        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        log_entry.box_type = cls.get_box_type(log_data['request']['item_id'])
        log_entry.save()
        log_entry.parse_items(log_data['response']['view_item_list'])
        log_entry.parse_crate(log_data['response']['reward']['crate'])

    def parse_items(self, item_list):
        # Parse items and ignore runes or grindstones/gems
        for item in item_list:
            master_type = item['item_master_type']

            if master_type in MagicBoxCraftItemDrop.PARSE_ITEM_TYPES:
                log_entry = MagicBoxCraftItemDrop.parse(**item)
            elif master_type in MagicBoxCraftRuneDrop.PARSE_ITEM_TYPES + MagicBoxCraftRuneCraftDrop.PARSE_ITEM_TYPES:
                # This will be parsed by iterating through the reward crate, skip for now.
                continue
            else:
                raise ValueError(f"Can't parse item type {master_type} with {self.__class__.__name__}")

            if log_entry:
                log_entry.log = self
                log_entry.save()

    def parse_crate(self, crate):
        for key, items in crate.items():
            if key == 'runes':
                for rune_data in items:
                    log_entry = MagicBoxCraftRuneDrop.parse(**rune_data)
                    log_entry.log = self
                    log_entry.save()
            elif key == 'changestones':
                for runecraft_data in items:
                    log_entry = MagicBoxCraftRuneCraftDrop.parse(**runecraft_data)
                    log_entry.log = self
                    log_entry.save()
            else:
                raise ValueError(f"Don't know how to parse crate key `{key}` with {self.__class__.__name__}")


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
            log_entry = cls.parse(**unit_info)
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
            dungeon__com2us_id=log_data['request']['region_id'],
            difficulty=log_data['request']['difficulty'],
            floor=log_data['request']['stage_no'],
        )

        # Remainder of information comes from BattleScenarioResult
        log_entry.save()

    @classmethod
    def parse_scenario_result(cls, summoner, log_data):
        try:
            log_entry = cls.objects.get(
                wizard_id=log_data['request']['wizard_id'],
                battle_key=log_data['request']['battle_key']
            )
        except cls.DoesNotExist:
            # Do not parse scenario results that didn't get created with parse_scenario_start()
            return

        log_entry.parse_common_log_data(log_data)
        log_entry.success = log_data['request']['win_lose'] == 1
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.save()
        log_entry.parse_rewards(log_data['response']['reward'])

    @classmethod
    def parse_dungeon_result(cls, summoner, log_data):
        dungeon_id = log_data['request']['dungeon_id']

        # Don't log HoH dungeons, which have IDs starting from 10000 and increments by 1 each new HoH.
        if 10000 <= dungeon_id < 11000:
            return

        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        log_entry.level = Level.objects.get(
            dungeon__category=Dungeon.CATEGORY_CAIROS,
            dungeon__com2us_id=dungeon_id,
            floor=log_data['request']['stage_id'],
        )
        log_entry.success = log_data['request']['win_lose'] == 1
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.save()
        log_entry.parse_rewards(log_data['response']['reward'])

    def parse_rewards(self, rewards):
        for key, val in rewards.items():
            reward = None

            if key == 'crate':
                self.parse_rewards(val)
            elif isinstance(val, dict):
                if 'item_master_type' in val:
                    # Parse by master type
                    if val['item_master_type'] in DungeonItemDrop.PARSE_ITEM_TYPES:
                        reward = DungeonItemDrop.parse(**val)
                elif key == 'rune':
                    reward = DungeonRuneDrop.parse(**val)
                elif key == 'unit_info':
                    reward = DungeonMonsterDrop.parse(**val)

            else:
                if key in DungeonItemDrop.PARSE_KEYS:
                    reward = DungeonItemDrop.parse(key=key, val=val)

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
    clear_time = models.DurationField()
    success = models.BooleanField()

    def __str__(self):
        return f'RiftDungeonLog {self.level} {self.grade}'

    @classmethod
    def parse_rift_dungeon_result(cls, summoner, log_data):
        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)

        log_entry.level = Level.objects.get(
            dungeon__category=Dungeon.CATEGORY_RIFT_OF_WORLDS_BEASTS,
            dungeon__com2us_id=log_data['request']['dungeon_id'],
            floor=1,
        )
        log_entry.grade = log_data['response']['rift_dungeon_box_id']
        log_entry.total_damage = log_data['response']['total_damage']
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.success = log_data['request']['battle_result'] == 1
        log_entry.save()
        log_entry.parse_rewards(log_data['response'].get('item_list', []))

    def parse_rewards(self, items):
        for item in items:
            master_type = item['type']
            if master_type in RiftDungeonItemDrop.PARSE_ITEM_TYPES:
                log_entry = RiftDungeonItemDrop.parse(**item)
            elif master_type in RiftDungeonMonsterDrop.PARSE_ITEM_TYPES:
                log_entry = RiftDungeonMonsterDrop.parse(**item['info'])
            elif master_type in RiftDungeonRuneDrop.PARSE_ITEM_TYPES:
                log_entry = RiftDungeonRuneDrop.parse(**item['info'])
            elif master_type in RiftDungeonRuneCraftDrop.PARSE_ITEM_TYPES:
                log_entry = RiftDungeonRuneCraftDrop.parse(**item['info'])
            else:
                raise ValueError(f"don't know how to parse {master_type} in {self.__class__.__name__}")

            if log_entry:
                log_entry.log = self
                log_entry.save()


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
