from rest_framework import serializers

from news.models import *


class ArticleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Article
        fields = ('url', 'pk', 'title', 'body', 'created', 'sticky')
        extra_kwargs = {
            'url': {
                'view_name': 'apiv2:article-detail',
            },
        }
