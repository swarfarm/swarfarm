from datetime import datetime, timedelta

import pytz
from django.contrib.postgres.fields import JSONField
from django.core.mail import mail_admins
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
        ordering = ('-timestamp', '-pk')
        get_latest_by = 'timestamp'

    def parse_common_log_data(self, log_data):
        self.wizard_id = log_data['request']['wizard_id']
        self.server = LogEntry.TIMEZONE_SERVER_MAP.get(log_data['response']['tzone'])
        self.timestamp = datetime.fromtimestamp(log_data['response']['tvalue'], tz=pytz.timezone('GMT'))


class ItemDropManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related('item')


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

    RELATED_NAME = 'items'
    objects = ItemDropManager()

    item = models.ForeignKey(GameItem, on_delete=models.PROTECT)
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


class MonsterDropManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related('monster')


class MonsterDrop(models.Model):
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_MONSTER,
        GameItem.CATEGORY_RAINBOWMON,
    )

    RELATED_NAME = 'monsters'
    objects = MonsterDropManager()

    monster = models.ForeignKey(Monster, on_delete=models.PROTECT)
    grade = models.IntegerField()
    level = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.monster} {self.grade}* lv.{self.level}'

    @classmethod
    def parse(cls, **monster_info):
        com2us_id = monster_info.get('unit_master_id') or monster_info.get('item_master_id')
        grade = monster_info.get('class') or monster_info.get('unit_class')
        level = monster_info.get('unit_level') or 1
        return cls(
                monster=Monster.objects.get(com2us_id=com2us_id),
                grade=grade,
                level=level,
            )


class MonsterPieceDrop(models.Model):
    PARSE_KEYS = ()

    RELATED_NAME = 'monster_pieces'
    objects = MonsterDropManager()

    monster = models.ForeignKey(Monster, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.monster} x{self.quantity}'


class RuneDrop(Rune):
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_RUNE,
    )

    RELATED_NAME = 'runes'

    class Meta:
        abstract = True

    @classmethod
    def parse(cls, **rune_data):
        if rune_data['class'] > 10:
            stars = rune_data['class'] - 10
            ancient = True
        else:
            stars = rune_data['class']
            ancient = False

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
            stars=stars,
            ancient=ancient,
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
    PARSE_KEYS = ()
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_RUNE_CRAFT,
    )

    RELATED_NAME = 'rune_crafts'

    class Meta:
        abstract = True

    @classmethod
    def parse(cls, **craft_data):
        craft_type_id = str(craft_data.get('craft_type_id') or craft_data.get('runecraft_item_id'))
        craft_type = craft_data.get('craft_type') or craft_data.get('runecraft_type')

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

    @classmethod
    def parse(cls, summoner, log_data):
        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        log_entry.command = log_data['request']['command']
        log_entry.request = log_data['request']
        log_entry.response = log_data['response']
        log_entry.save()


# Magic Shop
class ShopRefreshLogManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            ShopRefreshItemDrop.RELATED_NAME,
            ShopRefreshRuneDrop.RELATED_NAME,
            ShopRefreshMonsterDrop.RELATED_NAME,
        )


class ShopRefreshLog(LogEntry):
    objects = ShopRefreshLogManager()

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
    cost = models.IntegerField()

    class Meta:
        abstract = True

    @classmethod
    def parse(cls, **kwargs):
        log = super().parse(**kwargs)
        log.cost = kwargs.get('buy_mana', 0)
        return log


class ShopRefreshItemDrop(ShopRefreshDrop, ItemDrop):
    log = models.ForeignKey(ShopRefreshLog, on_delete=models.CASCADE, related_name=ItemDrop.RELATED_NAME)


class ShopRefreshRuneDrop(ShopRefreshDrop, RuneDrop):
    log = models.ForeignKey(ShopRefreshLog, on_delete=models.CASCADE, related_name=RuneDrop.RELATED_NAME)

    @classmethod
    def parse(cls, **kwargs):
        log = super().parse(**kwargs['runes'][0])
        log.cost = kwargs.get('buy_mana', 0)
        return log


class ShopRefreshMonsterDrop(ShopRefreshDrop, MonsterDrop):
    log = models.ForeignKey(ShopRefreshLog, on_delete=models.CASCADE, related_name=MonsterDrop.RELATED_NAME)


