from django.conf.urls import url, include

from . import views

urlpatterns = [
    # User management stuff
    url(r'^$', views.IssueList.as_view(), name='index'),
    url(r'^add/$', views.IssueCreate.as_view(), name='issue_add'),
    url(r'^(?P<pk>[0-9]+)/$', views.IssueDetail.as_view(), name='issue_detail'),
    url(r'^(?P<pk>[0-9]+)/update/$', views.IssueUpdateStatus.as_view(), name='issue_status_update'),
    url(r'^(?P<issue_pk>[0-9]+)/comment/$', views.CommentCreate.as_view(), name='comment_add'),
]
