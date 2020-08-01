from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from . import models


# User management stuff
class SummonerInline(admin.StackedInline):
    model = models.Summoner
    can_delete = False
    verbose_name_plural = 'summoners'
    exclude = ('following',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_login', 'date_joined')
    inlines = (SummonerInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class RuneInstanceInline(admin.TabularInline):
    model = models.RuneInstance
    fields = (
        'stars',
        'level',
        'slot',
        'quality',
        'ancient',
        'main_stat',
        'main_stat_value',
        'innate_stat',
        'innate_stat_value',
        'substats',
        'substat_values',
        'efficiency',
    )
    extra = 0
    show_change_link = True


class RuneBuildInline(admin.TabularInline):
    model = models.RuneBuild
    exclude = ('owner', 'runes', )
    extra = 0
    show_change_link = True


@admin.register(models.MonsterInstance)
class MonsterInstanceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner')
    filter_vertical = ('tags',)
    exclude = ('owner',)
    search_fields = ('id', )
    readonly_fields = ('default_build', 'rta_build', )
    inlines = (RuneInstanceInline, RuneBuildInline,)


admin.site.register(models.MonsterTag)


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'group', 'owner')
    filter_horizontal = ('roster',)


@admin.register(models.TeamGroup)
class TeamGroupAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner')


@admin.register(models.RuneInstance)
class RuneInstanceAdmin(admin.ModelAdmin):
    list_display = ('type', 'stars', 'level', 'slot', 'owner', 'main_stat')
    search_fields = ('id',)
    exclude = ('owner', 'assigned_to')
    readonly_fields = ('quality', 'has_hp', 'has_atk', 'has_def', 'has_crit_rate', 'has_crit_dmg', 'has_speed', 'has_resist', 'has_accuracy')


@admin.register(models.RuneBuild)
class RuneBuildAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'owner',
        'monster',
    )
    readonly_fields = ('owner', 'monster', 'runes', )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'monster',
            'monster__monster'
        )


@admin.register(models.RuneCraftInstance)
class RuneCraftInstanceAdmin(admin.ModelAdmin):
    exclude = ('owner',)


@admin.register(models.ArtifactInstance)
class ArtifactInstanceAdmin(admin.ModelAdmin):
    readonly_fields = ('owner', 'assigned_to')


@admin.register(models.ArtifactCraftInstance)
class ArtifactCraftInstanceAdmin(admin.ModelAdmin):
    readonly_fields = ('owner', )


admin.site.register(models.BuildingInstance)