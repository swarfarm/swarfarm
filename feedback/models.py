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

    user = models.ForeignKey(User)
    submitted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, blank=True, null=True)
    subject = models.CharField(max_length=40)
    description = models.TextField(help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))
    public = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    github_issue_url = models.URLField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_UNREVIEWED)  # TODO delete once all issues have 'closed' set.

    def __unicode__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('feedback:issue_detail', kwargs={'pk': self.pk})

    def comment_count(self):
        return Discussion.objects.filter(feedback=self).count()

    def latest_comment(self):
        return Discussion.objects.filter(feedback=self).latest('timestamp')

    class Meta:
        ordering = ['submitted',]


class Discussion(models.Model):
    feedback = models.ForeignKey(Issue)
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, blank=True, null=True)
    comment = models.TextField(help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))

    def __unicode__(self):
        return str(self.feedback) + ' ' + str(self.timestamp)

    class Meta:
        ordering = ('timestamp',)
