from django.contrib import admin

from . import models


# Shop Refresh
class ShopRefreshItemDropInline(admin.TabularInline):
    model = models.ShopRefreshItemDrop
    readonly_fields = ('item', )
    extra = 0


class ShopRefreshMonsterDropInline(admin.TabularInline):
    model = models.ShopRefreshMonsterDrop
    readonly_fields = ('monster', )
    extra = 0


class ShopRefreshRuneDropInline(admin.TabularInline):
    model = models.ShopRefreshRuneDrop
    fields = ('type', 'stars', 'cost', 'slot', 'quality', 'value', 'main_stat', 'main_stat_value')
    extra = 0


@admin.register(models.ShopRefreshLog)
class ShopRefreshLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner')
    readonly_fields = ('summoner', )
    inlines = (
        ShopRefreshItemDropInline,
        ShopRefreshMonsterDropInline,
        ShopRefreshRuneDropInline,
    )


# Wishes
class WishLogItemDropInline(admin.TabularInline):
    model = models.WishLogItemDrop
    readonly_fields = ('item', )
    extra = 0


class WishLogMonsterDropInline(admin.TabularInline):
    model = models.WishLogMonsterDrop
    readonly_fields = ('monster', )
    extra = 0


class WishLogRuneDropInline(admin.TabularInline):
    model = models.WishLogRuneDrop
    fields = ('type', 'stars', 'slot', 'quality', 'value', 'main_stat', 'main_stat_value')
    extra = 0


@admin.register(models.WishLog)
class WishLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner')
    readonly_fields = ('summoner', )
    inlines = (
        WishLogItemDropInline,
        WishLogMonsterDropInline,
        WishLogRuneDropInline,
    )


# Rune Crafting
@admin.register(models.CraftRuneLog)
class CraftRuneLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'craft_level', 'type', 'stars')
    readonly_fields = ('summoner', )


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


class DungeonMonsterPieceDropInline(admin.TabularInline):
    model = models.DungeonMonsterPieceDrop
    readonly_fields = ('monster', )
    extra = 0


class DungeonRuneDropInline(admin.TabularInline):
    model = models.DungeonRuneDrop
    fields = ('type', 'stars', 'level', 'slot', 'quality', 'original_quality', 'value', 'main_stat', 'main_stat_value')
    extra = 0


class DungeonSecretDungeonDropInline(admin.TabularInline):
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
        DungeonMonsterPieceDropInline,
        DungeonRuneDropInline,
        DungeonSecretDungeonDropInline,
    )
