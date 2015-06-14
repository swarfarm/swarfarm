from django.conf.urls import url, include

from . import views

urlpatterns = [
    # Bestiary - get monster data
    url(r'bestiary/', include([
        url(r'^$', views.monster, name='monster'),
        url(r'^(?P<monster_id>[0-9]+)/$', views.monster, name='monster_individual'),
    ])),
]
