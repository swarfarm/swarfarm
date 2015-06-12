from django.conf.urls import url, include

from . import views

urlpatterns = [
    # User management stuff
    url(r'^$', views.index, name='index'),  # Register new user
    url(r'^thanks/$', views.thanks, name='thanks'),  # Log in user and redirect to profile
]
