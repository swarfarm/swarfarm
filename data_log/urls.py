from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers

from . import views

app_name = 'log_data'

router = routers.SimpleRouter()
router.register(r'log/upload', views.LogData, basename='log-upload')
router.register(r'log/accepted_commands', views.AcceptedCommands, basename='log-accepted-commands')

urlpatterns = [
    url(r'^$', views.data_reports, name='data_reports'),
    url('magic_shop/', views.data_report_magic_shop_refresh, name='magic_shop_refresh'),
    url('magic_box/', include([
        path('', views.data_report_magic_box_crafting, name='magic_box_crafting'),
        path('<slug:slug>/', views.data_report_magic_box_crafting_detail, name='magic_box_crafting_detail'),
    ])),
    url('wish/', views.data_report_wish, name='wish'),
    url('summon/', include([
        path('', views.data_report_summon, name='summon'),
        path('<slug:slug>/', views.data_report_summon_detail, name='summon_detail'),
    ])),
    url('rune_crafting/', include([
        path('', views.data_report_rune_crafting, name='rune_crafting'),
        path('<slug:slug>/', views.data_report_rune_crafting_detail, name='rune_crafting_detail'),
    ])),
]

urlpatterns += router.urls
