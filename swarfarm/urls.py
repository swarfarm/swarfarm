from django.conf.urls import include, url
from django.views.generic.base import RedirectView
from django.templatetags.static import static
from django.contrib import admin

urlpatterns = [
    url(r'', include('herders.urls', namespace='herders')),
    url(r'', include('news.urls', namespace='news')),
    url(r'^feedback/', include('feedback.urls', namespace='feedback')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
]
