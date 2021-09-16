from django.urls import patterns
from django.urls import url

from vote.views import PollCreateView
from vote.views import PollListView
from vote.views import ResultsView
from vote.views import VoteCreateView


urlpatterns = patterns(
    '',
    url(r'^$', PollListView.as_view(), name='list'),
    url(r'^create/$', PollCreateView.as_view(), name='create'),
    url(r'^vote/(?P<poll_pk>\d+)/$', VoteCreateView.as_view(), name='vote'),
    url(r'^result/(?P<poll_pk>\d+)/$', ResultsView.as_view(), name='result')
)
