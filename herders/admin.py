from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

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
class MonsterAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic Information',  {
            'fields': (
                'name',
                'element',
                'archetype',
                'can_awaken',
                'is_awakened',
                'awakens_from',
                'awakens_to',
                'fusion_food',
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
                'skills',
            )
        })
    ]

    list_display = ('image_url', 'name', 'element', 'archetype', 'base_stars', 'awakens_from')
    list_filter = ('element', 'archetype', 'base_stars', 'is_awakened')
    filter_vertical = ('skills',)
    search_fields = ['name']

admin.site.register(Monster, MonsterAdmin)


class MonsterSkillAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'icon_filename', 'description', 'slot', 'passive', 'general_leader', 'dungeon_leader', 'arena_leader', 'guild_leader')
    filter_vertical = ('skill_effect',)
    list_filter = ('general_leader', 'dungeon_leader', 'arena_leader', 'guild_leader')
    search_fields = ['name', 'icon_filename']
    save_as = True
admin.site.register(MonsterSkill, MonsterSkillAdmin)


class MonsterSkillEffectAdmin(admin.ModelAdmin):
    list_display = ('image_url', 'name', 'description', 'is_buff')
admin.site.register(MonsterSkillEffect, MonsterSkillEffectAdmin)


class FusionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'stars', 'cost',)
    filter_horizontal = ('ingredients',)

admin.site.register(Fusion, FusionAdmin)


class MonsterInstanceAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'owner')
    search_fields = ['owner']

admin.site.register(MonsterInstance, MonsterInstanceAdmin)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'group', 'owner')
    filter_horizontal = ('roster',)

admin.site.register(Team, TeamAdmin)


class TeamGroupAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'owner')

admin.site.register(TeamGroup, TeamGroupAdmin)

admin.site.register(RuneInstance)
