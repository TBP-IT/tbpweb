from django.conf.urls import patterns
from django.conf.urls import url

from tbpweb.quote_board.views import QuoteCreateView
from tbpweb.quote_board.views import QuoteDetailView
from tbpweb.quote_board.views import QuoteLeaderboardListView
from tbpweb.quote_board.views import QuoteListView
from tbpweb.quote_board.views import SpeakerQuoteListView


urlpatterns = patterns(
    '',
    url(r'^$', QuoteListView.as_view(), name='list'),
    url(r'^(?P<quote_pk>\d+)/$', QuoteDetailView.as_view(), name='detail'),
    url(r'^add/$', QuoteCreateView.as_view(), name='add'),
    url(r'^leaderboard/$', QuoteLeaderboardListView.as_view(),
        name='leaderboard'),
    url(r'^speaker/(?P<user_id>\d+)/$', SpeakerQuoteListView.as_view(),
        name='speaker'),
)
