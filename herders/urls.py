from django.conf.urls import url, include

from . import views

app_name = 'herders'

urlpatterns = [
    # User management stuff
    url(r'^register/$', views.register, name='register'),  # Register new user

    # User profiles and monster views
    url(r'^profile/(?P<profile_name>[a-zA-Z0-9_@.]+)/', include([
        url(r'^$', views.profile, name='profile_default'),
        url(r'^edit/$', views.profile_edit, name='edit_profile'),
        url(r'^delete/$', views.profile_delete, name='profile_delete'),
        url(r'^storage/', include([
            url(r'^$', views.storage, name='storage'),
            url(r'^update/$', views.storage_update, name='storage_update'),
        ])),
        url(r'^buildings/$', views.buildings, name='profile_buildings'),
        url(r'^monster/', include([
            url(r'^inventory/$', views.monster_inventory, name='monster_inventory'),
            url(r'^inventory/(?P<view_mode>(list|box|pieces))/$', views.monster_inventory, name='monster_inventory_view_mode'),
            url(r'^inventory/(?P<view_mode>(list|box|pieces))/(?P<box_grouping>[a-zA-Z_]+)/$', views.monster_inventory, name='monster_inventory_view_mode_sorted'),
            url(r'^add/$', views.monster_instance_add, name='monster_instance_add'),
            url(r'^quick_add/(?P<monster_id>[0-9]+)/(?P<stars>[0-9])/(?P<level>[0-9]+)/$', views.monster_instance_quick_add, name='monster_instance_quick_add'),
            url(r'^quick_fodder/$', views.quick_fodder_menu, name='quick_fodder_menu'),
            url(r'^bulk_add/$', views.monster_instance_bulk_add, name='monster_instance_bulk_add'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/$', views.monster_instance_view, name='monster_instance_view'),
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
            url(r'^resave/all/$', views.rune_resave_all, name='rune_resave_all'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/$', views.rune_assign, name='rune_assign'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/(?P<slot>[0-9])/$', views.rune_assign, name='rune_assign_with_slot'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/(?P<rune_id>[0-9a-f]{32})/$', views.rune_assign_choice, name='rune_assign_choice'),
            url(r'^inventory/$', views.rune_inventory, name='rune_inventory'),
            url(r'^inventory/(?P<view_mode>(list|box|grid|crafts))/$', views.rune_inventory, name='rune_inventory_view_mode'),
            url(r'^inventory/(?P<view_mode>(list|box|grid))/(?P<box_grouping>[a-zA-Z]+)/$', views.rune_inventory, name='rune_inventory_view_mode_sorted'),
            url(r'^craft/', include([
                url(r'^add/$', views.rune_craft_add, name='rune_craft_add'),
                url(r'^edit/(?P<craft_id>[0-9a-f]{32})/$', views.rune_craft_edit, name='rune_craft_edit'),
                url(r'^delete/(?P<craft_id>[0-9a-f]{32})/$', views.rune_craft_delete, name='rune_craft_delete'),
            ])),
        ])),
        url(r'^buildings/', include([
            url(r'^$', views.buildings, name='buildings'),
            url(r'^inventory/$', views.buildings_inventory, name='buildings_inventory'),
            url(r'^edit/(?P<building_id>[0-9]+)/$', views.building_edit, name='building_edit'),
        ])),
        url(r'following/', include([
            url(r'^$', views.following, name='profile_following'),
            url(r'^add/(?P<follow_username>[a-zA-Z0-9_@.]+)/$', views.follow_add, name='profile_follow_add'),
            url(r'^remove/(?P<follow_username>[a-zA-Z0-9_@.]+)/$', views.follow_remove, name='profile_follow_remove'),
        ])),
        url(r'^data/$', views.import_export_home, name='import_export_home'),
        url(r'^import/', include([
            url(r'^pcap/$', views.import_pcap, name='import_pcap'),
            url(r'^swjson/$', views.import_sw_json, name='import_swparser'),
            url(r'^progress/$', views.import_status, name='import_status_data'),
        ])),
        url(r'^export/', include([
            url(r'^swop_optimizer/$', views.export_win10_optimizer, name='export_win10_optimizer'),
        ])),
        url(r'^data_logs/', include([
            url(r'^$', views.data_log_dashboard, name='data_log_dashboard'),
            url(r'^magic_shop/$', views.data_log_magic_shop, name='data_log_magic_shop'),
            url(r'^wish/$', views.data_log_wish, name='data_log_wish'),
            url(r'^rune_crafting/$', views.data_log_rune_crafting, name='data_log_rune_crafting'),
            url(r'^magic_box/$', views.data_log_magic_box, name='data_log_magic_box'),
            url(r'^summons/$', views.data_log_summons, name='data_log_summons'),
            url(r'^dungeons/$', views.data_log_dungeons, name='data_log_dungeons'),
            url(r'^rift_beast/$', views.data_log_rift_beast, name='data_log_rift_beast'),
            url(r'^rift_raid/$', views.data_log_rift_raid, name='data_log_rift_raid'),
            url(r'^world_boss/$', views.data_log_world_boss, name='data_log_world_boss'),
        ]))
    ])),
]
