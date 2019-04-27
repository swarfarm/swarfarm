from django.conf.urls import url, include
from . import views

app_name = 'bestiary'

urlpatterns = [
    url(r'^$', views.bestiary, name='home'),
    url(r'^inventory/$', views.bestiary_inventory, name='inventory'),
    url(r'^(?P<monster_slug>[\w-]+)/$', views.bestiary_detail, name='detail'),
]
