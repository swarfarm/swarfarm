from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles import views
from refreshtoken.views import delegate_jwt_token
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

from apiv2.views import generate_basic_auth_token
from bestiary.autocomplete import *
from data_log.autocomplete import SummonItemAutocomplete
from herders import views as herder_views
from herders.autocomplete import *
from herders.forms import CrispyAuthenticationForm, CrispyPasswordChangeForm, CrispyPasswordResetForm, \
    CrispySetPasswordForm

urlpatterns = [
    # AJAX-y stuff first
    url(r'^autocomplete/', include([
        url(r'^bestiary/$', BestiaryAutocomplete.as_view(), name='bestiary-monster-autocomplete'),
        url(r'^dungeon/$', DungeonAutocomplete.as_view(), name='bestiary-dungeon-autocomplete'),
        url(r'^item/$', DungeonAutocomplete.as_view(), name='bestiary-game-item-autocomplete'),
        url(r'#summon_item/$', SummonItemAutocomplete.as_view(), name='summon-game-item-autocomplete'),
        url(r'^quick-search/$', QuickSearchAutocomplete.as_view(), name='bestiary-quicksearch-autocomplete'),
        url(r'^monster-tag/$', MonsterTagAutocomplete.as_view(), name='monster-tag-autocomplete'),
        url(r'^monster-instance/$', MonsterInstanceAutocomplete.as_view(), name='monster-instance-autocomplete'),
    ])),
    url(r'^api/v2/', include('apiv2.urls', namespace='v2')),
    url(r'^api/', include('api.urls')),
    url(r'^api(/v\d+)?/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api(/v\d+)?/auth/generate-basic-token/', generate_basic_auth_token),
    url(r'^api(/v\d+)?/auth/get-token/', obtain_jwt_token),
    url(r'^api(/v\d+)?/auth/delegate-token', delegate_jwt_token),
    url(r'^api(/v\d+)?/auth/verify-token/', verify_jwt_token),

    # Bestiary
    url(r'^bestiary/', include('bestiary.urls', namespace='bestiary')),

    # SWARFARM app
    url(r'^feedback/', include('feedback.urls', namespace='feedback')),
    url(r'^data/', include('data_log.urls', namespace='data_log')),
    url(r'^', include('herders.urls', namespace='herders')),
    url(r'^', include('news.urls', namespace='news')),

    # Django auth/admin stuff
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(form_class=CrispyAuthenticationForm), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': 'news:latest_news'}, name='logout'),
    url(r'^password_change/$', auth_views.PasswordChangeView.as_view(
        form_class=CrispyPasswordChangeForm,
        success_url='password_change_done'
    ), name='password_change'),
    url(r'^password_change/password_change_done', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(form_class=CrispyPasswordResetForm), name='password_reset'),
    url(r'^password_reset/done$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(form_class=CrispySetPasswordForm),
        name='password_reset_confirm',
    ),
    url(
        r'^reset/done/$',
        auth_views.PasswordResetCompleteView.as_view(extra_context={'form': CrispyAuthenticationForm}),
        name='password_reset_complete'
    ),
    url(r'^username_change/$', herder_views.profile.change_username, name="username_change"),
    url(r'^username_change/done/$', herder_views.profile.change_username_complete, name="username_change_complete"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
