from django.contrib import admin

from .models import *


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('subject', 'submitted', 'user', 'status', 'priority', 'public',)
    list_filter = ['status', 'priority', 'user']


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'feedback', 'user',)