# Wishes
class WishLogManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            WishLogItemDrop.RELATED_NAME,
            WishLogMonsterDrop.RELATED_NAME,
            WishLogRuneDrop.RELATED_NAME,
        )


class WishLog(LogEntry):
    objects = WishLogManager()

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

        if master_type in WishLogMonsterDrop.PARSE_ITEM_TYPES:
            reward = WishLogMonsterDrop.parse(**log_data['response']['unit_info'])
        elif master_type in WishLogRuneDrop.PARSE_ITEM_TYPES:
            reward = WishLogRuneDrop.parse(**log_data['response']['rune'])
        elif master_type in WishLogItemDrop.PARSE_ITEM_TYPES:
            reward = WishLogItemDrop.parse(**log_data['response']['wish_info'])
        else:
            raise ValueError(f"Don't know how to parse item type `{master_type}` with {cls.__class__.__name__}")

        reward.log = log
        reward.save()


class WishLogItemDrop(ItemDrop):
    log = models.ForeignKey(WishLog, on_delete=models.CASCADE, related_name=ItemDrop.RELATED_NAME)


class WishLogMonsterDrop(MonsterDrop):
    log = models.ForeignKey(WishLog, on_delete=models.CASCADE, related_name=MonsterDrop.RELATED_NAME)


class WishLogRuneDrop(RuneDrop):
    log = models.ForeignKey(WishLog, on_delete=models.CASCADE, related_name=RuneDrop.RELATED_NAME)


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
        try:
            runes_data = log_data['response']['reward']['crate']['runes']
        except KeyError:
            # Missing rune data - discard the log
            return

        for rune_data in runes_data:
            log_entry = cls.parse(**rune_data)
            log_entry.summoner = summoner
            log_entry.parse_common_log_data(log_data)
            log_entry.craft_level = CraftRuneLog.get_craft_level(log_data['request']['item_id'])
            log_entry.save()


# Magic Box Crafting
class MagicBoxCraftManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            MagicBoxCraftItemDrop.RELATED_NAME,
            MagicBoxCraftRuneDrop.RELATED_NAME,
            MagicBoxCraftRuneCraftDrop.RELATED_NAME,
        )


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

    objects = MagicBoxCraftManager()

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
        log_entry.parse_items(log_data['response'].get('view_item_list', []))

        try:
            crate = log_data['response']['reward']['crate']
        except (KeyError, TypeError):
            # Crate not in data, or reward key missing. Don't try to parse anything in it.
            pass
        else:
            log_entry.parse_crate(crate)

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


class MagicBoxCraftItemDrop(ItemDrop):
    log = models.ForeignKey(MagicBoxCraft, on_delete=models.CASCADE, related_name=ItemDrop.RELATED_NAME)


class MagicBoxCraftRuneDrop(RuneDrop):
    log = models.ForeignKey(MagicBoxCraft, on_delete=models.CASCADE, related_name=RuneDrop.RELATED_NAME)


class MagicBoxCraftRuneCraftDrop(RuneCraftDrop):
    log = models.ForeignKey(MagicBoxCraft, on_delete=models.CASCADE, related_name=RuneCraftDrop.RELATED_NAME)


