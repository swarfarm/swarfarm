from django.contrib.postgres.fields import JSONField
from django.db import models

from archive.models.abstracts import ArchiveAbs
from bestiary.models import Monster, Level, GameItem, Rune, RuneCraft, Artifact
from data_log.models.log_models import ItemDropManager, MonsterDropManager, WishLogManager, \
    DungeonLogManager, MagicBoxCraftManager, RiftRaidLogManager, WorldBossLogManager, RiftDungeonLogManager, \
    ShopRefreshLogManager, DungeonSecretDungeonDropManager
from herders.models import Summoner


# Abstract models for encapsulating common data like drops and log entry metadata
class LogArchive(ArchiveAbs):
    # Abstract model with basic fields required for logging anything
    TIMEZONE_SERVER_MAP = {
        'America/Los_Angeles': Summoner.SERVER_GLOBAL,
        'Europe/Berlin': Summoner.SERVER_EUROPE,
        'Asia/Seoul': Summoner.SERVER_KOREA,
        'Asia/Shanghai': Summoner.SERVER_ASIA,
    }

    wizard_id = models.BigIntegerField()
    summoner = models.ForeignKey(Summoner, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True, db_index=True)
    server = models.IntegerField(choices=Summoner.SERVER_CHOICES, null=True, blank=True)

    @classmethod
    def archive_data(cls, log):
        return {
            'wizard_id': log.wizard_id,
            'summoner_id': log.summoner_id,
            'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S") if log.timestamp else None,
            'server': log.server,
        }

    class Meta:
        abstract = True
        ordering = ('-timestamp', '-pk')
        get_latest_by = 'timestamp'


class ItemDropArchive(models.Model):
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
        GameItem.CATEGORY_ARTIFACT_CRAFT,
    )

    RELATED_NAME = 'items'
    objects = ItemDropManager()

    item = models.ForeignKey(GameItem, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    @classmethod
    def archive_data(cls, item):
        return {
            'item_id': item.item_id,
            'quantity': item.quantity,
        }

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.item} x{self.quantity}'


class MonsterDropArchive(models.Model):
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_MONSTER,
        GameItem.CATEGORY_RAINBOWMON,
    )

    RELATED_NAME = 'monsters'
    objects = MonsterDropManager()

    monster = models.ForeignKey(Monster, on_delete=models.PROTECT)
    grade = models.IntegerField()
    level = models.IntegerField()

    @classmethod
    def archive_data(cls, monster):
        return {
            'monster_id': monster.monster_id,
            'grade': monster.grade,
            'level': monster.level,
        }

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.monster} {self.grade}* lv.{self.level}'


class MonsterPieceDropArchive(models.Model):
    PARSE_KEYS = ()

    RELATED_NAME = 'monster_pieces'
    objects = MonsterDropManager()

    monster = models.ForeignKey(Monster, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    @classmethod
    def archive_data(cls, log):
        return {
            'monster_id': log.monster_id,
            'quantity': log.quantity,
        }
	
    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.monster} x{self.quantity}'


class RuneDropArchive(Rune):
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_RUNE,
    )

    RELATED_NAME = 'runes'

    @classmethod
    def archive_data(cls, rune):
        return {
            'type': rune.type,
            'stars': rune.stars,
            'level': rune.level,
            'slot': rune.slot,
            'quality': rune.quality,
            'original_quality': rune.original_quality,
            'ancient': rune.ancient,
            'value': rune.value,
            'main_stat': rune.main_stat,
            'main_stat_value': rune.main_stat_value,
            'innate_stat': rune.innate_stat,
            'innate_stat_value': rune.innate_stat_value,
            'substats': rune.substats,
            'substat_values': rune.substat_values,
            'substats_enchanted': rune.substats_enchanted,
            'substats_grind_value': rune.substats_grind_value,
            'has_hp': rune.has_hp,
            'has_atk': rune.has_atk,
            'has_def': rune.has_def,
            'has_crit_rate': rune.has_crit_rate,
            'has_crit_dmg': rune.has_crit_dmg,
            'has_speed': rune.has_speed,
            'has_resist': rune.has_resist,
            'has_accuracy': rune.has_accuracy,
            'efficiency': rune.efficiency,
            'max_efficiency': rune.max_efficiency,
            'substat_upgrades_remaining': rune.substat_upgrades_remaining,
            'has_grind': rune.has_grind,
            'has_gem': rune.has_gem,
        }

    class Meta:
        abstract = True


class RuneCraftDropArchive(RuneCraft):
    PARSE_KEYS = ()
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_RUNE_CRAFT,
    )

    RELATED_NAME = 'rune_crafts'

    @classmethod
    def archive_data(cls, rune_craft):
        return {
            'type': rune_craft.type,
            'rune': rune_craft.rune,
            'stat': rune_craft.stat,
            'quality': rune_craft.quality,
            'value': rune_craft.value,
        }

    class Meta:
        abstract = True


