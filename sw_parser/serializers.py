from rest_framework import serializers

from .models import *


# These serializers are used to export data to disk
class MonsterDropSerializer(serializers.ModelSerializer):
    monster = serializers.CharField(source='monster.name')
    element = serializers.CharField(source='monster.get_element_display')
    com2us_id = serializers.IntegerField(source='monster.com2us_id')
    family_id = serializers.IntegerField(source='monster.family_id')

    class Meta:
        model = MonsterDrop
        fields = ['monster', 'element', 'grade', 'level', 'com2us_id', 'family_id']


class RuneDropSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display')
    quality = serializers.CharField(source='get_quality_display')
    main_stat = serializers.CharField(source='get_main_stat_display')
    innate_stat = serializers.CharField(source='get_innate_stat_display')
    substat_1 = serializers.CharField(source='get_substat_1_display')
    substat_2 = serializers.CharField(source='get_substat_2_display')
    substat_3 = serializers.CharField(source='get_substat_3_display')
    substat_4 = serializers.CharField(source='get_substat_4_display')

    class Meta:
        model = RuneDrop
        exclude = ['id']


# Scenario and Dungeon runs
class RunLogSerializer(serializers.ModelSerializer):
    server = serializers.CharField(source='get_server_display')
    dungeon = serializers.CharField(source='dungeon.name')
    difficulty = serializers.CharField(source='get_difficulty_display')
    drop_type = serializers.CharField(source='get_drop_type_display')
    drop_monster = MonsterDropSerializer()
    drop_rune = RuneDropSerializer()

    class Meta:
        model = RunLog
        exclude = ['wizard_id', 'summoner']
        depth = 1


# Summons
class SummonLogSerializer(serializers.ModelSerializer):
    server = serializers.CharField(source='get_server_display')
    summon_method = serializers.CharField(source='get_summon_method_display')
    monster = MonsterDropSerializer()

    class Meta:
        model = SummonLog
        exclude = ['wizard_id', 'summoner']
        depth = 1


# Rift dungeons
class RiftDungeonMonsterDropSerializer(MonsterDropSerializer):
    class Meta(MonsterDropSerializer.Meta):
        model = RiftDungeonMonsterDrop


class RiftDungeonItemDropSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source='get_item_display')

    class Meta:
        model = RiftDungeonItemDrop
        exclude = ['id', 'log']


class RiftDungeonLogSerializer(serializers.ModelSerializer):
    dungeon = serializers.CharField(source='get_dungeon_display')
    grade = serializers.CharField(source='get_grade_display')
    item_drops = RiftDungeonItemDropSerializer(many=True)
    monster_drops = RiftDungeonMonsterDropSerializer(many=True)

    class Meta:
        model = RiftDungeonLog
        depth = 1
        fields = ['id', 'dungeon', 'grade', 'success', 'total_damage', 'mana', 'item_drops', 'monster_drops']


# World Boss
class WorldBossMonsterDropSerializer(MonsterDropSerializer):
    class Meta(MonsterDropSerializer.Meta):
        model = WorldBossMonsterDrop


class WorldBossItemDropSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source='get_item_display')

    class Meta:
        model = WorldBossItemDrop
        exclude = ['id', 'log']


class WorldBossRuneDropSerializer(RuneDropSerializer):
    class Meta(RuneDropSerializer.Meta):
        model = WorldBossRuneDrop
        exclude = ['id', 'log']


class WorldBossLogSerializer(serializers.ModelSerializer):
    grade = serializers.CharField(source='get_grade_display')
    monster_drops = WorldBossMonsterDropSerializer(many=True)
    rune_drops = WorldBossRuneDropSerializer(many=True)
    item_drops = WorldBossItemDropSerializer(many=True)

    class Meta:
        model = WorldBossLog
        fields = ['id', 'grade', 'damage', 'battle_points', 'bonus_battle_points', 'avg_monster_level', 'monster_count', 'monster_drops', 'item_drops', 'rune_drops']


# Rune Crafts
class RuneCraftLogSerializer(serializers.ModelSerializer):
    craft_level = serializers.CharField(source='get_craft_level_display')
    rune = RuneDropSerializer(many=True)

    class Meta:
        model = RuneCraftLog
        fields = ['id', 'craft_level', 'rune']


# Shop Refreshes
class ShopRefreshItemSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source='get_item_display')

    class Meta:
        model = ShopRefreshItem
        exclude = ['id', 'log']


class ShopRefreshRuneSerializer(RuneDropSerializer):
    class Meta(RuneDropSerializer.Meta):
        model = ShopRefreshRune
        exclude = ['id', 'log']


class ShopRefreshMonsterSerializer(MonsterDropSerializer):
    class Meta(MonsterDropSerializer.Meta):
        model = ShopRefreshMonster
        fields = ['cost', 'monster', 'element', 'grade', 'level', 'com2us_id', 'family_id']


class ShopRefreshLogSerializer(serializers.ModelSerializer):
    rune_drops = ShopRefreshRuneSerializer(many=True)
    item_drops = ShopRefreshItemSerializer(many=True)
    monster_drops = ShopRefreshMonsterSerializer(many=True)

    class Meta:
        model = ShopRefreshLog
        fields = ['id', 'slots_available', 'rune_drops', 'item_drops', 'monster_drops']
