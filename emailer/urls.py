from django.conf.urls import patterns
from django.conf.urls import url

from tbpweb.emailer.views import CompanyEmailerView
from tbpweb.emailer.views import EventEmailerView
from tbpweb.emailer.views import HelpdeskEmailerView


urlpatterns = patterns(
    '',
    url(r'^helpdesk/$', HelpdeskEmailerView.as_view(),
        name='helpdesk'),
    url(r'^events/(?P<event_pk>\d+)/$', EventEmailerView.as_view(),
        name='event'),
    url(r'^industry/$', CompanyEmailerView.as_view(),
        name='company'),
)