class ArtifactDropArchive(Artifact):
    PARSE_ITEM_TYPES = (
        GameItem.CATEGORY_ARTIFACT,
    )

    RELATED_NAME = 'artifacts'

    @classmethod
    def archive_data(cls, artifact):
        return {
            'level': artifact.level,
            'original_quality': artifact.original_quality,
            'main_stat': artifact.main_stat,
            'main_stat_value': artifact.main_stat_value,
            'effects': artifact.effects,
            'effects_value': artifact.effects_value,
            'effects_upgrade_count': artifact.effects_upgrade_count,
            'effects_reroll_count': artifact.effects_reroll_count,
            'efficiency': artifact.efficiency,
            'max_efficiency': artifact.max_efficiency,
            'slot': artifact.slot,
            'element': artifact.element,
            'archetype': artifact.archetype,
            'quality': artifact.quality,
        }

    class Meta:
        abstract = True


# Data gathering model to store game API data for development and debugging purposes
class FullLogArchive(LogArchive):
    command = models.TextField(max_length=150, db_index=True)
    request = JSONField()
    response = JSONField()

    @classmethod
    def archive_data(cls, log):
        return {**{
            'command': log.command,
            'request': log.request,
            'response': log.response,
        }, **LogArchive.archive_data(log)}


# Magic Shop
class ShopRefreshLogArchive(LogArchive):
    objects = ShopRefreshLogManager()

    slots_available = models.IntegerField(blank=True, null=True)

    @classmethod
    def archive_data(cls, log):
        return {**{
            'slots_available': log.slots_available,
        }, **LogArchive.archive_data(log)}


class ShopRefreshDropArchive(models.Model):
    cost = models.IntegerField()

    @classmethod
    def archive_data(cls, log):
        return {
            'cost': log.cost,
        }

    class Meta:
        abstract = True


class ShopRefreshItemDropArchive(ShopRefreshDropArchive, ItemDropArchive):
    log = models.ForeignKey(ShopRefreshLogArchive, on_delete=models.CASCADE, related_name=ItemDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ShopRefreshDropArchive.archive_data(log),\
           **ItemDropArchive.archive_data(log)}


class ShopRefreshRuneDropArchive(ShopRefreshDropArchive, RuneDropArchive):
    log = models.ForeignKey(ShopRefreshLogArchive, on_delete=models.CASCADE, related_name=RuneDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ShopRefreshDropArchive.archive_data(log),\
           **RuneDropArchive.archive_data(log)}


class ShopRefreshMonsterDropArchive(ShopRefreshDropArchive, MonsterDropArchive):
    log = models.ForeignKey(ShopRefreshLogArchive, on_delete=models.CASCADE, related_name=MonsterDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ShopRefreshDropArchive.archive_data(log),\
           **MonsterDropArchive.archive_data(log)}


# Wishes
class WishLogArchive(LogArchive):
    objects = WishLogManager()

    wish_id = models.IntegerField()
    wish_sequence = models.IntegerField()
    crystal_used = models.BooleanField()

    @classmethod
    def archive_data(cls, log):
        return {**{
            'wish_id': log.wish_id,
            'wish_sequence': log.wish_sequence,
            'crystal_used': log.crystal_used,
        }, **LogArchive.archive_data(log)}


class WishLogItemDropArchive(ItemDropArchive):
    log = models.ForeignKey(WishLogArchive, on_delete=models.CASCADE, related_name=ItemDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ItemDropArchive.archive_data(log)}


class WishLogMonsterDropArchive(MonsterDropArchive):
    log = models.ForeignKey(WishLogArchive, on_delete=models.CASCADE, related_name=MonsterDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **MonsterDropArchive.archive_data(log)}


class WishLogRuneDropArchive(RuneDropArchive):
    log = models.ForeignKey(WishLogArchive, on_delete=models.CASCADE, related_name=RuneDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RuneDropArchive.archive_data(log)}


# Rune Crafting
class CraftRuneLogArchive(LogArchive, RuneDropArchive):
    # low, mid, high, ancient
    PARSE_IDS = list(range(1401001, 1401022)) + list(range(1402001, 1402022)) + list(range(1403001, 1403022)) + list(range(1403022, 1403026)) + [1403033]

    CRAFT_LOW = 1
    CRAFT_MID = 2
    CRAFT_HIGH = 3
    CRAFT_ANCIENT = 4
    CRAFT_LEGEND = 5

    CRAFT_CHOICES = [
        (CRAFT_LOW, 'Low'),
        (CRAFT_MID, 'Mid'),
        (CRAFT_HIGH, 'High'),
        (CRAFT_ANCIENT, 'Ancient'),
        (CRAFT_LEGEND, 'Legend'),
    ]

    craft_level = models.IntegerField(choices=CRAFT_CHOICES)
    
    @classmethod
    def archive_data(cls, log):
        return {**{
            'craft_level': log.level,
        }, **LogArchive.archive_data(log),\
           **RuneDropArchive.archive_data(log)}