# Summons
class SummonLog(LogEntry, MonsterDrop):
    # Redefine monster fields to allow nulls due to blessings that do not know which monster is summoned yet
    monster = models.ForeignKey(Monster, on_delete=models.PROTECT, null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)

    item = models.ForeignKey(GameItem, on_delete=models.PROTECT, help_text='Item or currency used to summon')
    blessing_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'SummonLog - {self.item} - {self.monster} {self.grade}*'

    @classmethod
    def parse_summon_log(cls, summoner, log_data):
        if log_data['response']['unit_list'] is None:
            return

        # Create one entry per unit summoned
        for unit_info in log_data['response']['unit_list']:
            log_entry = cls.parse(**unit_info)
            log_entry.parse_common_log_data(log_data)
            log_entry.summoner = summoner
            log_entry.get_summon_method(log_data)
            log_entry.save()
        else:
            if log_data['response'].get('summon_choices'):
                # Blessing popped, parse the common data but leave monster empty
                log_entry = cls()
                log_entry.parse_common_log_data(log_data)
                log_entry.summoner = summoner
                log_entry.get_summon_method(log_data)
                log_entry.blessing_id = log_data['response']['summon_choices'][0]['rid']
                log_entry.save()

    @classmethod
    def parse_blessing_choice(cls, summoner, log_data):
        try:
            log_entry = cls.objects.get(
                wizard_id=log_data['request']['wizard_id'],
                blessing_id=log_data['request']['rid']
            )
        except cls.DoesNotExist:
            # Do not parse blessing choices if no prior summon log entry found
            return

        # Save the monster which was chosen
        monster_data = cls.parse(**log_data['response']['unit_list'][0])
        log_entry.monster = monster_data.monster
        log_entry.grade = monster_data.grade
        log_entry.level = monster_data.level
        log_entry.save()

    def get_summon_method(self, log_data):
        if len(log_data['response'].get('item_list', [])) > 0:
            item_info = log_data['response']['item_list'][0]

            self.item = GameItem.objects.get(
                category=item_info['item_master_type'],
                com2us_id=item_info['item_master_id']
            )
        else:
            mode = log_data['request']['mode']
            if mode == 3:
                # Crystal summon
                self.item = GameItem.objects.get(
                    category=GameItem.CATEGORY_CURRENCY,
                    com2us_id=1,
                )
            elif mode == 5:
                # Social summon
                self.item = GameItem.objects.get(
                    category=GameItem.CATEGORY_CURRENCY,
                    com2us_id=2,
                )


# Dungeons
class DungeonLogManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'level',
            'level__dungeon',
            DungeonItemDrop.RELATED_NAME,
            DungeonMonsterDrop.RELATED_NAME,
            DungeonMonsterPieceDrop.RELATED_NAME,
            DungeonRuneDrop.RELATED_NAME,
            DungeonSecretDungeonDrop.RELATED_NAME,
        )


