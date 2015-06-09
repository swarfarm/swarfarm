from django.conf.urls import url

from . import views

urlpatterns = [
    # Main landing page
    url(r'^$', views.latest_news, name='latest_news'),
]