# Magic Box Crafting
class MagicBoxCraftArchive(LogArchive):
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

    @classmethod
    def archive_data(cls, log):
        return {**{
            'box_type': log.box_type,
        }, **LogArchive.archive_data(log)}


class MagicBoxCraftItemDropArchive(ItemDropArchive):
    log = models.ForeignKey(MagicBoxCraftArchive, on_delete=models.CASCADE, related_name=ItemDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ItemDropArchive.archive_data(log)}


class MagicBoxCraftRuneDropArchive(RuneDropArchive):
    log = models.ForeignKey(MagicBoxCraftArchive, on_delete=models.CASCADE, related_name=RuneDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RuneDropArchive.archive_data(log)}


class MagicBoxCraftRuneCraftDropArchive(RuneCraftDropArchive):
    log = models.ForeignKey(MagicBoxCraftArchive, on_delete=models.CASCADE, related_name=RuneCraftDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RuneCraftDropArchive.archive_data(log)}


# Summons
class SummonLogArchive(LogArchive, MonsterDropArchive):
    # Redefine monster fields to allow nulls due to blessings that do not know which monster is summoned yet
    monster = models.ForeignKey(Monster, on_delete=models.PROTECT, null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)

    item = models.ForeignKey(GameItem, on_delete=models.PROTECT, help_text='Item or currency used to summon')
    blessing_id = models.IntegerField(blank=True, null=True)

    @classmethod
    def archive_data(cls, log):
        return {**{
            'monster_id': log.monster_id,
            'grade': log.grade,
            'level': log.level,
            'item_id': log.item_id,
            'blessing_id': log.blessing_id,
        }, **LogArchive.archive_data(log),\
           **MonsterDropArchive.archive_data(log)}

    def __str__(self):
        return f'SummonLog - {self.item} - {self.monster} {self.grade}*'


# Dungeons
class DungeonLogArchive(LogArchive):
    objects = DungeonLogManager()

    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    success = models.NullBooleanField(db_index=True, help_text='Null indicates that run was not completed')
    clear_time = models.DurationField(blank=True, null=True)

    @classmethod
    def archive_data(cls, log):
        return {**{
            'battle_key': log.battle_key,
            'level_id': log.level_id,
            'success': log.success,
            'clear_time': log.clear_time.total_seconds() if log.clear_time else None,
        }, **LogArchive.archive_data(log)}


class DungeonItemDropArchive(ItemDropArchive):
    log = models.ForeignKey(DungeonLogArchive, on_delete=models.CASCADE, related_name=ItemDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ItemDropArchive.archive_data(log)}


class DungeonMonsterDropArchive(MonsterDropArchive):
    log = models.ForeignKey(DungeonLogArchive, on_delete=models.CASCADE, related_name=MonsterDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **MonsterDropArchive.archive_data(log)}


class DungeonMonsterPieceDropArchive(MonsterPieceDropArchive):
    log = models.ForeignKey(DungeonLogArchive, on_delete=models.CASCADE, related_name=MonsterPieceDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **MonsterPieceDropArchive.archive_data(log)}


class DungeonRuneDropArchive(RuneDropArchive):
    log = models.ForeignKey(DungeonLogArchive, on_delete=models.CASCADE, related_name=RuneDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RuneDropArchive.archive_data(log)}


class DungeonRuneCraftDropArchive(RuneCraftDropArchive):
    log = models.ForeignKey(DungeonLogArchive, on_delete=models.CASCADE, related_name=RuneCraftDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RuneCraftDropArchive.archive_data(log)}


class DungeonArtifactDropArchive(ArtifactDropArchive):
    log = models.ForeignKey(DungeonLogArchive, on_delete=models.CASCADE, related_name=ArtifactDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ArtifactDropArchive.archive_data(log)}


class DungeonSecretDungeonDropArchive(models.Model):
    RELATED_NAME = 'secret_dungeons'
    objects = DungeonSecretDungeonDropManager()

    log = models.ForeignKey(DungeonLogArchive, on_delete=models.CASCADE, related_name=RELATED_NAME)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)


    @classmethod
    def archive_data(cls, archive_log, log):
        return {
            'log': archive_log,
            'level_id': log.level_id,
        }

