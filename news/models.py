from django.db import models
from django.utils import timezone


class Article(models.Model):
    title = models.CharField(max_length=60)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    sticky = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-sticky', 'created')
