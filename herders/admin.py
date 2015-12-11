from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


# User management stuff
class SummonerInline(admin.StackedInline):
    model = Summoner
    can_delete = False
    verbose_name_plural = 'summoners'
    exclude = ('following',)


class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_login', 'date_joined')
    inlines = (SummonerInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Monster Database stuff
@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    suit_form_tabs = (('basic', 'Basic Info'), ('awakening', 'Awakening'), ('other', 'Other'))
    fieldsets = [
        ('Basic Information', {
            'classes': ('suit-tab', 'suit-tab-basic'),
            'fields': (
                'name',
                'element',
                'archetype',
                'fusion_food',
                'obtainable',
            ),
        }),
        ('Awakening', {
            'classes': ('suit-tab', 'suit-tab-awakening'),
            'fields': (
                'awakens_from',
                'awakens_to',
                'can_awaken',
                'is_awakened',
                'awaken_bonus',
                'awaken_bonus_content_type',
                'awaken_bonus_content_id',
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
                'base_hp',
                'base_attack',
                'base_defense',
                'speed',
                'crit_rate',
                'crit_damage',
                'resistance',
                'accuracy',
                'max_lvl_hp',
                'max_lvl_defense',
                'max_lvl_attack',
            ),
        }),
        ('Skills', {
            'classes': ('suit-tab', 'suit-tab-basic'),
            'fields': (
                'leader_skill',
                'skills',
            ),
        }),
        ('Source', {
            'classes': ('suit-tab', 'suit-tab-other'),
            'fields': (
                'source',
            ),
        }),
        ('Resources', {
            'classes': ('suit-tab', 'suit-tab-other'),
            'fields': (
                'summonerswar_co_url',
                'wikia_url',
                'bestiary_slug',
            ),
        }),
    ]

    list_display = ('image_url', 'name', 'element', 'archetype', 'base_stars', 'awakens_from', 'awakens_to')
    list_filter = ('element', 'archetype', 'base_stars', 'is_awakened', 'can_awaken')
    filter_vertical = ('skills',)
    filter_horizontal = ('source',)
    readonly_fields = ('bestiary_slug', 'max_lvl_hp', 'max_lvl_defense', 'max_lvl_attack')
    search_fields = ['name']
    save_as = True

    def save_related(self, request, form, formsets, change):
        super(MonsterAdmin, self).save_related(request, form, formsets, change)

        # Copy the unawakened version's sources if they exist.
        # Has to be done here instead of in model's save() because django admin clears M2M on form submit
        if form.instance.awakens_from and form.instance.awakens_from.source.count() > 0:
            form.instance.source.clear()
            form.instance.source = form.instance.awakens_from.source.all()


@admin.register(MonsterSkill)
class MonsterSkillAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'icon_filename', 'description', 'slot', 'passive',)
    filter_vertical = ('skill_effect',)
    search_fields = ['name', 'icon_filename', 'description']
    list_filter = ['slot', 'skill_effect', 'passive']
    save_as = True


@admin.register(MonsterLeaderSkill)
class MonsterLeaderSkillAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'attribute', 'amount', 'skill_string', 'area',)
    list_filter = ('attribute', 'area',)


@admin.register(MonsterSkillEffect)
class MonsterSkillEffectAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'description', 'is_buff')


@admin.register(MonsterSource)
class MonsterSourceAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'meta_order',)


@admin.register(Fusion)
class FusionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'stars', 'cost', 'meta_order')
    filter_horizontal = ('ingredients',)


@admin.register(MonsterInstance)
class MonsterInstanceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'owner')
    exclude = ('owner',)
    search_fields = ['id',]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'group', 'owner')
    filter_horizontal = ('roster',)


@admin.register(TeamGroup)
class TeamGroupAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'owner')


@admin.register(RuneInstance)
class RuneInstanceAdmin(admin.ModelAdmin):
    list_display = ('type', 'stars', 'level', 'slot', 'owner', 'main_stat')
    search_fields = ('id',)
    exclude = ('owner', 'assigned_to')
    readonly_fields = ('quality', 'has_hp', 'has_atk', 'has_def', 'has_crit_rate', 'has_crit_dmg', 'has_speed', 'has_resist', 'has_accuracy')

admin.site.register(GameEvent)
