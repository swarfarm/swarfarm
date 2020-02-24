from rest_framework import serializers

from bestiary import models


class GameItemSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = models.GameItem
        fields = [
            'id',
            'com2us_id',
            'url',
            'name',
            'category',
            'icon',
            'description',
            'sell_value',
        ]
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/items-detail',
            },
        }

    def get_category(self, instance):
        return instance.get_category_display()


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Source
        fields = ['id', 'url', 'name', 'description', 'farmable_source']
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/monster-sources-detail',
            },
        }


class SkillUpgradeSerializer(serializers.ModelSerializer):
    effect = serializers.SerializerMethodField()

    class Meta:
        model = models.SkillUpgrade
        fields = ('effect', 'amount')

    def get_effect(self, instance):
        return instance.get_effect_display()


class SkillEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SkillEffect
        fields = ('id', 'url', 'name', 'is_buff', 'description', 'icon_filename')
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/skill-effects-detail',
            },
        }


class SkillEffectDetailSerializer(serializers.ModelSerializer):
    effect = SkillEffectSerializer()

    class Meta:
        model = models.SkillEffectDetail
        fields = [
            'effect',
            'aoe', 'single_target', 'self_effect',
            'chance', 'on_crit', 'on_death', 'random',
            'quantity', 'all', 'self_hp', 'target_hp', 'damage',
            'note',
        ]


class SkillSerializer(serializers.HyperlinkedModelSerializer):
    level_progress_description = serializers.SerializerMethodField()
    upgrades = SkillUpgradeSerializer(many=True, read_only=True)
    effects = SkillEffectDetailSerializer(many=True, read_only=True, source='skilleffectdetail_set')
    scales_with = serializers.SerializerMethodField()
    used_on = serializers.PrimaryKeyRelatedField(source='monster_set', many=True, read_only=True)

    class Meta:
        model = models.Skill
        fields = (
            'id', 'com2us_id', 'name', 'description', 'slot', 'cooltime', 'hits', 'passive', 'aoe',
            'max_level', 'upgrades', 'effects', 'multiplier_formula', 'multiplier_formula_raw',
            'scales_with', 'icon_filename', 'used_on', 'level_progress_description',
        )

    def get_level_progress_description(self, instance):
        if instance.level_progress_description:
            return instance.level_progress_description.rstrip().split('\n')
        else:
            return []

    def get_scales_with(self, instance):
        return instance.scaling_stats.values_list('stat', flat=True)


class LeaderSkillSerializer(serializers.ModelSerializer):
    attribute = serializers.SerializerMethodField('get_stat')
    area = serializers.SerializerMethodField()
    element = serializers.SerializerMethodField()

    class Meta:
        model = models.LeaderSkill
        fields = ('id', 'url', 'attribute', 'amount', 'area', 'element')
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/leader-skills-detail',
            },
        }

    def get_stat(self, instance):
        return instance.get_attribute_display()

    def get_area(self, instance):
        return instance.get_area_display()

    def get_element(self, instance):
        return instance.get_element_display()


class HomunculusSkillCraftCostSerializer(serializers.ModelSerializer):
    item = GameItemSerializer(read_only=True)

    class Meta:
        model = models.HomunculusSkillCraftCost
        fields = ['item', 'quantity']


class HomunculusSkillSerializer(serializers.ModelSerializer):
    craft_materials = HomunculusSkillCraftCostSerializer(source='homunculusskillcraftcost_set', many=True, read_only=True)
    used_on = serializers.PrimaryKeyRelatedField(source='monsters', many=True, read_only=True)

    class Meta:
        model = models.HomunculusSkill
        fields = ['id', 'url', 'skill', 'craft_materials', 'prerequisites', 'used_on']
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/homunculus-skills-detail',
            },
        }


class MonsterCraftCostSerializer(serializers.ModelSerializer):
    item = GameItemSerializer(read_only=True)

    class Meta:
        model = models.MonsterCraftCost
        fields = ['item', 'quantity']


