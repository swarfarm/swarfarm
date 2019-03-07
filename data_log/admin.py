from django.contrib import admin

from .models import SummonLog, DungeonLog


@admin.register(SummonLog)
class SummonLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'item', 'monster')
    readonly_fields = ('summoner', )


@admin.register(DungeonLog)
class DungeonLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'level', 'success', 'clear_time')
    readonly_fields = ('summoner', )
