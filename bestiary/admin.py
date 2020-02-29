from django.contrib import admin
from django.db.models import TextField, ForeignKey
from django.forms.widgets import TextInput
from django_select2.forms import Select2Widget

from .models import Monster, Skill, SkillUpgrade, SkillEffectDetail, MonsterCraftCost, Dungeon, Level, \
    HomunculusSkillCraftCost, HomunculusSkill, LeaderSkill, SkillEffect, ScalingStat, \
    Source, Fusion, Building, GameItem, AwakenCost


class MonsterCraftCostInline(admin.TabularInline):
    model = MonsterCraftCost
    extra = 0


class MonsterAwakeningCostInline(admin.TabularInline):
    model = AwakenCost
    extra = 0


@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {
            'fields': (
                'name',
                'com2us_id',
                'family_id',
                'element',
                'archetype',
                'fusion_food',
                'obtainable',
                'image_filename',
                'homunculus',
                'transforms_to',
                'bestiary_slug',
            ),
        }),
        ('Awakening', {
            'fields': (
                'awakens_to',
                'awakens_from',
                'can_awaken',
                'is_awakened',
                'awaken_level',
                'awaken_bonus',
            ),
        }),
        ('Stats', {
            'fields': (
                'base_stars',
                'natural_stars',
                'raw_hp',
                'raw_attack',
                'raw_defense',
                'speed',
                'crit_rate',
                'crit_damage',
                'resistance',
                'accuracy',
                'base_hp',
                'base_attack',
                'base_defense',
                'max_lvl_hp',
                'max_lvl_attack',
                'max_lvl_defense',
            ),
        }),
        ('Skills', {
            'fields': (
                'leader_skill',
                'skills',
                'skill_ups_to_max',
            ),
        }),
        ('Source', {
            'fields': (
                'source',
                'farmable',
            ),
        }),
    ]

    list_display = (
        'image_url',
        'name',
        'obtainable',
        'element',
        'archetype',
        'base_stars',
        'natural_stars',
        'awaken_level',
    )
    list_filter = (
        'element',
        'archetype',
        'base_stars',
        'natural_stars',
        'awaken_level',
        'homunculus',
        'obtainable'
    )
    list_per_page = 100
    filter_vertical = ('skills', )
    filter_horizontal = ('source', )
    inlines = (MonsterAwakeningCostInline, MonsterCraftCostInline, )
    readonly_fields = (
        'bestiary_slug',
        'base_hp',
        'base_attack',
        'base_defense',
        'max_lvl_hp',
        'max_lvl_defense',
        'max_lvl_attack',
    )
    search_fields = ('name', 'com2us_id', )
    save_as = True


class SkillUpgradeInline(admin.TabularInline):
    model = SkillUpgrade
    extra = 0


class EffectDetailInline(admin.StackedInline):
    model = SkillEffectDetail
    extra = 3
    formfield_overrides = {
        TextField: {'widget': TextInput},
    }


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    readonly_fields = ('used_on',)
    list_display = ('image_url', 'name', 'icon_filename', 'description', 'slot', 'passive',)
    filter_vertical = ('skill_effect', 'scaling_stats')
    search_fields = ['com2us_id', 'name', 'description']
    list_filter = ['slot', 'skill_effect', 'passive']
    inlines = (SkillUpgradeInline, EffectDetailInline,)
    save_as = True

    def used_on(self, obj):
        return ', '.join([str(monster) for monster in obj.monster_set.all()])


class HomunculusSkillCraftCostInline(admin.TabularInline):
    model = HomunculusSkillCraftCost
    extra = 4


@admin.register(HomunculusSkill)
class HomunculusSkillAdmin(admin.ModelAdmin):
    list_display = ['skill']
    filter_horizontal = ['monsters', 'prerequisites']
    inlines = (HomunculusSkillCraftCostInline,)
    save_as = True
    formfield_overrides = {
        ForeignKey: {'widget': Select2Widget}
    }


@admin.register(LeaderSkill)
class LeaderSkillAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'attribute', 'amount', 'skill_string', 'area',)
    list_filter = ('attribute', 'area',)


@admin.register(SkillEffect)
class EffectAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'description', 'is_buff')


@admin.register(ScalingStat)
class ScalingStatAdmin(admin.ModelAdmin):
    list_display = ['stat', 'com2us_desc', 'description']
    search_fields = ['stat', 'com2us_desc']
    save_as = True


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'meta_order',)


@admin.register(Fusion)
class FusionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'cost', 'meta_order')
    filter_horizontal = ('ingredients',)


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'com2us_id', 'affected_stat', 'area')
    save_as = True


# Dungeons and levels
class LevelInline(admin.TabularInline):
    model = Level
    extra = 1


@admin.register(Dungeon)
class DungeonAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'com2us_id')
    list_filter = ('enabled', 'category')
    readonly_fields = ('slug', )
    inlines = (
        LevelInline,
    )


# Items and currency
@admin.register(GameItem)
class GameItemAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'com2us_id', 'category', 'name', 'sell_value')
    list_filter = ('category', )