class DungeonLog(LogEntry):
    objects = DungeonLogManager()

    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    success = models.NullBooleanField(help_text='Null indicates that run was not completed')
    clear_time = models.DurationField(blank=True, null=True)

    @classmethod
    def parse_scenario_start(cls, summoner, log_data):
        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
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
        floor = log_data['request']['stage_id']

        # Don't log HoH dungeons, which have IDs starting from 10000 and increments by 1 each new HoH.
        if 10000 <= dungeon_id < 11000:
            return

        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        try:
            log_entry.level = Level.objects.get(
                dungeon__category=Dungeon.CATEGORY_CAIROS,
                dungeon__com2us_id=dungeon_id,
                floor=floor,
            )
        except Level.DoesNotExist:
            # Create a placeholder level for later updating
            try:
                d = Dungeon.objects.get(category=Dungeon.CATEGORY_CAIROS, com2us_id=dungeon_id)
            except Dungeon.DoesNotExist:
                # Create the dungeon
                d = Dungeon.objects.create(
                    com2us_id=dungeon_id,
                    enabled=False,
                    name='UNKNOWN DUNGEON',
                    category=Dungeon.CATEGORY_CAIROS,
                )

            # Create the level
            log_entry.level = Level.objects.create(
                dungeon=d,
                floor=floor,
            )
            mail_admins('New Level Created', f'New level {floor} created in dungeon com2us ID {dungeon_id}.')

        log_entry.success = log_data['request']['win_lose'] == 1
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.save()
        log_entry.parse_rewards(log_data['response']['reward'])

        # Parse secret dungeon drop
        sd_info = log_data['response'].get('instance_info')
        if sd_info:
            sd_reward = DungeonSecretDungeonDrop.parse(sd_info)
            sd_reward.log = log_entry
            sd_reward.save()

    @classmethod
    def parse_dungeon_result_v2(cls, summoner, log_data):
        dungeon_id = log_data['request']['dungeon_id']
        floor = log_data['request']['stage_id']

        # Don't log HoH dungeons, which have IDs starting from 10000 and increments by 1 each new HoH.
        if 10000 <= dungeon_id < 11000:
            return

        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        try:
            log_entry.level = Level.objects.get(
                dungeon__category=Dungeon.CATEGORY_CAIROS,
                dungeon__com2us_id=dungeon_id,
                floor=floor,
            )
        except Level.DoesNotExist:
            # Create a placeholder level for later updating
            try:
                d = Dungeon.objects.get(category=Dungeon.CATEGORY_CAIROS, com2us_id=dungeon_id)
            except Dungeon.DoesNotExist:
                # Create the dungeon
                d = Dungeon.objects.create(
                    com2us_id=dungeon_id,
                    enabled=False,
                    name='UNKNOWN DUNGEON',
                    category=Dungeon.CATEGORY_CAIROS,
                )

            # Create the level
            log_entry.level = Level.objects.create(
                dungeon=d,
                floor=floor,
            )
            mail_admins('New Level Created', f'New level {floor} created in dungeon com2us ID {dungeon_id}.')

        log_entry.success = log_data['request']['win_lose'] == 1
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.save()
        log_entry.parse_rewards(log_data['response']['reward'])
        log_entry.parse_changed_item_list(log_data['response']['changed_item_list'])

    @classmethod
    def parse_dimension_hole_result(cls, summoner, log_data):
        if log_data['response']['practice_mode']:
            # Don't parse practice modes
            return

        dungeon_id = log_data['response']['dungeon_id']
        floor = log_data['response']['difficulty']

        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        try:
            log_entry.level = Level.objects.get(
                dungeon__category=Dungeon.CATEGORY_DIMENSIONAL_HOLE,
                dungeon__com2us_id=dungeon_id,
                floor=floor,
            )
        except Level.DoesNotExist:
            # Create a placeholder level for later updating
            try:
                d = Dungeon.objects.get(category=Dungeon.CATEGORY_CAIROS, com2us_id=dungeon_id)
            except Dungeon.DoesNotExist:
                # Create the dungeon
                d = Dungeon.objects.create(
                    com2us_id=dungeon_id,
                    enabled=False,
                    name='UNKNOWN DUNGEON',
                    category=Dungeon.CATEGORY_DIMENSIONAL_HOLE,
                )

            # Create the level
            log_entry.level = Level.objects.create(
                dungeon=d,
                floor=floor,
            )
            mail_admins('New Level Created', f'New level {floor} created in dungeon com2us ID {dungeon_id}.')

        log_entry.success = log_data['request']['win_lose'] == 1
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.save()
        log_entry.parse_rewards(log_data['response']['reward'])

    def parse_rewards(self, rewards):
        if not rewards:
            # If there are no rewards, it's an empty list. Exit early since later code assumes rewards is a dict
            return

        # Parse each reward
        reward_objs = []
        for key, val in rewards.items():
            if key == 'crate':
                # Recurse with crate contents
                self.parse_rewards(val)
            elif key in DungeonItemDrop.PARSE_KEYS:
                reward_objs.append(DungeonItemDrop.parse(key=key, val=val))
            elif isinstance(val, dict):
                if 'item_master_type' in val:
                    # Parse by master type
                    if val['item_master_type'] in DungeonItemDrop.PARSE_ITEM_TYPES:
                        reward_objs.append(DungeonItemDrop.parse(**val))
                elif key == 'rune':
                    reward_objs.append(DungeonRuneDrop.parse(**val))
                elif key == 'unit_info':
                    reward_objs.append(DungeonMonsterDrop.parse(**val))
                elif key == 'material':
                    reward_objs.append(DungeonItemDrop.parse(**{'item_master_type': GameItem.CATEGORY_ESSENCE, **val}))
                elif key == 'random_scroll':
                    reward_objs.append(DungeonItemDrop.parse(**{'item_master_type': GameItem.CATEGORY_SUMMON_SCROLL, **val}))
                elif key == 'changestones':
                    reward_objs.append(DungeonRuneCraftDrop.parse(**val))
                else:
                    raise ValueError(f"don't know how to parse {key} reward in {self.__class__.__name__}")
            elif isinstance(val, list):
                if key == 'changestones':
                    for craft_data in val:
                        reward_objs.append(DungeonRuneCraftDrop.parse(**craft_data))
                elif key == 'event_crate':
                    # Don't care, skip it
                    continue
                else:
                    raise ValueError(f"don't know how to parse array of {key} reward in {self.__class__.__name__}")
            else:
                ValueError(f"don't know how to parse {key} reward in {self.__class__.__name__}")

        # Save parsed rewards
        for reward in reward_objs:
            if reward is not None:
                reward.log = self
                reward.save()

    def parse_changed_item_list(self, changed_item_list):
        if not changed_item_list:
            # If there are changed items, it's an empty list. Exit early since later code assumes a dict
            return

        # Parse each reward
        changed_items_object = []
        for obj in changed_item_list:
            # check if all required keys exist in the dict
            for k in ("type", "info", "view"):
                if k not in obj:
                    raise ValueError(f"missing key {k} in {self.__class__.__name__}")

            item_type = obj["type"]
            info = obj["info"]
            view = obj["view"]

            # parse common item drop
            if item_type in ItemDrop.PARSE_ITEM_TYPES:
                changed_items_object.append(DungeonItemDrop.parse(
                    item_master_type=view["item_master_type"],
                    item_master_id=view["item_master_id"],
                    item_quantity=view["item_quantity"],
                ))
            # parse unit monster drop
            elif item_type == GameItem.CATEGORY_MONSTER:
                changed_items_object.append(DungeonMonsterDrop.parse(
                    unit_master_id=view["item_master_id"],
                    unit_class=view["unit_class"],
                    unit_level=view["unit_level"],
                ))
            # parse rune drop
            elif item_type == GameItem.CATEGORY_RUNE:
                changed_items_object.append(DungeonRuneDrop.parse(**info))
            # parse secret dungeon drop
            elif item_type == 30:
                # Parse secret dungeon drop
                sd_reward = DungeonSecretDungeonDrop.parse(info)
                sd_reward.log = self  # TODO: Make sure this works
                sd_reward.save()
            else:
                raise ValueError(f"don't know how to parse changed item type {item_type} in {self.__class__.__name__}")

        # Save parsed rewards
        for reward in changed_items_object:
            if reward is not None:
                reward.log = self
                reward.save()


