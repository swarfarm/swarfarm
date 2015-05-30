from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),  # Site root

    # User management stuff
    url(r'^register/', views.register, name='register'),  # Register new user
    url(r'^login/', views.log_in, name='login'),  # Log in user and redirect to profile
    url(r'^logout/', views.log_out, name='logout'),  # Log in user and redirect to index

    # Herders stuff
    url(r'^profile/$', views.profile, name='profile'),  # User profile - show owned library
    url(r'profile/box/', views.profile_box, name='profile_box'),  # View monster list similar to shown in game
    url(r'profile/box/(?P<sort_method>[a-zA-Z]+)', views.profile_box, name='profile_box_sorted'),  # View monster list similar to shown in game

    url(r'profile/storage', views.profile_storage, name='profile_storage'),  # View/edit essence storage

    url(r'^profile/add/$', views.add_monster_instance, name='add_monster_instance'),  # Add monster to profile
    url(r'^profile/monster/(?P<instance_id>[0-9a-f]{32})/edit/$',  # Edit existing monster instance
        views.edit_monster_instance,
        name='edit_monster_instance'
        ),
    url(r'^profile/monster/(?P<instance_id>[0-9a-f]{32})/delete/$',  # Delete monster instance
        views.delete_monster_instance,
        name='delete_monster_instance'
        ),
    url(r'^profile/monster/(?P<instance_id>[0-9a-f]{32})/powerup/$',  # Power up monster instance
        views.power_up_monster_instance,
        name='power_up_monster_instance'
        ),
    url(r'^profile/monster/(?P<instance_id>[0-9a-f]{32})/awaken/$',  # Awaken monster instance
        views.awaken_monster_instance,
        name='awaken_monster_instance'
        ),

    url(r'^bestiary/$', views.bestiary, name='bestiary'),  # Browse all monsters
    url(r'^bestiary/(?P<monster_element>[a-zA-Z]+)/$',
        views.bestiary,
        name='bestiary'
        ),  # Browse monsters of a specific type
    url(r'^bestiary/(?P<monster_id>[0-9]+)/$',
        views.bestiary_detail,
        name='bestiary_detail'
        ),  # View single monster detail

    url(r'^fusion/$', views.fusion, name='fusion'),  # Show fusion progress

    url(r'^teams/$', views.teams, name='teams')  # Create and view team setup for running certain dungeons
]