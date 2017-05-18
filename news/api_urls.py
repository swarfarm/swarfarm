from rest_framework import routers

from news.api_views import *

router = routers.DefaultRouter()
router.register(r'news', ArticleViewSet)
