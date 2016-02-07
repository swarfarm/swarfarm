from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^skill_debug/$', views.bestiary_sanity_checks, name='skill_checks'),
    url(r'^$', views.bestiary, name='home'),
    url(r'^inventory/$', views.bestiary_inventory, name='inventory'),
    url(r'^(?P<monster_slug>[\w-]+)/$', views.bestiary_detail, name='detail'),
]
