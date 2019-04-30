from django.urls import path, include
from . import views

app_name = 'bestiary'

urlpatterns = [
    path('', views.bestiary, name='home'),
    path('inventory/', views.bestiary_inventory, name='inventory'),
    path('dungeons/', include([
        path('', views.dungeons, name='dungeons'),
        path('<slug:slug>/<int:floor>/', views.dungeon_detail, name='dungeon_detail'),
        path('<slug:slug>/<str:difficulty>/<int:floor>/', views.dungeon_detail, name='dungeon_detail_difficulty'),
    ])),
    path('<slug:monster_slug>/', views.bestiary_detail, name='detail'),
]
