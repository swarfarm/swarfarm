from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Summoner, MonsterInstance, MonsterTag, Team, TeamGroup, RuneInstance, RuneCraftInstance, \
    BuildingInstance


# User management stuff
class SummonerInline(admin.StackedInline):
    model = Summoner
    can_delete = False
    verbose_name_plural = 'summoners'
    exclude = ('following',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_login', 'date_joined')
    inlines = (SummonerInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(MonsterInstance)
class MonsterInstanceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner')
    filter_vertical = ('tags',)
    exclude = ('owner',)
    search_fields = ['id',]


admin.site.register(MonsterTag)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'group', 'owner')
    filter_horizontal = ('roster',)


@admin.register(TeamGroup)
class TeamGroupAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner')


@admin.register(RuneInstance)
class RuneInstanceAdmin(admin.ModelAdmin):
    list_display = ('type', 'stars', 'level', 'slot', 'owner', 'main_stat')
    search_fields = ('id',)
    exclude = ('owner', 'assigned_to')
    readonly_fields = ('quality', 'has_hp', 'has_atk', 'has_def', 'has_crit_rate', 'has_crit_dmg', 'has_speed', 'has_resist', 'has_accuracy')


@admin.register(RuneCraftInstance)
class RuneCraftInstanceAdmin(admin.ModelAdmin):
    exclude = ('owner',)


admin.site.register(BuildingInstance)