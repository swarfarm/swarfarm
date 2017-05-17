from rest_framework import serializers

from news.models import *


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ('url', 'pk', 'title', 'body', 'created', 'sticky')
