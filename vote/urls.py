from django.urls import re_path

from vote.views import PollCreateView
from vote.views import PollListView
from vote.views import ResultsView
from vote.views import VoteCreateView


urlpatterns = [
    re_path(r'^$', PollListView.as_view(), name='list'),
    re_path(r'^create/$', PollCreateView.as_view(), name='create'),
    re_path(r'^vote/(?P<poll_pk>\d+)/$', VoteCreateView.as_view(), name='vote'),
    re_path(r'^result/(?P<poll_pk>\d+)/$', ResultsView.as_view(), name='result')
]
