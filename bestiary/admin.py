from django.contrib import admin
from django.db.models import TextField, ForeignKey
from django.forms.widgets import TextInput
from django_select2.forms import Select2Widget

from .models import Monster, Skill, SkillEffectDetail, MonsterCraftCost, Dungeon, Level, \
    HomunculusSkillCraftCost, HomunculusSkill, LeaderSkill, SkillEffect, ScalingStat, \
    Source, Fusion, Building, CraftMaterial, GameItem


class MonsterCraftCostInline(admin.TabularInline):
    model = MonsterCraftCost
    extra = 4


@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {
            'classes': ('suit-tab', 'suit-tab-basic'),
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
                'transforms_into',
                'craft_cost',
            ),
        }),
        ('Awakening', {
            'classes': ('suit-tab', 'suit-tab-awakening'),
            'fields': (
                'awakens_from',
                'awakens_to',
                'can_awaken',
                'is_awakened',
                'awaken_level',
                'awaken_bonus',
            ),
        }),
        ('Awakening Mats', {
            'classes': ('suit-tab', 'suit-tab-awakening'),
            'fields': (
                'awaken_mats_magic_low',
                'awaken_mats_magic_mid',
                'awaken_mats_magic_high',
                'awaken_mats_fire_low',
                'awaken_mats_fire_mid',
                'awaken_mats_fire_high',
                'awaken_mats_water_low',
                'awaken_mats_water_mid',
                'awaken_mats_water_high',
                'awaken_mats_wind_low',
                'awaken_mats_wind_mid',
                'awaken_mats_wind_high',
                'awaken_mats_light_low',
                'awaken_mats_light_mid',
                'awaken_mats_light_high',
                'awaken_mats_dark_low',
                'awaken_mats_dark_mid',
                'awaken_mats_dark_high',
            ),
        }),
        ('Stats', {
            'classes': ('suit-tab', 'suit-tab-basic'),
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
            'classes': ('suit-tab', 'suit-tab-basic'),
            'fields': (
                'leader_skill',
                'skills',
                'skill_ups_to_max',
            ),
        }),
        ('Source', {
            'classes': ('suit-tab', 'suit-tab-other'),
            'fields': (
                'source',
                'farmable',
            ),
        }),
    ]

    list_display = ('image_url', 'name', 'element', 'archetype', 'base_stars', 'natural_stars', 'awakens_from', 'awakens_to')
    list_filter = ('element', 'archetype', 'base_stars', 'natural_stars', 'awaken_level', 'homunculus', 'obtainable')
    list_per_page = 100
    filter_vertical = ('skills',)
    filter_horizontal = ('source',)
    inlines = (MonsterCraftCostInline,)
    readonly_fields = ('bestiary_slug', 'base_hp', 'base_attack', 'base_defense', 'max_lvl_hp', 'max_lvl_defense', 'max_lvl_attack',)
    search_fields = ['name', 'com2us_id']
    save_as = True
    actions = ['resave']

    def resave(self, request, queryset):
        for obj in queryset:
            if obj.skills is not None:
                skill_list = obj.skills.values_list('max_level', flat=True)
                obj.skill_ups_to_max = sum(skill_list) - len(skill_list)
            else:
                obj.skill_ups_to_max = 0

            if obj.awakens_from and obj.awakens_from.source.count() > 0:
                # Update from unawakened version
                obj.source.clear()
                obj.source = obj.awakens_from.source.all()

            obj.save()
    resave.short_description = 'Resave model instances and update data'

    def save_related(self, request, form, formsets, change):
        super(MonsterAdmin, self).save_related(request, form, formsets, change)

        # Copy the unawakened version's sources if they exist.
        # Has to be done here instead of in model's save() because django admin clears M2M on form submit
        if form.instance.awakens_from and form.instance.awakens_from.source.count() > 0:
            # This is the awakened one so copy from awakens_from monster
            form.instance.source.set(form.instance.awakens_from.source.all())

        if form.instance.awakens_to:
            # This is the unawakened one so push to the awakened one
            form.instance.awakens_to.source.set(form.instance.source.all())

        form.instance.save()


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
    inlines = (EffectDetailInline,)
    save_as = True

    def used_on(self, obj):
        return ', '.join([str(monster) for monster in obj.monster_set.all()])


class HomunculusSkillCraftCostInline(admin.TabularInline):
    model = HomunculusSkillCraftCost
    extra = 4


@admin.register(HomunculusSkill)
class HomunculusSkillAdmin(admin.ModelAdmin):
    list_display = ['skill', 'mana_cost']
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
    list_display = ('__str__', 'stars', 'cost', 'meta_order')
    filter_horizontal = ('ingredients',)


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'com2us_id', 'affected_stat', 'area')
    save_as = True


@admin.register(CraftMaterial)
class CraftMaterialAdmin(admin.ModelAdmin):
    list_display = ('image_url', '__str__')
    filter_horizontal = ['source',]
    save_as = True


# Dungeons and levels
class LevelInline(admin.TabularInline):
    model = Level
    extra = 1


@admin.register(Dungeon)
class DungeonAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'com2us_id')
    readonly_fields = ('slug', )
    inlines = (
        LevelInline,
    )


# Items and currency
@admin.register(GameItem)
class GameItemAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'com2us_id', 'category', 'name', 'sell_value')
