from rest_framework import serializers

from .models import *


class CraftMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CraftMaterial
        fields = ['name', 'icon_filename']


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        exclude = ['meta_order', 'icon_filename']


class SkillEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Effect
        fields = ('name', 'is_buff', 'description', 'icon_filename')


class SkillEffectDetailSerializer(serializers.ModelSerializer):
    effect = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/skill-effects-detail', read_only=True)

    class Meta:
        model = EffectDetail
        fields = [
            'effect',
            'aoe', 'single_target', 'self_effect',
            'chance', 'on_crit', 'on_death', 'random',
            'quantity', 'all', 'self_hp', 'target_hp', 'damage',
            'note',
        ]


class SkillScalingStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScalingStat
        fields = ('stat',)


class SkillSerializer(serializers.HyperlinkedModelSerializer):
    level_progress_description = serializers.SerializerMethodField()
    effects = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/skill-effects-detail', many=True, read_only=True, source='skill_effect')
    effects_detail = SkillEffectDetailSerializer(many=True, read_only=True, source='monsterskilleffectdetail_set')
    scales_with = SkillScalingStatSerializer(many=True, read_only=True)

    class Meta:
        model = Skill
        fields = (
            'pk', 'com2us_id', 'name', 'description', 'slot', 'cooltime', 'hits', 'passive', 'max_level', 'level_progress_description',
            'effects', 'effects_detail', 'multiplier_formula', 'multiplier_formula_raw', 'scales_with', 'icon_filename',
        )

    def get_level_progress_description(self, instance):
        return instance.level_progress_description.rstrip().split('\n')


class LeaderSkillSerializer(serializers.ModelSerializer):
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
    material = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/craft-materials-detail', read_only=True)

    class Meta:
        model = HomunculusSkillCraftCost
        fields = ['material', 'quantity']


class HomunculusSkillSerializer(serializers.ModelSerializer):
    skill = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/skills-detail', read_only=True)
    craft_materials = HomunculusSkillCraftCostSerializer(source='homunculusskillcraftcost_set', many=True)
    prerequisites = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/homunculus-skills-detail', many=True, read_only=True)

    class Meta:
        model = HomunculusSkill
        fields = ['skill', 'craft_materials', 'mana_cost', 'prerequisites']


class MonsterCraftCostSerializer(serializers.ModelSerializer):
    material = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/craft-materials-detail', source='craft', read_only=True)

    class Meta:
        model = MonsterCraftCost
        fields = ['material', 'quantity']


class MonsterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='apiv2:bestiary/monsters-detail')
    element = serializers.SerializerMethodField()
    archetype = serializers.SerializerMethodField()
    source = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/monster-sources-detail', read_only=True, many=True)
    skills = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/skills-detail', read_only=True, many=True)
    leader_skill = LeaderSkillSerializer(read_only=True)
    homunculus_skills = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/homunculus-skills-detail', source='homunculusskill_set', read_only=True, many=True)
    awakens_from = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/monsters-detail', read_only=True)
    awakens_to = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/monsters-detail', read_only=True)
    craft_materials = MonsterCraftCostSerializer(many=True, source='monstercraftcost_set', read_only=True)
    resources = serializers.SerializerMethodField()

    class Meta:
        model = Monster
        fields = (
            'pk', 'url', 'com2us_id', 'name', 'image_filename', 'element', 'archetype', 'base_stars',
            'obtainable', 'can_awaken', 'is_awakened', 'awaken_bonus',
            'skills', 'leader_skill', 'homunculus_skills', 'skill_ups_to_max',
            'base_hp', 'base_attack', 'base_defense', 'speed', 'crit_rate', 'crit_damage', 'resistance', 'accuracy',
            'max_lvl_hp', 'max_lvl_attack', 'max_lvl_defense',
            'awakens_from', 'awakens_to',
            'awaken_mats_fire_low', 'awaken_mats_fire_mid', 'awaken_mats_fire_high',
            'awaken_mats_water_low', 'awaken_mats_water_mid', 'awaken_mats_water_high',
            'awaken_mats_wind_low', 'awaken_mats_wind_mid', 'awaken_mats_wind_high',
            'awaken_mats_light_low', 'awaken_mats_light_mid', 'awaken_mats_light_high',
            'awaken_mats_dark_low', 'awaken_mats_dark_mid', 'awaken_mats_dark_high',
            'awaken_mats_magic_low', 'awaken_mats_magic_mid', 'awaken_mats_magic_high',
            'source', 'fusion_food', 'resources',
            'homunculus', 'craft_materials', 'craft_cost',
        )

    def get_element(self, instance):
        return instance.get_element_display()

    def get_archetype(self, instance):
        return instance.get_archetype_display()

    def get_resources(self, instance):
        return {
            'Wikia': instance.wikia_url,
            'summonerswar.co': instance.summonerswar_co_url,
            'SummonersWarMonsters.com': instance.summonerswarmonsters_url,
        }


class FusionSerializer(serializers.ModelSerializer):
    product = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/monsters-detail', read_only=True)
    ingredients = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/monsters-detail', read_only=True, many=True)

    class Meta:
        model = Fusion
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()
    affected_stat = serializers.SerializerMethodField()
    element = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = '__all__'

    def get_area(self, instance):
        return instance.get_area_display()

    def get_affected_stat(self, instance):
        return instance.get_affected_stat_display()

    def get_element(self, instance):
        return instance.get_element_display()