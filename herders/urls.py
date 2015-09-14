from django.conf.urls import url, include

from . import views

urlpatterns = [
    # User management stuff
    url(r'^register/$', views.register, name='register'),  # Register new user
    url(r'^skill_debug/$', views.bestiary_sanity_checks, name='skill_checks'),


    # User profiles and monster views
    url(r'^profile/(?P<profile_name>[a-zA-Z0-9_@.]+)/', include([
        url(r'^$', views.profile, name='profile_default'),
        url(r'^edit/$', views.profile_edit, name='edit_profile'),
        url(r'^delete/$', views.profile_delete, name='profile_delete'),
        url(r'^storage/$', views.profile_storage, name='profile_storage'),
        url(r'^monster/', include([
            url(r'^add/$', views.monster_instance_add, name='monster_instance_add'),
            url(r'^quick_add/(?P<monster_id>[0-9]+)/(?P<stars>[0-9])/(?P<level>[0-9]+)/$', views.monster_instance_quick_add, name='monster_instance_quick_add'),
            url(r'^bulk_add/$', views.monster_instance_bulk_add, name='monster_instance_bulk_add'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_view, name='monster_instance_view'),
            url(r'^edit/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_edit, name='monster_instance_edit'),
            url(r'^delete/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_delete, name='monster_instance_delete'),
            url(r'^powerup/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_power_up, name='monster_instance_power_up'),
            url(r'^awaken/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_awaken, name='monster_instance_awaken'),
            url(r'^copy/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_duplicate, name='monster_instance_duplicate'),
        ])),
        url(r'^fusion/$', views.fusion_progress, name='fusion'),
        url(r'^teams/', include([
            url(r'^$', views.teams, name='teams'),
            url(r'^list/$', views.team_list),
            url(r'^add/$', views.team_edit, name='team_add'),
            url(r'^detail/(?P<team_id>[0-9a-f]{32})/$', views.team_detail, name='team_detail'),
            url(r'^edit/(?P<team_id>[0-9a-f]{32})/$', views.team_edit, name='team_edit'),
            url(r'^delete/(?P<team_id>[0-9a-f]{32})/$', views.team_delete, name='team_delete'),
            url(r'^group/', include([
                url(r'^add/$', views.team_group_add, name='team_group_add'),
                url(r'^delete/(?P<group_id>[0-9a-f]{32})/$', views.team_group_delete, name='team_group_delete'),
                url(r'^edit/(?P<group_id>[0-9a-f]{32})/$', views.team_group_edit, name='team_group_edit'),
            ])),
        ])),
        url(r'following/', include([
            url(r'^$', views.following, name='profile_following'),
            url(r'^add/(?P<follow_username>[a-zA-Z0-9_@.]+)/$', views.follow_add, name='profile_follow_add'),
            url(r'^remove/(?P<follow_username>[a-zA-Z0-9_@.]+)/$', views.follow_remove, name='profile_follow_remove'),
        ])),
        url(r'(?P<view_mode>[a-zA-Z]+)/(?P<sort_method>[a-zA-Z]+)/$', views.profile, name='profile_sorted'),
        url(r'(?P<view_mode>[a-zA-Z]+)/$', views.profile, name='profile'),
    ])),

    # Bestiary
    url(r'^bestiary/', include([
        url(r'^$', views.bestiary, name='bestiary'),
        url(r'^(?P<monster_id>[0-9]+)/$', views.bestiary_detail, name='bestiary_detail'),
    ])),
]
