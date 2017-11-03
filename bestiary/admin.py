from django.contrib import admin
from .models import *


@admin.register(Dungeon)
class DungeonAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'type', 'max_floors']


@admin.register(PatchNotes)
class PatchNoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'timestamp',]
