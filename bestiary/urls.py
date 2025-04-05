from django.urls import path, include

from . import views

app_name = 'bestiary'

urlpatterns = [
    path('', views.bestiary, name='home'),
    path('inventory/', views.bestiary_inventory, name='inventory'),
    path('<slug:monster_slug>/', views.bestiary_detail, name='detail'),
]
