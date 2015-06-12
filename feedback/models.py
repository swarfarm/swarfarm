from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Feedback(models.Model):
    TOPIC_SITE_ERROR = 1
    TOPIC_IMPROVEMENT = 2
    TOPIC_INCORRECT_DATA = 3
    TOPIC_OTHER = 99

    TOPIC_CHOICES = (
        (TOPIC_SITE_ERROR, 'Errors or layout issues on website'),
        (TOPIC_IMPROVEMENT, 'Idea for new feature or improvement'),
        (TOPIC_INCORRECT_DATA, 'Incorrect monster data'),
        (TOPIC_OTHER, 'Other (Please be descriptive below'),
    )

    user = models.CharField(max_length=120)
    submitted = models.DateTimeField(auto_now=True)
    topic = models.IntegerField(choices=TOPIC_CHOICES)
    subject = models.CharField(max_length=40)
    feedback = models.TextField()

    def __unicode__(self):
        return self.subject