from django.contrib import admin

from .models import SummonLog


@admin.register(SummonLog)
class SummonLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'wizard_id', 'summoner', 'item', 'monster')
    readonly_fields = ('summoner', )
