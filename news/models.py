from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=60)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    display_until = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.title

