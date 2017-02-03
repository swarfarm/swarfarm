from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe


class Issue(models.Model):
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
    topic = models.IntegerField(choices=TOPIC_CHOICES)
    subject = models.CharField(max_length=40)
    description = models.TextField(help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))
    public = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    github_issue_url = models.URLField(null=True, blank=True)

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
    timestamp = models.DateTimeField(auto_now=True)
    comment = models.TextField(help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))

    def __unicode__(self):
        return str(self.feedback) + ' ' + str(self.timestamp)

    class Meta:
        ordering = ('timestamp',)
