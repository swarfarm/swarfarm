from django.contrib import admin

from . import models


# Full Log
@admin.register(models.FullLog)
class FullLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'command', 'wizard_id', 'summoner')
    search_fields = ('wizard_id', 'summoner__user__username', 'command')
    readonly_fields = ('summoner', )


# Common drop inlines
class ItemDropInline(admin.TabularInline):
    readonly_fields = ('item', )
    extra = 0


class MonsterDropInline(admin.TabularInline):
    readonly_fields = ('monster',)
    extra = 0


class RuneDropInline(admin.TabularInline):
    fields = ('type', 'stars', 'level', 'slot', 'quality', 'value', 'main_stat', 'main_stat_value')
    extra = 0


class RuneCraftDropinline(admin.TabularInline):
    fields = ('type', 'rune', 'stat', 'quality', 'value')
    extra = 0


# Shop Refresh
class ShopRefreshItemDropDropInline(ItemDropInline):
    model = models.ShopRefreshItemDrop


class ShopRefreshMonsterDropInline(MonsterDropInline):
    model = models.ShopRefreshMonsterDrop


class ShopRefreshRuneDropInline(RuneDropInline):
    model = models.ShopRefreshRuneDrop


@admin.register(models.ShopRefreshLog)
class ShopRefreshLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner')
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', )
    inlines = (
        ShopRefreshItemDropDropInline,
        ShopRefreshMonsterDropInline,
        ShopRefreshRuneDropInline,
    )


# Wishes
class WishLogItemDropDropInline(ItemDropInline):
    model = models.WishLogItemDrop


class WishLogMonsterDropInline(MonsterDropInline):
    model = models.WishLogMonsterDrop


class WishLogRuneDropInline(RuneDropInline):
    model = models.WishLogRuneDrop


@admin.register(models.WishLog)
class WishLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner')
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', )
    inlines = (
        WishLogItemDropDropInline,
        WishLogMonsterDropInline,
        WishLogRuneDropInline,
    )


# Rune Crafting
@admin.register(models.CraftRuneLog)
class CraftRuneLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'craft_level', 'type', 'stars')
    list_filter = ('craft_level', 'type', 'stars')
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', )


# Magic Box Crafting
class MagicBoxCraftItemDropInline(ItemDropInline):
    model = models.MagicBoxCraftItemDrop


class MagicBoxCraftRuneDropInline(RuneDropInline):
    model = models.MagicBoxCraftRuneDrop


class MagicBoxCraftRuneCraftDropInline(RuneCraftDropinline):
    model = models.MagicBoxCraftRuneCraftDrop


@admin.register(models.MagicBoxCraft)
class MagicBoxCraftlogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'box_type')
    list_filter = ('box_type', )
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', )
    inlines = (
        MagicBoxCraftItemDropInline,
        MagicBoxCraftRuneDropInline,
        MagicBoxCraftRuneCraftDropInline,
    )


# Summons
@admin.register(models.SummonLog)
class SummonLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'item', 'monster')
    list_filter = ('item', )
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', )


# Dungeons
class DungeonItemDropDropInline(ItemDropInline):
    model = models.DungeonItemDrop


class DungeonMonsterDropInline(MonsterDropInline):
    model = models.DungeonMonsterDrop


class DungeonMonsterPieceDropInline(MonsterDropInline):
    model = models.DungeonMonsterPieceDrop


class DungeonRuneDropInline(RuneDropInline):
    model = models.DungeonRuneDrop


class DungeonSecretDungeonDropInline(admin.TabularInline):
    model = models.DungeonSecretDungeonDrop
    readonly_fields = ('level', )
    extra = 0


@admin.register(models.DungeonLog)
class DungeonLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'level', 'success', 'clear_time')
    list_filter = ('level__dungeon__name', 'success')
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', 'level')
    inlines = (
        DungeonItemDropDropInline,
        DungeonMonsterDropInline,
        DungeonMonsterPieceDropInline,
        DungeonRuneDropInline,
        DungeonSecretDungeonDropInline,
    )


class RiftDungeonItemDropInline(ItemDropInline):
    model = models.RiftDungeonItemDrop


class RiftDungeonMonsterDropInlne(MonsterDropInline):
    model = models.RiftDungeonMonsterDrop


class RiftDungeonRuneDropInline(RuneDropInline):
    model = models.RiftDungeonRuneDrop


class RiftDungeonRuneCraftDropInline(RuneCraftDropinline):
    model = models.RiftDungeonRuneCraftDrop


@admin.register(models.RiftDungeonLog)
class RiftDungeonLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'level', 'grade', 'clear_time')
    list_filter = ('level__dungeon__name', 'success')
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', 'level')
    inlines = (
        RiftDungeonItemDropInline,
        RiftDungeonMonsterDropInlne,
        RiftDungeonRuneDropInline,
        RiftDungeonRuneCraftDropInline,
    )


# Rift Raid
class RiftRaidItemDropInline(ItemDropInline):
    model = models.RiftRaidItemDrop


class RiftRaidRuneCraftDropInline(RuneCraftDropinline):
    model = models.RiftRaidRuneCraftDrop


class RiftRaidMonsterDropInline(MonsterDropInline):
    model = models.RiftRaidMonsterDrop


@admin.register(models.RiftRaidLog)
class RiftRaidLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'level', 'clear_time', 'success')
    list_filter = ('level__dungeon__name', 'success')
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', 'level')
    inlines = (
        RiftRaidItemDropInline,
        RiftRaidRuneCraftDropInline,
        RiftRaidMonsterDropInline,
    )


# World Boss
class WorldBossItemDropInline(ItemDropInline):
    model = models.WorldBossLogItemDrop


class WorldBossMonsterDropInline(MonsterDropInline):
    model = models.WorldBossLogMonsterDrop


class WorldBossRuneDropInline(RuneDropInline):
    model = models.WorldBossLogRuneDrop


@admin.register(models.WorldBossLog)
class WorldBossAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'grade')
    list_filter = ('grade',)
    search_fields = ('wizard_id', 'summoner__user__username')
    readonly_fields = ('summoner', 'level')
    inlines = (
        WorldBossItemDropInline,
        WorldBossMonsterDropInline,
        WorldBossRuneDropInline,
    )


# Reports
@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('generated_on',)


@admin.register(models.LevelReport)
class LevelReportAdmin(admin.ModelAdmin):
    readonly_fields = ('generated_on', 'level')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('level', 'level__dungeon')
