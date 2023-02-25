from django.urls import re_path

from emailer.views import CompanyEmailerView
from emailer.views import EventEmailerView


urlpatterns = [
    re_path(r'^events/(?P<event_pk>\d+)/$', EventEmailerView.as_view(),
        name='event'),
    re_path(r'^industry/$', CompanyEmailerView.as_view(),
        name='company'),
]
