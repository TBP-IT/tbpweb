from django.urls import re_path

from quote_board.views import QuoteCreateView
from quote_board.views import QuoteDetailView
from quote_board.views import QuoteLeaderboardListView
from quote_board.views import QuoteListView
from quote_board.views import SpeakerQuoteListView


urlpatterns = [
    re_path(r'^$', QuoteListView.as_view(), name='list'),
    re_path(r'^(?P<quote_pk>\d+)/$', QuoteDetailView.as_view(), name='detail'),
    re_path(r'^add/$', QuoteCreateView.as_view(), name='add'),
    re_path(r'^leaderboard/$', QuoteLeaderboardListView.as_view(),
        name='leaderboard'),
    re_path(r'^speaker/(?P<user_id>\d+)/$', SpeakerQuoteListView.as_view(),
        name='speaker'),
]
