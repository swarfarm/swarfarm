from django.contrib import admin
from .models import Dungeon, Level


@admin.register(Dungeon)
class DungeonAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'type', 'max_floors']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['dungeon', 'floor', 'difficulty']
