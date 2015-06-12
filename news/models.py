from django.db import models
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=60)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    display_until = models.DateTimeField(blank=True, null=True)\


    def is_active(self):
        if self.display_until is None:
            return True
        else:
            return self.display_until >= timezone.now()

    def __unicode__(self):
        return self.title
