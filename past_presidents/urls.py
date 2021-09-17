from django.urls import re_path

from past_presidents.views import PastPresidentsListView
from past_presidents.views import PastPresidentsDetailView

urlpatterns = [
    re_path(r'^$', PastPresidentsListView.as_view(), name='list'),
    re_path(r'^words/(?P<past_president_id>\d+)/$',
        PastPresidentsDetailView.as_view(), name='detail'),
]
