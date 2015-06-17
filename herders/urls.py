from django.conf.urls import url, include

from . import views

urlpatterns = [
    # User management stuff
    url(r'^register/$', views.register, name='register'),  # Register new user
    url(r'^login/$', views.log_in, name='login'),  # Log in user and redirect to profile
    url(r'^logout/$', views.log_out, name='logout'),  # Log in user and redirect to index


    # User profiles and monster views
    url(r'^profile/(?P<profile_name>[a-zA-Z0-9_@.]+)/', include([
        url(r'^$', views.profile),
        url(r'^edit/$', views.profile_edit, name='edit_profile'),
        url(r'^storage/$', views.profile_storage, name='profile_storage'),
        url(r'^monster/', include([
            url(r'^add/$', views.monster_instance_add, name='monster_instance_add'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_view, name='monster_instance_view'),
            url(r'^edit/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_edit, name='monster_instance_edit'),
            url(r'^delete/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_delete, name='monster_instance_delete'),
            url(r'^powerup/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_power_up, name='monster_instance_power_up'),
            url(r'^awaken/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_awaken, name='monster_instance_awaken'),
        ])),
        url(r'^fusion/$', views.fusion, name='fusion'),
        url(r'^teams/$', views.teams, name='teams'),
        url(r'^view/$', views.profile),  # Legacy URL scheme ended in /view. Now represented by /list)
        url(r'(?P<view_mode>[a-zA-Z]+)/(?P<sort_method>[a-zA-Z]+)/$', views.profile, name='profile_sorted'),
        url(r'(?P<view_mode>[a-zA-Z]+)/$', views.profile, name='profile'),
    ])),

    # Bestiary
    url(r'^bestiary/', include([
        url(r'^$', views.bestiary, name='bestiary'),
        url(r'^(?P<monster_element>[a-zA-Z]+)/$', views.bestiary, name='bestiary_element'),
        url(r'^(?P<monster_id>[0-9]+)/$', views.bestiary_detail, name='bestiary_detail'),
    ])),

    url(r'^fixdb/$', views.fixdb),
]