class DungeonItemDrop(ItemDrop):
    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE, related_name=ItemDrop.RELATED_NAME)


class DungeonMonsterDrop(MonsterDrop):
    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE, related_name=MonsterDrop.RELATED_NAME)


class DungeonMonsterPieceDrop(MonsterPieceDrop):
    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE, related_name=MonsterPieceDrop.RELATED_NAME)


class DungeonRuneDrop(RuneDrop):
    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE, related_name=RuneDrop.RELATED_NAME)


class DungeonRuneCraftDrop(RuneCraftDrop):
    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE, related_name=RuneCraftDrop.RELATED_NAME)


class DungeonSecretDungeonDropManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'level__dungeon__secretdungeon__monster',
        )


class DungeonSecretDungeonDrop(models.Model):
    RELATED_NAME = 'secret_dungeons'
    objects = DungeonSecretDungeonDropManager()

    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE, related_name=RELATED_NAME)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)

    @classmethod
    def parse(cls, instance_info):
        return cls(
            level=Level.objects.get(
                dungeon__category=Dungeon.CATEGORY_SECRET,
                dungeon__com2us_id=instance_info['instance_id'],
                floor=1,
            )
        )


# Rift dungeon
class RiftDungeonLogManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'level',
            'level__dungeon',
            RiftDungeonItemDrop.RELATED_NAME,
            RiftDungeonMonsterDrop.RELATED_NAME,
            RiftDungeonRuneDrop.RELATED_NAME,
            RiftDungeonRuneCraftDrop.RELATED_NAME,
        )


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

    objects = RiftDungeonLogManager()

    level = models.ForeignKey(Level, on_delete=models.PROTECT)
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
        log_entry.parse_rewards(log_data['response'].get('item_list') or [])

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

            log_entry.log = self
            log_entry.save()


class RiftDungeonItemDrop(ItemDrop):
    log = models.ForeignKey(RiftDungeonLog, on_delete=models.CASCADE, related_name=ItemDrop.RELATED_NAME)


class RiftDungeonMonsterDrop(MonsterDrop):
    log = models.ForeignKey(RiftDungeonLog, on_delete=models.CASCADE, related_name=MonsterDrop.RELATED_NAME)


