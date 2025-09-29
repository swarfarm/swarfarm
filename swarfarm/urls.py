from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles import views
from bestiary.autocomplete import *

urlpatterns = [
    # AJAX-y stuff first
    url(r'^autocomplete/', include([
        url(r'^bestiary/$', BestiaryAutocomplete.as_view(), name='bestiary-monster-autocomplete'),
        url(r'^quick-search/$', QuickSearchAutocomplete.as_view(), name='bestiary-quicksearch-autocomplete'),
    ])),
    url(r'^api/v2/', include('apiv2.urls', namespace='v2')),
    url(r'^api/', include('api.urls')),
    url(r'^api(/v\d+)?/auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Bestiary
    url(r'^bestiary/', include('bestiary.urls', namespace='bestiary')),

    # SWARFARM app
    url(r'^', include('news.urls', namespace='news')),

    # Django auth/admin stuff
    url('admin/clearcache/', include('clearcache.urls')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
