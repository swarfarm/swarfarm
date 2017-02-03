from django.contrib import admin

from .models import *


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('topic', 'subject', 'submitted', 'user', 'public',)
    list_filter = ['subject', 'description']
    readonly_fields = ['user',]


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'feedback', 'user',)
