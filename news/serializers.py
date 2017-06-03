from rest_framework import serializers

from news.models import *


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'url', 'title', 'body', 'created', 'sticky']
        extra_kwargs = {
            'url': {
                'view_name': 'article-detail',
            },
            'timestamp': {
                'help_text': 'ISO 8601 format date string',
            },
            'sticky': {
                'help_text': 'Will pin to top of results with default sorting',
            },
        }
