from django.contrib import admin
from django.db.models import Q
from .models import *


class IssueStatusListFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('unreviewed', 'Unreviewed'),
            ('accepted', 'Accepted'),
            ('implemented', 'Implemented'),
            ('closed', 'Closed'),
        ]

    def queryset(self, request, queryset):

        blank_github_issue_url = Q(github_issue_url__isnull=True) | Q(github_issue_url='')

        if self.value() == 'unreviewed':
            return queryset.filter(closed=False).filter(blank_github_issue_url)
        elif self.value() == 'accepted':
            return queryset.filter(closed=False).exclude(blank_github_issue_url)
        elif self.value() == 'implemented':
            return queryset.filter(closed=True).exclude(blank_github_issue_url)
        elif self.value() == 'closed':
            return queryset.filter(closed=True).filter(blank_github_issue_url)
        else:
            return queryset


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('subject', 'submitted', 'user', 'public',)
    list_filter = ['subject', 'description', IssueStatusListFilter,]
    ordering = ['-submitted',]
    readonly_fields = ['user',]


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'feedback', 'user',]
    ordering = ['-timestamp',]
