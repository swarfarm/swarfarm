from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe


class Issue(models.Model):
    STATUS_UNREVIEWED = 1
    STATUS_ACCEPTED = 2
    STATUS_IN_PROGRESS = 3
    STATUS_FEEDBACK = 4
    STATUS_RESOLVED = 5
    STATUS_REJECTED = 6
    STATUS_DUPLICATE = 7

    STATUS_CHOICES = (
        (STATUS_UNREVIEWED, 'Unreviewed'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_FEEDBACK, 'Requires Feedback'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_DUPLICATE, 'Duplicate'),
    )

    PRIORITY_NOW = 1
    PRIORITY_SOON = 2
    PRIORITY_SOMEDAY = 3

    PRIORITY_CHOICES = (
        (PRIORITY_NOW, 'Now'),
        (PRIORITY_SOON, 'Soon'),
        (PRIORITY_SOMEDAY, 'Someday'),
    )

    TOPIC_SITE_ERROR = 1
    TOPIC_IMPROVEMENT = 2
    TOPIC_INCORRECT_DATA = 3
    TOPIC_OTHER = 99

    TOPIC_CHOICES = (
        (TOPIC_SITE_ERROR, 'Errors or layout issues on website'),
        (TOPIC_IMPROVEMENT, 'Idea for new feature or improvement'),
        (TOPIC_INCORRECT_DATA, 'Incorrect monster data'),
        (TOPIC_OTHER, 'Other'),
    )

    user = models.ForeignKey(User)
    submitted = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_UNREVIEWED)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, null=True, blank=True)
    topic = models.IntegerField(choices=TOPIC_CHOICES)
    subject = models.CharField(max_length=40)
    description = models.TextField(help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))
    public = models.BooleanField(default=False)

    def __unicode__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('feedback:issue_detail', kwargs={'pk': self.pk})

    def comment_count(self):
        return Discussion.objects.filter(feedback=self).count()

    def closed(self):
        return self.status >= self.STATUS_RESOLVED

    def latest_comment(self):
        return Discussion.objects.filter(feedback=self).latest('timestamp')

    class Meta:
        ordering = ('status', 'priority', 'submitted')


class Discussion(models.Model):
    feedback = models.ForeignKey(Issue)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now=True)
    comment = models.TextField(help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))

    def __unicode__(self):
        return str(self.feedback) + ' ' + str(self.timestamp)

    class Meta:
        ordering = ('timestamp',)
