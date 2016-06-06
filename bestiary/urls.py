from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^skill_debug/$', views.bestiary_sanity_checks, name='skill_checks'),
    url(r'^$', views.bestiary, name='home'),
    url(r'^inventory/$', views.bestiary_inventory, name='inventory'),
    url(r'^(?P<monster_slug>[\w-]+)/$', views.bestiary_detail, name='detail'),
    url(r'^edit/', include([
        url(r'skill/(?P<pk>[0-9]+)/$', views.edit_skill, name='edit_skill'),
        url(r'monster/(?P<pk>[0-9]+)/$', views.edit_monster, name='edit_monster'),
    ])),
]
