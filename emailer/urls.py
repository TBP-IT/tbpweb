from django.urls import re_path

from emailer.views import CompanyEmailerView
from emailer.views import EventEmailerView
from emailer.views import HelpdeskEmailerView


urlpatterns = [
    re_path(r'^helpdesk/$', HelpdeskEmailerView.as_view(),
        name='helpdesk'),
    re_path(r'^events/(?P<event_pk>\d+)/$', EventEmailerView.as_view(),
        name='event'),
    re_path(r'^industry/$', CompanyEmailerView.as_view(),
        name='company'),
]
