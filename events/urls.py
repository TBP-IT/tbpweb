from django.urls import re_path

from emailer.views import EventEmailerView
from events.views import AllTimeLeaderboardListView
from events.views import attendance_delete
from events.views import attendance_search
from events.views import attendance_submit
from events.views import AttendanceRecordView
from events.views import EventBuilderView
from events.views import EventCancelView
from events.views import EventCreateView
from events.views import EventDetailView
from events.views import EventListView
from events.views import EventSignUpView
from events.views import event_revive
from events.views import event_unsignup
from events.views import EventUpdateView
from events.views import ical
from events.views import IndividualAttendanceListView
from events.views import LeaderboardListView

urlpatterns = [
    re_path(r'^$', EventListView.as_view(), name='list'),
    re_path(r'^builder/$', EventBuilderView.as_view(), name='builder'),
    re_path(r'^add/$', EventCreateView.as_view(), name='add'),
    re_path(r'^(?P<event_pk>\d+)/$', EventDetailView.as_view(),
        name='detail'),
    re_path(r'^(?P<event_pk>\d+)/edit/$', EventUpdateView.as_view(), name='edit'),
    re_path(r'^(?P<event_pk>\d+)/cancel/$', EventCancelView.as_view(),
        name='cancel'),
    re_path(r'^(?P<event_pk>\d+)/revive/$', event_revive,
        name='revive'),
    re_path(r'^(?P<event_pk>\d+)/signup/$', EventSignUpView.as_view(),
        name='signup'),
    re_path(r'^(?P<event_pk>\d+)/unsignup/$', event_unsignup,
        name='unsignup'),
    re_path(r'^(?P<event_pk>\d+)/attendance/$', AttendanceRecordView.as_view(),
        name='attendance'),
    re_path(r'^(?P<event_pk>\d+)/email/$', EventEmailerView.as_view(),
        name='email'),
    re_path(r'^attendance/delete/$', attendance_delete, name='attendance-delete'),
    re_path(r'^attendance/search/$', attendance_search, name='attendance-search'),
    re_path(r'^attendance/submit/$', attendance_submit, name='attendance-submit'),
    re_path(r'^user/(?P<username>[a-zA-Z0-9._-]+)/$',
        IndividualAttendanceListView.as_view(), name='individual-attendance'),
    re_path(r'^calendar/$', EventListView.as_view(show_all=True,
        template_name='events/calendar.html'), name='calendar'),
    re_path(r'^leaderboard/$', LeaderboardListView.as_view(), name='leaderboard'),
    re_path(r'^leaderboard/all-time/$',
        AllTimeLeaderboardListView.as_view(), name='all-time-leaderboard'),
    re_path(r'^events.ics$', ical, name='ical'),
    re_path(r'^(?P<event_pk>\d+)/event.ics$', ical, name='event-ical'),
]