class RiftDungeonRuneDrop(RuneDrop):
    log = models.ForeignKey(RiftDungeonLog, on_delete=models.CASCADE, related_name=RuneDrop.RELATED_NAME)


class RiftDungeonRuneCraftDrop(RuneCraftDrop):
    log = models.ForeignKey(RiftDungeonLog, on_delete=models.CASCADE, related_name=RuneCraftDrop.RELATED_NAME)


# Rift of Worlds Raid
class RiftRaidLogManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'level',
            'level__dungeon',
            RiftRaidItemDrop.RELATED_NAME,
            RiftRaidMonsterDrop.RELATED_NAME,
            RiftRaidRuneCraftDrop.RELATED_NAME,
        )


class RiftRaidLog(LogEntry):
    objects = RiftRaidLogManager()

    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    success = models.NullBooleanField(help_text='Null indicates that run was not completed')
    contribution_amount = models.IntegerField(blank=True, null=True)
    clear_time = models.DurationField(blank=True, null=True)

    @classmethod
    def parse_rift_raid_start(cls, summoner, log_data):
        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        log_entry.battle_key = log_data['request']['battle_key']
        log_entry.level = Level.objects.get(
            dungeon__category=Dungeon.CATEGORY_RIFT_OF_WORLDS_RAID,
            dungeon__com2us_id=log_data['response']['battle_info']['raid_id'],
            floor=log_data['response']['battle_info']['stage_id'],
        )
        log_entry.save()

    @classmethod
    def parse_rift_raid_result(cls, summoner, log_data):
        wizard_id = log_data['request']['wizard_id']
        battle_key = log_data['request']['battle_key']

        try:
            if summoner is not None:
                log_entry = cls.objects.get(summoner=summoner, battle_key=battle_key)
            else:
                log_entry = cls.objects.get(wizard_id=wizard_id, battle_key=battle_key)
        except (cls.DoesNotExist, cls.MultipleObjectsReturned):
            return

        # Get this user's info out of `user_status_list`
        user_status = None

        for status in log_data['request']['user_status_list']:
            if status['wizard_id'] == wizard_id:
                user_status = status
                break

        log_entry.parse_common_log_data(log_data)
        log_entry.success = log_data['request']['win_lose'] == 1
        log_entry.contribution_amount = user_status['damage']
        log_entry.clear_time = timedelta(milliseconds=log_data['request']['clear_time'])
        log_entry.save()
        log_entry.parse_rewards(battle_key, log_data['response']['battle_reward_list'])

    def parse_rewards(self, battle_key, rewards_list):
        for rewards in rewards_list:
            reward_wizard_id = rewards['wizard_id']
            if self.wizard_id == reward_wizard_id:
                for reward_info in rewards['reward_list']:
                    master_type = reward_info['item_master_type']

                    if master_type in RiftRaidItemDrop.PARSE_ITEM_TYPES:
                        log_entry = RiftRaidItemDrop.parse(battle_key, reward_wizard_id, reward_info)
                    elif master_type in RiftRaidMonsterDrop.PARSE_ITEM_TYPES:
                        log_entry = RiftRaidMonsterDrop.parse(battle_key, reward_wizard_id, reward_info)
                    elif master_type in RiftRaidRuneCraftDrop.PARSE_ITEM_TYPES:
                        log_entry = RiftRaidRuneCraftDrop.parse(battle_key, reward_wizard_id, reward_info)
                    else:
                        raise ValueError(f"don't know how to parse {master_type} in {self.__class__.__name__}")

                    log_entry.log = self
                    log_entry.save()


class RiftRaidDrop(models.Model):
    wizard_id = models.BigIntegerField()

    class Meta:
        abstract = True

    @classmethod
    def parse(cls, battle_key, wizard_id, item_data):
        try:
            log_entry = cls.objects.get(log__battle_key=battle_key, wizard_id=wizard_id)
        except cls.DoesNotExist:
            log_entry = super().parse(**item_data)
            log_entry.wizard_id = wizard_id

        return log_entry


class RiftRaidItemDrop(RiftRaidDrop, ItemDrop):
    log = models.ForeignKey(RiftRaidLog, on_delete=models.CASCADE, related_name=ItemDrop.RELATED_NAME)


