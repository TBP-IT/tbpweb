from django.conf.urls import patterns
from django.conf.urls import url

from quark.emailer.views import EventEmailerView
from quark.events.views import AllTimeLeaderboardListView
from quark.events.views import attendance_delete
from quark.events.views import attendance_search
from quark.events.views import attendance_submit
from quark.events.views import AttendanceRecordView
from quark.events.views import EventBuilderView
from quark.events.views import EventCancelView
from quark.events.views import EventCreateView
from quark.events.views import EventDetailView
from quark.events.views import EventListView
from quark.events.views import EventSignUpView
from quark.events.views import event_revive
from quark.events.views import event_unsignup
from quark.events.views import EventUpdateView
from quark.events.views import ical
from quark.events.views import IndividualAttendanceListView
from quark.events.views import LeaderboardListView

urlpatterns = patterns(
    '',
    url(r'^$', EventListView.as_view(), name='list'),
    url(r'^builder/$', EventBuilderView.as_view(), name='builder'),
    url(r'^add/$', EventCreateView.as_view(), name='add'),
    url(r'^(?P<event_pk>\d+)/$', EventDetailView.as_view(),
        name='detail'),
    url(r'^(?P<event_pk>\d+)/edit/$', EventUpdateView.as_view(), name='edit'),
    url(r'^(?P<event_pk>\d+)/cancel/$', EventCancelView.as_view(),
        name='cancel'),
    url(r'^(?P<event_pk>\d+)/revive/$', event_revive,
        name='revive'),
    url(r'^(?P<event_pk>\d+)/signup/$', EventSignUpView.as_view(),
        name='signup'),
    url(r'^(?P<event_pk>\d+)/unsignup/$', event_unsignup,
        name='unsignup'),
    url(r'^(?P<event_pk>\d+)/attendance/$', AttendanceRecordView.as_view(),
        name='attendance'),
    url(r'^(?P<event_pk>\d+)/email/$', EventEmailerView.as_view(),
        name='email'),
    url(r'^attendance/delete/$', attendance_delete, name='attendance-delete'),
    url(r'^attendance/search/$', attendance_search, name='attendance-search'),
    url(r'^attendance/submit/$', attendance_submit, name='attendance-submit'),
    url(r'^user/(?P<username>[a-zA-Z0-9._-]+)/$',
        IndividualAttendanceListView.as_view(), name='individual-attendance'),
    url(r'^calendar/$', EventListView.as_view(show_all=True,
        template_name='events/calendar.html'), name='calendar'),
    url(r'^leaderboard/$', LeaderboardListView.as_view(), name='leaderboard'),
    url(r'^leaderboard/all-time/$',
        AllTimeLeaderboardListView.as_view(), name='all-time-leaderboard'),
    url(r'^events.ics$', ical, name='ical'),
    url(r'^(?P<event_pk>\d+)/event.ics$', ical, name='event-ical'),
)