# Rift dungeon
class RiftDungeonLogArchive(LogArchive):
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
    grade = models.IntegerField(db_index=True, choices=GRADE_CHOICES)
    total_damage = models.IntegerField(db_index=True)
    clear_time = models.DurationField()
    success = models.BooleanField(db_index=True)

    @classmethod
    def archive_data(cls, log):
        return {**{
            'level_id': log.level_id,
            'grade': log.grade,
            'total_damage': log.total_damage,
            'clear_time': log.clear_time.total_seconds() if log.clear_time else None,
            'success': log.success,
        }, **LogArchive.archive_data(log)}

    def __str__(self):
        return f'RiftDungeonLog {self.level} {self.grade}'


class RiftDungeonItemDropArchive(ItemDropArchive):
    log = models.ForeignKey(RiftDungeonLogArchive, on_delete=models.CASCADE, related_name=ItemDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ItemDropArchive.archive_data(log)}


class RiftDungeonMonsterDropArchive(MonsterDropArchive):
    log = models.ForeignKey(RiftDungeonLogArchive, on_delete=models.CASCADE, related_name=MonsterDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **MonsterDropArchive.archive_data(log)}


class RiftDungeonRuneDropArchive(RuneDropArchive):
    log = models.ForeignKey(RiftDungeonLogArchive, on_delete=models.CASCADE, related_name=RuneDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RuneDropArchive.archive_data(log)}


class RiftDungeonRuneCraftDropArchive(RuneCraftDropArchive):
    log = models.ForeignKey(RiftDungeonLogArchive, on_delete=models.CASCADE, related_name=RuneCraftDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RuneCraftDropArchive.archive_data(log)}


# Rift of Worlds Raid
class RiftRaidLogArchive(LogArchive):
    objects = RiftRaidLogManager()

    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    success = models.NullBooleanField(db_index=True, help_text='Null indicates that run was not completed')
    contribution_amount = models.IntegerField(blank=True, null=True)
    clear_time = models.DurationField(blank=True, null=True)

    @classmethod
    def archive_data(cls, log):
        return {**{
            'level_id': log.level_id,
            'battle_key': log.battle_key,
            'success': log.success,
            'contribution_amount': log.contribution_amount,
            'clear_time': log.clear_time.total_seconds() if log.clear_time else None,
        }, **LogArchive.archive_data(log)}


class RiftRaidDropArchive(models.Model):
    wizard_id = models.BigIntegerField()

    @classmethod
    def archive_data(cls, log):
        return {
            'wizard_id': log.wizard_id,
        }

    class Meta:
        abstract = True


class RiftRaidItemDropArchive(RiftRaidDropArchive, ItemDropArchive):
    log = models.ForeignKey(RiftRaidLogArchive, on_delete=models.CASCADE, related_name=ItemDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RiftRaidDropArchive.archive_data(log),\
           **ItemDropArchive.archive_data(log)}


class RiftRaidMonsterDropArchive(RiftRaidDropArchive, MonsterDropArchive):
    log = models.ForeignKey(RiftRaidLogArchive, on_delete=models.CASCADE, related_name=MonsterDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RiftRaidDropArchive.archive_data(log),\
           **MonsterDropArchive.archive_data(log)}


class RiftRaidRuneCraftDropArchive(RiftRaidDropArchive, RuneCraftDropArchive):
    log = models.ForeignKey(RiftRaidLogArchive, on_delete=models.CASCADE, related_name=RuneCraftDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RiftRaidDropArchive.archive_data(log),\
           **RuneCraftDropArchive.archive_data(log)}


# World Boss
class WorldBossLogArchive(LogArchive):
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
    damage = models.IntegerField(db_index=True)
    battle_points = models.IntegerField()
    bonus_battle_points = models.IntegerField()
    avg_monster_level = models.FloatField()
    monster_count = models.IntegerField()

    @classmethod
    def archive_data(cls, log):
        return {**{
            'level_id': log.level_id,
            'battle_key': log.battle_key,
            'grade': log.grade,
            'damage': log.damage,
            'battle_points': log.battle_points,
            'bonus_battle_points': log.bonus_battle_points,
            'avg_monster_level': log.avg_monster_level,
            'monster_count': log.monster_count,
        }, **LogArchive.archive_data(log)}


class WorldBossLogItemDropArchive(ItemDropArchive):
    log = models.ForeignKey(WorldBossLogArchive, on_delete=models.CASCADE, related_name=ItemDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **ItemDropArchive.archive_data(log)}


class WorldBossLogMonsterDropArchive(MonsterDropArchive):
    log = models.ForeignKey(WorldBossLogArchive, on_delete=models.CASCADE, related_name=MonsterDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **MonsterDropArchive.archive_data(log)}


class WorldBossLogRuneDropArchive(RuneDropArchive):
    log = models.ForeignKey(WorldBossLogArchive, on_delete=models.CASCADE, related_name=RuneDropArchive.RELATED_NAME)

    @classmethod
    def archive_data(cls, archive_log, log):
        return {**{
            'log': archive_log,
        }, **RuneDropArchive.archive_data(log)}