class AwakenCostSerializer(serializers.ModelSerializer):
    item = GameItemSerializer(read_only=True)

    class Meta:
        model = models.AwakenCost
        fields = ['item', 'quantity']


class MonsterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='bestiary/monsters-detail')
    element = serializers.SerializerMethodField()
    archetype = serializers.SerializerMethodField()
    source = SourceSerializer(many=True, read_only=True)
    leader_skill = LeaderSkillSerializer(read_only=True)
    awaken_cost = AwakenCostSerializer(source='awakencost_set', many=True, read_only=True)
    homunculus_skills = serializers.PrimaryKeyRelatedField(source='homunculusskill_set', read_only=True, many=True)
    craft_materials = MonsterCraftCostSerializer(many=True, source='monstercraftcost_set', read_only=True)

    class Meta:
        model = models.Monster
        fields = (
            'id', 'url', 'com2us_id', 'family_id',
            'name', 'image_filename', 'element', 'archetype', 'base_stars', 'natural_stars',
            'obtainable', 'can_awaken', 'awaken_level', 'awaken_bonus',
            'skills', 'skill_ups_to_max', 'leader_skill', 'homunculus_skills',
            'base_hp', 'base_attack', 'base_defense', 'speed', 'crit_rate', 'crit_damage', 'resistance', 'accuracy',
            'raw_hp', 'raw_attack', 'raw_defense', 'max_lvl_hp', 'max_lvl_attack', 'max_lvl_defense',
            'awakens_from', 'awakens_to', 'awaken_cost',
            'source', 'fusion_food',
            'homunculus', 'craft_cost', 'craft_materials',
        )

    def get_element(self, instance):
        return instance.get_element_display()

    def get_archetype(self, instance):
        return instance.get_archetype_display()


class FusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Fusion
        fields = ['id', 'url', 'product', 'cost', 'ingredients']
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/fusions-detail',
            },
        }


class BuildingSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='bestiary/buildings-detail')
    area = serializers.SerializerMethodField()
    affected_stat = serializers.SerializerMethodField()
    element = serializers.SerializerMethodField()

    class Meta:
        model = models.Building
        fields = [
            'id',
            'url',
            'area',
            'affected_stat',
            'element',
            'com2us_id',
            'name',
            'max_level',
            'stat_bonus',
            'upgrade_cost',
            'description',
            'icon_filename',
        ]

    def get_area(self, instance):
        return instance.get_area_display()

    def get_affected_stat(self, instance):
        return instance.get_affected_stat_display()

    def get_element(self, instance):
        return instance.get_element_display()


class DungeonSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='bestiary/dungeons-detail')
    levels = serializers.PrimaryKeyRelatedField(source='level_set', read_only=True, many=True)
    category = serializers.SerializerMethodField()

    class Meta:
        model = models.Dungeon
        fields = [
            'id',
            'url',
            'enabled',
            'name',
            'slug',
            'category',
            'icon',
            'levels',
        ]

    def get_category(self, instance):
        return instance.get_category_display()


class EnemySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enemy
        fields = [
            'id',
            'monster',
            'stars',
            'level',
            'hp',
            'attack',
            'defense',
            'speed',
            'resist',
            'crit_bonus',
            'crit_damage_reduction',
            'accuracy_bonus',
        ]


class WaveSerializer(serializers.ModelSerializer):
    enemies = EnemySerializer(source='enemy_set', many=True, read_only=True)

    class Meta:
        model = models.Wave
        fields = [
            'enemies',
        ]

class LevelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='bestiary/levels-detail')
    difficulty = serializers.SerializerMethodField()
    waves = WaveSerializer(source='wave_set', many=True, read_only=True)

    class Meta:
        model = models.Level
        fields = [
            'id',
            'url',
            'dungeon',
            'floor',
            'difficulty',
            'energy_cost',
            'xp',
            'frontline_slots',
            'backline_slots',
            'total_slots',
            'waves',
        ]

    def get_difficulty(self, instance):
        return instance.get_difficulty_display()
