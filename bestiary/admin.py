from django.contrib import admin
from .models import *


@admin.register(PatchNotes)
class PatchNoteAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'timestamp',]