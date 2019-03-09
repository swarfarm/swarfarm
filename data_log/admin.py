from django.contrib import admin

from . import models


# Summons
@admin.register(models.SummonLog)
class SummonLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'item', 'monster')
    readonly_fields = ('summoner', )


# Dungeons
class DungeonItemDropInline(admin.TabularInline):
    model = models.DungeonItemDrop
    readonly_fields = ('item', )
    extra = 0


class DungeonMonsterDropInline(admin.TabularInline):
    model = models.DungeonMonsterDrop
    readonly_fields = ('monster', )
    extra = 0


class DungeonMonsterPieceDrop(admin.TabularInline):
    model = models.DungeonMonsterPieceDrop
    readonly_fields = ('monster', )
    extra = 0


class DungeonRuneDrop(admin.TabularInline):
    model = models.DungeonRuneDrop
    fields = ('type', 'stars', 'level', 'slot', 'quality', 'original_quality', 'value', 'main_stat', 'main_stat_value')
    extra = 0


class DungeonSecretDungeonDrop(admin.TabularInline):
    model = models.DungeonSecretDungeonDrop
    readonly_fields = ('level', )
    extra = 0


@admin.register(models.DungeonLog)
class DungeonLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'level', 'success', 'clear_time')
    readonly_fields = ('summoner', 'level')
    inlines = (
        DungeonItemDropInline,
        DungeonMonsterDropInline,
        DungeonMonsterPieceDrop,
        DungeonRuneDrop,
        DungeonSecretDungeonDrop,
    )
