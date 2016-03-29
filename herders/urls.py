from django.conf.urls import url, include

from . import views

urlpatterns = [
    # User management stuff
    url(r'^register/$', views.register, name='register'),  # Register new user

    # User profiles and monster views
    url(r'^profile/(?P<profile_name>[a-zA-Z0-9_@.]+)/', include([
        url(r'^$', views.profile, name='profile_default'),
        url(r'^edit/$', views.profile_edit, name='edit_profile'),
        url(r'^delete/$', views.profile_delete, name='profile_delete'),
        url(r'^storage/$', views.profile_storage, name='profile_storage'),
        url(r'^monster/', include([
            url(r'^inventory/$', views.monster_inventory, name='monster_inventory'),
            url(r'^inventory/(?i)(?P<view_mode>(list|box|pieces))/$', views.monster_inventory, name='monster_inventory_view_mode'),
            url(r'^inventory/(?i)(?P<view_mode>(list|box|pieces))/(?i)(?P<box_grouping>[a-zA-Z]+)/$', views.monster_inventory, name='monster_inventory_view_mode_sorted'),
            url(r'^add/$', views.monster_instance_add, name='monster_instance_add'),
            url(r'^quick_add/(?P<monster_id>[0-9]+)/(?P<stars>[0-9])/(?P<level>[0-9]+)/$', views.monster_instance_quick_add, name='monster_instance_quick_add'),
            url(r'^bulk_add/$', views.monster_instance_bulk_add, name='monster_instance_bulk_add'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_view, name='monster_instance_view'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/sidebar/$', views.monster_instance_view_sidebar, name='monster_instance_view_sidebar'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/runes/$', views.monster_instance_view_runes, name='monster_instance_view_runes'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/stats/$', views.monster_instance_view_stats, name='monster_instance_view_stats'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/skills/$', views.monster_instance_view_skills, name='monster_instance_view_skills'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/info/$', views.monster_instance_view_info, name='monster_instance_view_info'),
            url(r'^edit/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_edit, name='monster_instance_edit'),
            url(r'^delete/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_delete, name='monster_instance_delete'),
            url(r'^powerup/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_power_up, name='monster_instance_power_up'),
            url(r'^awaken/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_awaken, name='monster_instance_awaken'),
            url(r'^remove_runes/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_remove_runes, name='monster_instance_remove_runes'),
            url(r'^copy/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_duplicate, name='monster_instance_duplicate'),
            url(r'^piece/', include([
                url(r'^add/$', views.monster_piece_add, name='monster_piece_add'),
                url(r'^edit/(?P<instance_id>[0-9a-f]{32})/$', views.monster_piece_edit, name='monster_piece_edit'),
                url(r'^summon/(?P<instance_id>[0-9a-f]{32})/$', views.monster_piece_summon, name='monster_piece_summon'),
                url(r'^delete/(?P<instance_id>[0-9a-f]{32})/$', views.monster_piece_delete, name='monster_piece_delete'),
            ]))
        ])),
        url(r'^fusion/$', views.fusion_progress, name='fusion'),
        url(r'^fusion/(?P<monster_slug>[\w-]+)/$$', views.fusion_progress_detail, name='fusion'),
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
        url(r'^runes/', include([
            url(r'^$', views.runes, name='runes'),
            url(r'^add/$', views.rune_add, name='rune_add'),
            url(r'^edit/(?P<rune_id>[0-9a-f]{32})/$', views.rune_edit, name='rune_edit'),
            url(r'^delete/all/$', views.rune_delete_all, name='rune_delete_all'),
            url(r'^delete/(?P<rune_id>[0-9a-f]{32})/$', views.rune_delete, name='rune_delete'),
            url(r'^unassign/(?P<rune_id>[0-9a-f]{32})/$', views.rune_unassign, name='rune_unassign'),
            url(r'^unassign/all/$', views.rune_unassign_all, name='rune_unassign_all'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/$', views.rune_assign, name='rune_assign'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/(?P<slot>[0-9])/$', views.rune_assign, name='rune_assign_with_slot'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/(?P<rune_id>[0-9a-f]{32})/$', views.rune_assign_choice, name='rune_assign_choice'),
            url(r'^inventory/$', views.rune_inventory, name='rune_inventory'),
            url(r'^inventory/(?P<view_mode>(list|box|grid))/$', views.rune_inventory, name='rune_inventory_view_mode'),
            url(r'^inventory/(?i)(?P<view_mode>(list|box|grid))/(?i)(?P<box_grouping>[a-zA-Z]+)/$', views.rune_inventory, name='rune_inventory_view_mode_sorted'),
            url(r'^inventory/counts/$', views.rune_counts, name='rune_inventory_counts'),
        ])),
        url(r'following/', include([
            url(r'^$', views.following, name='profile_following'),
            url(r'^add/(?P<follow_username>[a-zA-Z0-9_@.]+)/$', views.follow_add, name='profile_follow_add'),
            url(r'^remove/(?P<follow_username>[a-zA-Z0-9_@.]+)/$', views.follow_remove, name='profile_follow_remove'),
        ])),
    ])),
]
