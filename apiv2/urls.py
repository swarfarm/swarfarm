from django.conf.urls import url, include
from rest_framework import routers
from apiv2 import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'news', views.ArticleViewSet)

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
]
