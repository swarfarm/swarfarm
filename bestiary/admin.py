from django.contrib import admin

from .models import Dungeon, Level, MonsterGuide


@admin.register(Dungeon)
class DungeonAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'type', 'max_floors']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['dungeon', 'floor', 'difficulty']


@admin.register(MonsterGuide)
class MonsterGuideAdmin(admin.ModelAdmin):
    list_display = ['monster', 'last_updated', 'edited_by']

    def save_model(self, request, obj, form, change):
        obj.edited_by = request.user
        super().save_model(request, obj, form, change)
