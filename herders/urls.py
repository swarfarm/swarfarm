from django.conf.urls import url, include
from django.urls import path, re_path

from . import views

app_name = 'herders'

urlpatterns = [
    # User management stuff
    url(r'^register/$', views.profile.register, name='register'),  # Register new user

    # User profiles and monster views
    url(r'^profile/(?P<profile_name>[a-zA-Z0-9_@.]+)/', include([
        url(r'^$', views.monsters.monsters, name='profile_default'),
        url(r'^edit/$', views.profile.profile_edit, name='edit_profile'),
        url(r'^delete/$', views.profile.profile_delete, name='profile_delete'),
        url(r'^storage/', include([
            url(r'^$', views.profile.storage, name='storage'),
            url(r'^update/$', views.profile.storage_update, name='storage_update'),
        ])),
        url(r'^buildings/$', views.profile.buildings, name='profile_buildings'),
        url(r'^monster/', include([
            url(r'^inventory/$', views.monsters.monster_inventory, name='monster_inventory'),
            url(r'^inventory/(?P<view_mode>(list|box|pieces|collection))/$', views.monsters.monster_inventory, name='monster_inventory_view_mode'),
            url(r'^inventory/(?P<view_mode>(list|box|pieces|collection))/(?P<box_grouping>[a-zA-Z_]+)/$', views.monsters.monster_inventory, name='monster_inventory_view_mode_sorted'),
            url(r'^add/$', views.monsters.monster_instance_add, name='monster_instance_add'),
            url(r'^quick_add/(?P<monster_id>[0-9]+)/(?P<stars>[0-9])/(?P<level>[0-9]+)/$', views.monsters.monster_instance_quick_add, name='monster_instance_quick_add'),
            url(r'^quick_fodder/$', views.monsters.quick_fodder_menu, name='quick_fodder_menu'),
            url(r'^bulk_add/$', views.monsters.monster_instance_bulk_add, name='monster_instance_bulk_add'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_instance_view, name='monster_instance_view'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/runes/$', views.monsters.monster_instance_view_runes, name='monster_instance_view_runes'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/stats/$', views.monsters.monster_instance_view_stats, name='monster_instance_view_stats'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/skills/$', views.monsters.monster_instance_view_skills, name='monster_instance_view_skills'),
            url(r'^view/(?P<instance_id>[0-9a-f]{32})/info/$', views.monsters.monster_instance_view_info, name='monster_instance_view_info'),
            url(r'^edit/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_instance_edit, name='monster_instance_edit'),
            url(r'^delete/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_instance_delete, name='monster_instance_delete'),
            url(r'^powerup/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_instance_power_up, name='monster_instance_power_up'),
            url(r'^awaken/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_instance_awaken, name='monster_instance_awaken'),
            url(r'^remove_runes/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_instance_remove_runes, name='monster_instance_remove_runes'),
            url(r'^copy/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_instance_duplicate, name='monster_instance_duplicate'),
            url(r'^piece/', include([
                url(r'^add/$', views.monsters.monster_piece_add, name='monster_piece_add'),
                url(r'^edit/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_piece_edit, name='monster_piece_edit'),
                url(r'^summon/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_piece_summon, name='monster_piece_summon'),
                url(r'^delete/(?P<instance_id>[0-9a-f]{32})/$', views.monsters.monster_piece_delete, name='monster_piece_delete'),
            ]))
        ])),
        url(r'^fusion/$', views.fusion.fusion_progress, name='fusion'),
        url(r'^fusion/(?P<monster_slug>[\w-]+)/$$', views.fusion.fusion_progress_detail, name='fusion'),
        url(r'^teams/', include([
            url(r'^$', views.teams.teams, name='teams'),
            url(r'^list/$', views.teams.team_list),
            url(r'^add/$', views.teams.team_edit, name='team_add'),
            url(r'^detail/(?P<team_id>[0-9a-f]{32})/$', views.teams.team_detail, name='team_detail'),
            url(r'^edit/(?P<team_id>[0-9a-f]{32})/$', views.teams.team_edit, name='team_edit'),
            url(r'^delete/(?P<team_id>[0-9a-f]{32})/$', views.teams.team_delete, name='team_delete'),
            url(r'^group/', include([
                url(r'^add/$', views.teams.team_group_add, name='team_group_add'),
                url(r'^delete/(?P<group_id>[0-9a-f]{32})/$', views.teams.team_group_delete, name='team_group_delete'),
                url(r'^edit/(?P<group_id>[0-9a-f]{32})/$', views.teams.team_group_edit, name='team_group_edit'),
            ])),
        ])),
        url(r'^runes/', include([
            url(r'^$', views.runes.runes, name='runes'),
            url(r'^add/$', views.runes.rune_add, name='rune_add'),
            url(r'^edit/(?P<rune_id>[0-9a-f]{32})/$', views.runes.rune_edit, name='rune_edit'),
            url(r'^delete/all/$', views.runes.rune_delete_all, name='rune_delete_all'),
            url(r'^delete/(?P<rune_id>[0-9a-f]{32})/$', views.runes.rune_delete, name='rune_delete'),
            url(r'^unassign/(?P<rune_id>[0-9a-f]{32})/$', views.runes.rune_unassign, name='rune_unassign'),
            url(r'^unassign/all/$', views.runes.rune_unassign_all, name='rune_unassign_all'),
            url(r'^delete-notes/$', views.runes.rune_delete_notes_all, name='rune_delete_notes_all'),
            url(r'^resave/all/$', views.runes.rune_resave_all, name='rune_resave_all'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/$', views.runes.rune_assign, name='rune_assign'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/(?P<slot>[0-9])/$', views.runes.rune_assign, name='rune_assign_with_slot'),
            url(r'^assign/(?P<instance_id>[0-9a-f]{32})/(?P<rune_id>[0-9a-f]{32})/$', views.runes.rune_assign_choice, name='rune_assign_choice'),
            url(r'^inventory/$', views.runes.rune_inventory, name='rune_inventory'),
            url(r'^inventory/(?P<view_mode>(list|box|grid|crafts))/$', views.runes.rune_inventory, name='rune_inventory_view_mode'),
            url(r'^inventory/(?P<view_mode>(list|box|grid))/(?P<box_grouping>[a-zA-Z]+)/$', views.runes.rune_inventory, name='rune_inventory_view_mode_sorted'),
            url(r'^craft/', include([
                url(r'^add/$', views.runes.rune_craft_add, name='rune_craft_add'),
                url(r'^edit/(?P<craft_id>[0-9a-f]{32})/$', views.runes.rune_craft_edit, name='rune_craft_edit'),
                url(r'^delete/(?P<craft_id>[0-9a-f]{32})/$', views.runes.rune_craft_delete, name='rune_craft_delete'),
            ])),
        ])),
        path('artifacts/', include([
            path('', views.artifacts.artifacts, name='artifacts'),
            path('inventory/', views.artifacts.inventory, name='artifact_inventory'),
            path('inventory/box/<str:box_grouping>/', views.artifacts.inventory, name='artifact_inventory_view_mode_sorted'),
            path('add/', views.artifacts.add, name='artifact_add'),
            re_path(r'^edit/(?P<artifact_id>[0-9a-f]{32})/$', views.artifacts.edit, name='artifact_edit'),
            re_path(r'^delete/(?P<artifact_id>[0-9a-f]{32})/$', views.artifacts.delete, name='artifact_delete'),
            re_path(r'^assign/(?P<instance_id>[0-9a-f]{32})/$', views.artifacts.assign, name='artifact_assign'),
            re_path(r'^assign/(?P<instance_id>[0-9a-f]{32})/(?P<artifact_id>[0-9a-f]{32})/$', views.artifacts.assign_choice, name='artifact_assign_choice'),
            re_path(r'^assign/(?P<instance_id>[0-9a-f]{32})/(?P<slot>[a-z]*)/', views.artifacts.assign, name='artifact_assign_with_slot'),
            re_path(r'^unassign/(?P<artifact_id>[0-9a-f]{32})/$', views.artifacts.unassign, name='artifact_unassign'),
        ])),
        url(r'^buildings/', include([
            url(r'^$', views.profile.buildings, name='buildings'),
            url(r'^inventory/$', views.profile.buildings_inventory, name='buildings_inventory'),
            url(r'^edit/(?P<building_id>[0-9]+)/$', views.profile.building_edit, name='building_edit'),
        ])),
        url(r'following/', include([
            url(r'^$', views.profile.following, name='profile_following'),
            url(r'^add/(?P<follow_username>[a-zA-Z0-9_@.]+)/$', views.profile.follow_add, name='profile_follow_add'),
            url(r'^remove/(?P<follow_username>[a-zA-Z0-9_@.]+)/$', views.profile.follow_remove, name='profile_follow_remove'),
        ])),
        url(r'compare/(?P<follow_username>[a-zA-Z0-9_@.]+)/', include([
            url(r'^$', views.compare.summary, name='profile_compare'),
            url(r'^runes/$', views.compare.runes, name='profile_compare_runes'),
            url(r'^rune_crafts/(?P<rune_craft_slug>[\w-]+)$', views.compare.rune_crafts, name='profile_compare_rune_crafts'),
            url(r'^artifacts/$', views.compare.artifacts, name='profile_compare_artifacts'),
            url(r'^artifact_crafts/$', views.compare.artifact_crafts, name='profile_compare_artifact_crafts'),
            url(r'^monsters/$', views.compare.monsters, name='profile_compare_monsters'),
            url(r'^buildings/$', views.compare.buildings, name='profile_compare_buildings'),
            url(r'^builds/$', views.compare.builds, name='profile_compare_builds'),
        ])),
        url(r'^data/$', views.profile.import_export_home, name='import_export_home'),
        url(r'^import/', include([
            url(r'^swjson/$', views.profile.import_sw_json, name='import_swparser'),
            url(r'^progress/$', views.profile.import_status, name='import_status_data'),
        ])),
        url(r'^export/', include([
            url(r'^swop_optimizer/$', views.profile.export_win10_optimizer, name='export_win10_optimizer'),
        ])),
        url(r'^data_logs/', include([
            url(r'^$', views.data_log.Dashboard.as_view(), name='data_log_dashboard'),
            url(r'^detach/$', views.data_log.detach_data_logs, name='data_log_detach'),
            url(r'^help/$', views.data_log.Help.as_view(), name='data_log_help'),
            url(r'^magic_shop/', include([
                path('', views.data_log.MagicShopDashboard.as_view(), name='data_log_magic_shop_dashboard'),
                path('table/', views.data_log.MagicShopTable.as_view(), name='data_log_magic_shop_table'),
            ])),
            url(r'^wish/', include([
                path('', views.data_log.WishDashboard.as_view(), name='data_log_wish_dashboard'),
                path('table/', views.data_log.WishTable.as_view(), name='data_log_wish_table'),
            ])),
            url(r'^rune_crafting/', include([
                path('', views.data_log.RuneCraftDashboard.as_view(), name='data_log_rune_craft_dashboard'),
                path('table/', views.data_log.RuneCraftTable.as_view(), name='data_log_rune_craft_table'),
            ])),
            url(r'^magic_box/', include([
                path('', views.data_log.MagicBoxCraftDashboard.as_view(), name='data_log_magic_box_craft_dashboard'),
                path('table/', views.data_log.MagicBoxCraftTable.as_view(), name='data_log_magic_box_craft_table'),
            ])),
            url(r'^summons/', include([
                path('', views.data_log.SummonsDashboard.as_view(), name='data_log_summons_dashboard'),
                path('table/', views.data_log.SummonsTable.as_view(), name='data_log_summons_table'),
                path('<slug:slug>/', views.data_log.SummonsDetail.as_view(), name='data_log_summons_detail'),
            ])),
            url(r'^dungeons/', include([
                path('', views.data_log.DungeonDashboard.as_view(), name='data_log_dungeon_dashboard'),
                path('table/', views.data_log.DungeonTable.as_view(), name='data_log_dungeon_table'),
                path('<slug:slug>/', views.data_log.DungeonDetail.as_view(), name='data_log_dungeon_detail_no_floor'),
                path('<slug:slug>/b<int:floor>/', views.data_log.DungeonDetail.as_view(), name='data_log_dungeon_detail'),
                path('<slug:slug>/<str:difficulty>/b<int:floor>/', views.data_log.DungeonDetail.as_view(), name='data_log_dungeon_detail_difficulty'),
            ])),
            url(r'^rift_beast/', include([
                path('', views.data_log.ElementalRiftDungeonDashboard.as_view(), name='data_log_rift_dungeon_dashboard'),
                path('table/', views.data_log.ElementalRiftBeastTable.as_view(), name='data_log_rift_dungeon_table'),
                path('<slug:slug>/', views.data_log.ElementalRiftDungeonDetail.as_view(), name='data_log_rift_dungeon_detail'),
            ])),
            url(r'^rift_raid/', include([
                path('', views.data_log.RiftRaidDashboard.as_view(), name='data_log_rift_raid_dashboard'),
                path('table/', views.data_log.RiftRaidTable.as_view(), name='data_log_rift_raid_table'),
                path('r<int:floor>/', views.data_log.RiftRaidDetail.as_view(), name='data_log_rift_raid_detail'),
            ])),
            url(r'^world_boss/', include([
                path('', views.data_log.WorldBossDashboard.as_view(), name='data_log_world_boss_dashboard'),
                path('table/', views.data_log.WorldBossTable.as_view(), name='data_log_world_boss_table'),
            ])),
        ])),
        url(r'stats/(?P<follow_username>[a-zA-Z0-9_@.]+)/', include([
            url(r'^$', views.profile.stats, name='profile_stats'),
            url(r'^runes/$', views.profile.stats_runes, name='profile_stats_runes'),
            url(r'^rune_crafts/(?P<rune_craft_slug>[\w-]+)$', views.profile.stats_rune_crafts, name='profile_stats_rune_crafts'),
            url(r'^artifacts/$', views.profile.stats_artifacts, name='profile_stats_artifacts'),
            url(r'^artifact_crafts/$', views.profile.stats_artifact_crafts, name='profilestats_artifact_crafts'),
            url(r'^monsters/$', views.profile.stats_monsters, name='profile_stats_monsters'),
        ])),
    ])),
]
