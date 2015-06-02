from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('herders.urls', namespace="herders")),
    url(r'^feedback/', include('django_basic_feedback.urls')),
]
