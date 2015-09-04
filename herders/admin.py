from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *


# User management stuff
class SummonerInline(admin.StackedInline):
    model = Summoner
    can_delete = False
    verbose_name_plural = 'summoner'


class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_login', 'date_joined')
    inlines = (SummonerInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Monster Database stuff
@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information', {
            'fields': (
                'name',
                'element',
                'archetype',
                'can_awaken',
                'is_awakened',
                'awaken_bonus',
                'awakens_from',
                'awakens_to',
                'fusion_food',
                'obtainable',
            )
        }),
        ('Stats', {
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
            )
        }),
        ('Awakening Materials', {
            'fields': (
                'awaken_magic_mats_low',
                'awaken_magic_mats_mid',
                'awaken_magic_mats_high',
                'awaken_ele_mats_low',
                'awaken_ele_mats_mid',
                'awaken_ele_mats_high',
            )
        }),
        ('Skills', {
            'fields': (
                'leader_skill',
                'skills',
            )
        }),
        ('Source', {
            'fields': (
                'source',
            )
        }),
    ]

    list_display = ('image_url', 'name', 'element', 'archetype', 'base_stars', 'awakens_from', 'awakens_to')
    list_filter = ('element', 'archetype', 'base_stars', 'is_awakened', 'can_awaken')
    filter_vertical = ('skills',)
    filter_horizontal = ('source',)
    search_fields = ['name']
    save_as = True


@admin.register(MonsterSkill)
class MonsterSkillAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'icon_filename', 'description', 'slot', 'passive',)
    filter_vertical = ('skill_effect',)
    search_fields = ['name', 'icon_filename']
    list_filter = ['slot', 'skill_effect', 'passive']
    save_as = True


@admin.register(MonsterLeaderSkill)
class MonsterLeaderSkillAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'attribute', 'amount', 'skill_string', 'dungeon_skill', 'element_skill', 'arena_skill', 'guild_skill')
    list_filter = ('attribute', 'dungeon_skill', 'element_skill', 'arena_skill', 'guild_skill')


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
    search_fields = ['id',]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'group', 'owner')
    filter_horizontal = ('roster',)


@admin.register(TeamGroup)
class TeamGroupAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'owner')


admin.site.register(RuneInstance)

admin.site.register(GameEvent)