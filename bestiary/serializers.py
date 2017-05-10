from rest_framework import serializers

from .models import *


class CraftMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CraftMaterial
        fields = ['name', 'icon_filename']


class MonsterSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        exclude = ['meta_order', 'icon_filename']


class MonsterSkillEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Effect
        fields = ('name', 'is_buff', 'description', 'icon_filename')


class MonsterSkillScalingStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScalingStat
        fields = ('stat',)


class MonsterSkillSerializer(serializers.HyperlinkedModelSerializer):
    skill_effect = MonsterSkillEffectSerializer(many=True, read_only=True)
    scales_with = MonsterSkillScalingStatSerializer(many=True, read_only=True)

    class Meta:
        model = Skill
        fields = (
            'pk', 'com2us_id', 'name', 'description', 'slot', 'cooltime', 'hits', 'passive', 'max_level', 'level_progress_description',
            'skill_effect', 'multiplier_formula', 'multiplier_formula_raw', 'scales_with', 'icon_filename',
        )


class MonsterLeaderSkillSerializer(serializers.ModelSerializer):
    attribute = serializers.SerializerMethodField('get_stat')
    area = serializers.SerializerMethodField()
    element = serializers.SerializerMethodField()

    class Meta:
        model = LeaderSkill
        fields = ('attribute', 'amount', 'area', 'element')

    def get_stat(self, instance):
        return instance.get_attribute_display()

    def get_area(self, instance):
        return instance.get_area_display()

    def get_element(self, instance):
        return instance.get_element_display()


class HomunculusSkillCraftCostSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='craft.name')
    icon_filename = serializers.ReadOnlyField(source='craft.icon_filename')

    class Meta:
        model = HomunculusSkillCraftCost
        fields = ['name', 'quantity', 'icon_filename']


class HomunculusSkillSerializer(serializers.ModelSerializer):
    skill = MonsterSkillSerializer(read_only=True)
    craft_materials = HomunculusSkillCraftCostSerializer(source='homunculusskillcraftcost_set', many=True)

    class Meta:
        model = HomunculusSkill
        fields = ['skill', 'craft_materials', 'mana_cost', 'prerequisites',]


# Small serializer for necessary info for awakens_from/to on main MonsterSerializer
class AwakensMonsterSerializer(serializers.HyperlinkedModelSerializer):
    element = serializers.SerializerMethodField()

    class Meta:
        model = Monster
        fields = ('url', 'pk', 'name', 'element')

    def get_element(self, instance):
        return instance.get_element_display()


class MonsterSerializer(serializers.ModelSerializer):
    element = serializers.SerializerMethodField()
    archetype = serializers.SerializerMethodField()
    source = MonsterSourceSerializer(many=True, read_only=True)
    homunculus_skills = HomunculusSkillSerializer(many=True, source='homunculusskill_set')

    class Meta:
        model = Monster
        fields = (
            'pk', 'url', 'com2us_id', 'name', 'image_filename', 'element', 'archetype', 'base_stars',
            'obtainable', 'can_awaken', 'is_awakened', 'awaken_bonus',
            'skills', 'leader_skill', 'homunculus_skills',
            'base_hp', 'base_attack', 'base_defense', 'speed', 'crit_rate', 'crit_damage', 'resistance', 'accuracy',
            'max_lvl_hp', 'max_lvl_attack', 'max_lvl_defense',
            'awakens_from', 'awakens_to',
            'awaken_mats_fire_low', 'awaken_mats_fire_mid', 'awaken_mats_fire_high',
            'awaken_mats_water_low', 'awaken_mats_water_mid', 'awaken_mats_water_high',
            'awaken_mats_wind_low', 'awaken_mats_wind_mid', 'awaken_mats_wind_high',
            'awaken_mats_light_low', 'awaken_mats_light_mid', 'awaken_mats_light_high',
            'awaken_mats_dark_low', 'awaken_mats_dark_mid', 'awaken_mats_dark_high',
            'awaken_mats_magic_low', 'awaken_mats_magic_mid', 'awaken_mats_magic_high',
            'source', 'fusion_food'
        )

    def get_element(self, instance):
        return instance.get_element_display()

    def get_archetype(self, instance):
        return instance.get_archetype_display()


# Limited fields for displaying list view sort of display.
class MonsterSummarySerializer(serializers.HyperlinkedModelSerializer):
    element = serializers.SerializerMethodField()
    archetype = serializers.SerializerMethodField()

    class Meta:
        model = Monster
        fields = ('url', 'pk', 'com2us_id', 'name', 'image_filename', 'element', 'archetype', 'base_stars', 'fusion_food',)

    def get_element(self, instance):
        return instance.get_element_display()

    def get_archetype(self, instance):
        return instance.get_archetype_display()