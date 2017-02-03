from django.conf.urls import url, include

from . import views

urlpatterns = [
    # User management stuff
    url(r'^$', views.IssueList.as_view(), {'mode': 'open'}, name='index'),
    url(r'^mine/$', views.IssueList.as_view(), {'mode': 'mine'}, name='myissue_list'),
    url(r'^closed/$', views.IssueList.as_view(), {'mode': 'closed'}, name='closedissue_list'),
    url(r'^add/$', views.IssueCreate.as_view(), {'mode': 'add'}, name='issue_add'),
    url(r'^(?P<pk>[0-9]+)/$', views.IssueDetail.as_view(), name='issue_detail'),
    url(r'^(?P<issue_pk>[0-9]+)/comment/$', views.CommentCreate.as_view(), name='comment_add'),
]