class RiftRaidMonsterDrop(RiftRaidDrop, MonsterDrop):
    log = models.ForeignKey(RiftRaidLog, on_delete=models.CASCADE, related_name=MonsterDrop.RELATED_NAME)


class RiftRaidRuneCraftDrop(RiftRaidDrop, RuneCraftDrop):
    log = models.ForeignKey(RiftRaidLog, on_delete=models.CASCADE, related_name=RuneCraftDrop.RELATED_NAME)


# World Boss
class WorldBossLogManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'level',
            'level__dungeon',
            WorldBossLogItemDrop.RELATED_NAME,
            WorldBossLogMonsterDrop.RELATED_NAME,
            WorldBossLogRuneDrop.RELATED_NAME,
        )


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

    objects = WorldBossLogManager()

    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    battle_key = models.BigIntegerField(null=True, blank=True)
    grade = models.IntegerField(choices=GRADE_CHOICES, null=True, blank=True)
    damage = models.IntegerField()
    battle_points = models.IntegerField()
    bonus_battle_points = models.IntegerField()
    avg_monster_level = models.FloatField()
    monster_count = models.IntegerField()

    @classmethod
    def parse_world_boss_start(cls, summoner, log_data):
        log_entry = cls(summoner=summoner)
        log_entry.parse_common_log_data(log_data)
        log_entry.level = Level.objects.get(dungeon__category=Dungeon.CATEGORY_WORLD_BOSS, floor=1)
        log_entry.battle_key = log_data['response']['battle_key']
        log_entry.damage = log_data['response']['worldboss_battle_result']['total_damage']
        log_entry.battle_points = log_data['response']['worldboss_battle_result']['total_battle_point']
        log_entry.bonus_battle_points = log_data['response']['worldboss_battle_result']['bonus_battle_point']
        log_entry.avg_monster_level = log_data['response']['worldboss_battle_result']['unit_avg_level']
        log_entry.monster_count = log_data['response']['worldboss_battle_result']['unit_count']
        log_entry.save()

    @classmethod
    def parse_world_boss_result(cls, summoner, log_data):
        try:
            log_entry = cls.objects.get(
                wizard_id=log_data['request']['wizard_id'],
                battle_key=log_data['request']['battle_key'],
            )
        except (cls.DoesNotExist, cls.MultipleObjectsReturned):
            # Unable to find matching log from BattleWorldBossStart command
            return

        log_entry.grade = log_data['response']['reward_info']['box_id']
        log_entry.parse_rewards(log_data['response']['reward_info']['reward_list'])
        log_entry.save()

        # Parse runes only out of the reward crate
        runes_reward = log_data['response']['reward']['crate'].get('runes', [])

        for rune_data in runes_reward:
            rune_drop = WorldBossLogRuneDrop.parse(**rune_data)
            rune_drop.log = log_entry
            rune_drop.save()

    def parse_rewards(self, rewards):
        for reward in rewards:
            master_type = reward['item_master_type']
            if master_type in WorldBossLogItemDrop.PARSE_ITEM_TYPES:
                log_entry = WorldBossLogItemDrop.parse(**reward)
            elif master_type in WorldBossLogMonsterDrop.PARSE_ITEM_TYPES:
                log_entry = WorldBossLogMonsterDrop.parse(**reward)
            elif master_type in WorldBossLogRuneDrop.PARSE_ITEM_TYPES:
                # Full rune data not available here, parse on world boss result
                continue
            else:
                raise ValueError(f"don't know how to parse {master_type} in {self.__class__.__name__}")

            if log_entry:
                log_entry.log = self
                log_entry.save()


class WorldBossLogItemDrop(ItemDrop):
    log = models.ForeignKey(WorldBossLog, on_delete=models.CASCADE, related_name=ItemDrop.RELATED_NAME)


class WorldBossLogMonsterDrop(MonsterDrop):
    log = models.ForeignKey(WorldBossLog, on_delete=models.CASCADE, related_name=MonsterDrop.RELATED_NAME)


class WorldBossLogRuneDrop(RuneDrop):
    log = models.ForeignKey(WorldBossLog, on_delete=models.CASCADE, related_name=RuneDrop.RELATED_NAME)
