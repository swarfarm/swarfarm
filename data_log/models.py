from django.contrib.postgres.fields import JSONField
from django.db import models

from bestiary.models import Monster, Level, GameItem, Rune, RuneCraft
from herders.models import Summoner


# Abstract models for encapsulating common data like drops and log entry metadata
class LogEntry(models.Model):
    # Abstract model with basic fields required for logging anything

    wizard_id = models.BigIntegerField()
    summoner = models.ForeignKey(Summoner, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    server = models.IntegerField(choices=Summoner.SERVER_CHOICES, null=True, blank=True)

    class Meta:
        abstract = True


class ItemDrop(models.Model):
    item = models.ForeignKey(GameItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.item} x{self.quantity}'


class MonsterDrop(models.Model):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    grade = models.IntegerField()
    level = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.monster} {self.grade}* lv.{self.level}'


class RuneDrop(Rune):
    class Meta:
        abstract = True


class RuneCraftDrop(RuneCraft):
    class Meta:
        abstract = True


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


# Dungeons
class DungeonLog(LogEntry):
    battle_key = models.BigIntegerField(db_index=True, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    success = models.NullBooleanField(help_text='Null indicates that run was not completed')
    clear_time = models.DurationField(blank=True, null=True)


class DungeonLogDrop(models.Model):
    log = models.ForeignKey(DungeonLog, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class DungeonItemDrop(ItemDrop, DungeonLogDrop):
    pass


class DungeonMonsterDrop(MonsterDrop, DungeonLogDrop):
    pass


class DungeonMonsterPieceDrop(DungeonLogDrop):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class DungeonRuneDrop(RuneDrop, DungeonLogDrop):
    pass


class DungeonSecretDungeonDrop(DungeonLogDrop):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)


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
