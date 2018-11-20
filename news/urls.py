from django.conf.urls import url

from . import views

app_name = 'news'

urlpatterns = [
    # Main landing page
    url(r'^$', views.latest_news, name='latest_news'),
]
