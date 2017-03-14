from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^import/', include([
        url(r'^pcap/$', views.import_pcap, name='import_pcap'),
        url(r'^swparser/$', views.import_sw_json, name='import_swparser'),
        url(r'^progress/$', views.import_status, name='import_status_data'),
    ])),
    url(r'^export/', include([
        url(r'^optimizer/$', views.export_rune_optimizer, name='export_optimizer'),
        url(r'^optimizer/file/$', views.export_rune_optimizer, {'download_file': True}, name='export_optimizer_file'),
        url(r'^w10optimizer/$', views.export_win10_optimizer, name='export_win10_optimizer'),
    ])),
    url(r'^log/', include([
        url(r'^$', views.log_home, name='log_home'),
        url(r'^accepted_commands/', views.log_accepted_commands, name='log_accepted_commands'),
        url(r'^mine/$', views.log_mine_home, name='log_mine_home'),
        url(r'^mine/download/runs/', views.download_runs, name='log_mine_runs_download'),
        url(r'^mine/download/summons/', views.download_summons, name='log_mine_summons_download'),
        url(r'^summons/(?P<summon_slug>[\w-]+)/$', views.view_summon_log, name='view_summon_detail'),
        url(r'^summons/(?P<summon_slug>[\w-]+)/mine/$', views.view_summon_log, {'mine': True}, name='view_summon_detail_mine'),
        url(r'^scenarios/', include([
            url(r'^$', views.view_scenario_log_summary, name='view_scenario_summary'),
            url(r'^mine/$', views.view_scenario_log_summary, {'mine': True}, name='view_scenario_summary_mine'),
            url(r'^(?P<dungeon_slug>[\w-]+)/(?P<floor>[0-9]+)/$', views.view_dungeon_log, name='view_scenario_detail_floor'),
            url(r'^(?P<dungeon_slug>[\w-]+)/(?P<floor>[0-9]+)/mine/$', views.view_dungeon_log, {'mine': True}, name='view_scenario_detail_floor_mine'),
            url(r'^(?P<dungeon_slug>[\w-]+)/(?P<floor>[0-9]+)/(?P<difficulty>[0-9]+)/$', views.view_dungeon_log, name='view_scenario_detail_floor_difficulty'),
            url(r'^(?P<dungeon_slug>[\w-]+)/(?P<floor>[0-9]+)/(?P<difficulty>[0-9]+)/mine/$', views.view_dungeon_log, {'mine': True}, name='view_scenario_detail_floor_difficulty_mine'),
        ])),
        url(r'^dungeons/', include([
            url(r'^(?P<dungeon_slug>[\w-]+)/$', views.view_dungeon_log, name='view_dungeon_detail'),
            url(r'^(?P<dungeon_slug>[\w-]+)/mine/$', views.view_dungeon_log, {'mine': True}, name='view_dungeon_detail_mine'),
            url(r'^(?P<dungeon_slug>[\w-]+)/(?P<floor>[0-9]+)/$', views.view_dungeon_log, name='view_dungeon_detail_floor'),
            url(r'^(?P<dungeon_slug>[\w-]+)/(?P<floor>[0-9]+)/mine/$', views.view_dungeon_log, {'mine': True}, name='view_dungeon_detail_floor_mine'),
            url(r'^(?P<dungeon_slug>[\w-]+)/(?P<floor>[0-9]+)/(?P<difficulty>[0-9]+)/$', views.view_dungeon_log, name='view_dungeon_detail_floor_difficulty'),
            url(r'^(?P<dungeon_slug>[\w-]+)/(?P<floor>[0-9]+)/(?P<difficulty>[0-9]+)/mine/$', views.view_dungeon_log, {'mine': True}, name='view_dungeon_detail_floor_difficulty_mine'),
        ])),
        url(r'^rifts/', include([
            url(r'(?P<rift_slug>[\w-]+)/mine/$', views.view_elemental_rift_log, {'mine': True}, name='view_elemental_rift_mine'),
            url(r'(?P<rift_slug>[\w-]+)/$', views.view_elemental_rift_log, name='view_elemental_rift'),
        ])),
        url(r'^rune-crafting/', include([
            url('^$', views.view_rune_craft_log, name='view_rune_craft_log'),
            url('^mine/$', views.view_rune_craft_log, {'mine': True}, name='view_rune_craft_log_mine'),
        ])),
        url(r'^magic-shop/', include([
            url('^$', views.view_magic_shop_log, name='view_magic_shop_log'),
            url('^mine/$', views.view_magic_shop_log, {'mine': True}, name='view_magic_shop_log_mine'),
        ])),
        url(r'^world-boss/', include([
            url('^$', views.view_world_boss_log, name='view_world_boss_log'),
            url('^mine/$', views.view_world_boss_log, {'mine': True}, name='view_world_boss_log_mine'),
        ])),
        url(r'^wishes/', include([
            url('^$', views.view_wish_log, name='view_wish_log'),
            url('^mine/$', views.view_wish_log, {'mine': True}, name='view_wish_log_mine'),
        ])),
        url(r'^charts/', include([
            url(r'^contrib/$', views.log_contribution_chart_data, name='contribution_chart_data'),
            url(r'^contrib/mine/$', views.log_contribution_chart_data, {'mine': True}, name='contribution_chart_data_mine'),
            url(r'^rune/$', views.dungeon_rune_chart_data, name='dungeon_rune_chart_data'),
            url(r'^rune/mine/$', views.dungeon_rune_chart_data, {'mine': True}, name='dungeon_rune_chart_data_mine'),
            url(r'^dungeon/$', views.dungeon_stats_chart_data, name='dungeon_stats_chart_data'),
            url(r'^dungeon/mine/$', views.dungeon_stats_chart_data, {'mine': True}, name='dungeon_stats_chart_data_mine'),
            url(r'^summon/$', views.summon_stats_chart_data, name='summon_stats_chart_data'),
            url(r'^summon/mine/$', views.summon_stats_chart_data, {'mine': True}, name='summon_stats_chart_data_mine'),
            url(r'^rune-crafting/$', views.rune_craft_chart_data, name='rune_craft_chart_data'),
            url(r'^rune-crafting/mine/$', views.rune_craft_chart_data, {'mine': True}, name='rune_craft_chart_data_mine'),
            url(r'^magic-shop/$', views.magic_shop_chart_data, name='magic_shop_chart_data'),
            url(r'^magic-shop/mine/$', views.magic_shop_chart_data, name='magic_shop_chart_data_mine'),
        ])),
        url(r'^timespan/', include([
            url(r'^(?P<days>[0-9]+)/$', views.log_timespan, name='log_timespan_days'),
            url(r'^(?P<name>[a-zA-Z0-9.\-_]+)/$', views.log_timespan, name='log_timespan_named'),
            url(r'^$', views.log_timespan, name='log_timespan_custom'),
        ])),
        url(r'^upload/$', views.log_data, name='upload_log'),
    ]))
]
