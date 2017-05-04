from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe


class Issue(models.Model):
    user = models.ForeignKey(User)
    submitted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, blank=True, null=True)
    subject = models.CharField(max_length=40)
    description = models.TextField(help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))
    public = models.BooleanField(default=True)
    closed = models.BooleanField(default=False)
    latest_comment = models.DateTimeField(default=timezone.now)
    github_issue_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('feedback:issue_detail', kwargs={'pk': self.pk})

    def comment_count(self):
        return Discussion.objects.filter(feedback=self).count()

    def get_status_html(self):
        if self.closed:
            if self.github_issue_url:
                return mark_safe('<a href="{}" target="_blank" class="label label-success"><span class="glyphicon glyphicon-check"></span> Implemented</a>'.format(
                    self.github_issue_url,
                ))
            else:
                return mark_safe('<span class="label label-default">Closed</span>')
        else:
            if self.github_issue_url:
                return mark_safe('<a href="{}" target="_blank" class="label label-info">Accepted - Tracked on <span class="fa fa-github"></span> GitHub</a>'.format(
                     self.github_issue_url,
                ))
            else:
                return mark_safe('<span class="label label-default">Under Discussion</span>')

    class Meta:
        ordering = ['-latest_comment']


class Discussion(models.Model):
    feedback = models.ForeignKey(Issue)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, blank=True, null=True)
    comment = models.TextField(help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))

    def __str__(self):
        return str(self.feedback) + ' ' + str(self.timestamp)

    def save(self, *args, **kwargs):
        super(Discussion, self).save(*args, **kwargs)

        # If this is the latest comment, send a pointer back to the main discussion article.
        if self.feedback and self.feedback.latest_comment < self.timestamp:
            self.feedback.latest_comment = self.timestamp
            self.feedback.save()

    class Meta:
        ordering = ('timestamp',)
