from rest_framework import serializers

from bestiary.models import MonsterGuide
from herders.models import CraftMaterial, MonsterSource as Source, MonsterSkillEffect as Effect, \
    MonsterSkillEffectDetail as EffectDetail, MonsterSkill as Skill, MonsterLeaderSkill as LeaderSkill, \
    HomunculusSkill, HomunculusSkillCraftCost, MonsterCraftCost, Monster, Fusion, Building


class CraftMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CraftMaterial
        fields = ['id', 'url', 'name', 'icon_filename']
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/craft-materials-detail',
            },
        }


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'url', 'name', 'description', 'farmable_source']
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/monster-sources-detail',
            },
        }


class SkillEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Effect
        fields = ('id', 'url', 'name', 'is_buff', 'description', 'icon_filename')
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/skill-effects-detail',
            },
        }


class SkillEffectDetailSerializer(serializers.ModelSerializer):
    effect = SkillEffectSerializer()

    class Meta:
        model = EffectDetail
        fields = [
            'effect',
            'aoe', 'single_target', 'self_effect',
            'chance', 'on_crit', 'on_death', 'random',
            'quantity', 'all', 'self_hp', 'target_hp', 'damage',
            'note',
        ]


class SkillSerializer(serializers.HyperlinkedModelSerializer):
    level_progress_description = serializers.SerializerMethodField()
    effects = SkillEffectDetailSerializer(many=True, read_only=True, source='monsterskilleffectdetail_set')
    scales_with = serializers.SerializerMethodField()
    used_on = serializers.PrimaryKeyRelatedField(source='monster_set', many=True, read_only=True)

    class Meta:
        model = Skill
        fields = (
            'id', 'com2us_id', 'name', 'description', 'slot', 'cooltime', 'hits', 'passive', 'aoe',
            'max_level', 'level_progress_description', 'effects', 'multiplier_formula', 'multiplier_formula_raw',
            'scales_with', 'icon_filename', 'used_on',
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
        model = LeaderSkill
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
    material = CraftMaterialSerializer(source='craft', read_only=True)

    class Meta:
        model = HomunculusSkillCraftCost
        fields = ['material', 'quantity']


class HomunculusSkillSerializer(serializers.ModelSerializer):
    craft_materials = HomunculusSkillCraftCostSerializer(source='homunculusskillcraftcost_set', many=True, read_only=True)
    used_on = serializers.PrimaryKeyRelatedField(source='monsters', many=True, read_only=True)

    class Meta:
        model = HomunculusSkill
        fields = ['id', 'url', 'skill', 'craft_materials', 'mana_cost', 'prerequisites', 'used_on']
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/homunculus-skills-detail',
            },
        }


class MonsterCraftCostSerializer(serializers.ModelSerializer):
    material = CraftMaterialSerializer(source='craft', read_only=True)

    class Meta:
        model = MonsterCraftCost
        fields = ['material', 'quantity']


class MonsterGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonsterGuide
        fields = ['id', 'short_text', 'long_text', 'last_updated']


class MonsterSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='bestiary/monsters-detail')
    element = serializers.SerializerMethodField()
    archetype = serializers.SerializerMethodField()
    source = SourceSerializer(many=True, read_only=True)
    leader_skill = LeaderSkillSerializer(read_only=True)
    homunculus_skills = serializers.PrimaryKeyRelatedField(source='homunculusskill_set', read_only=True, many=True)
    craft_materials = MonsterCraftCostSerializer(many=True, source='monstercraftcost_set', read_only=True)
    resources = serializers.SerializerMethodField()
    guides = MonsterGuideSerializer(source='monsterguide', read_only=True)

    class Meta:
        model = Monster
        fields = (
            'id', 'url', 'com2us_id', 'family_id', 'name', 'image_filename', 'element', 'archetype', 'base_stars',
            'obtainable', 'can_awaken', 'is_awakened', 'awaken_bonus',
            'skills', 'skill_ups_to_max', 'leader_skill', 'homunculus_skills',
            'base_hp', 'base_attack', 'base_defense', 'speed', 'crit_rate', 'crit_damage', 'resistance', 'accuracy',
            'raw_hp', 'raw_attack', 'raw_defense', 'max_lvl_hp', 'max_lvl_attack', 'max_lvl_defense',
            'awakens_from', 'awakens_to',
            'awaken_mats_fire_low', 'awaken_mats_fire_mid', 'awaken_mats_fire_high',
            'awaken_mats_water_low', 'awaken_mats_water_mid', 'awaken_mats_water_high',
            'awaken_mats_wind_low', 'awaken_mats_wind_mid', 'awaken_mats_wind_high',
            'awaken_mats_light_low', 'awaken_mats_light_mid', 'awaken_mats_light_high',
            'awaken_mats_dark_low', 'awaken_mats_dark_mid', 'awaken_mats_dark_high',
            'awaken_mats_magic_low', 'awaken_mats_magic_mid', 'awaken_mats_magic_high',
            'source', 'fusion_food', 'resources', 'guides',
            'homunculus', 'craft_cost', 'craft_materials',
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
    class Meta:
        model = Fusion
        fields = ['id', 'url', 'product', 'stars', 'cost', 'ingredients']
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/fusions-detail',
            },
        }


class BuildingSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()
    affected_stat = serializers.SerializerMethodField()
    element = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = ['id', 'url', 'area', 'affected_stat', 'element', 'com2us_id', 'name', 'max_level', 'stat_bonus', 'upgrade_cost', 'description', 'icon_filename']
        extra_kwargs = {
            'url': {
                'view_name': 'bestiary/buildings-detail',
            },
        }

    def get_area(self, instance):
        return instance.get_area_display()

    def get_affected_stat(self, instance):
        return instance.get_affected_stat_display()

    def get_element(self, instance):
        return instance.get_element_display()