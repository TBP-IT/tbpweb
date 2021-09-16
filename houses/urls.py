from django.urls import patterns
from django.urls import url

from houses.views import assign_house
from houses.views import HouseMembersEditView
from houses.views import HouseMembersListView
from houses.views import unassign_house


urlpatterns = patterns(
    '',
    url(r'^$', HouseMembersListView.as_view(), name='list'),
    url(r'^assign/$', assign_house, name='assign'),
    url(r'^edit/$', HouseMembersEditView.as_view(), name='edit'),
    url(r'^unassign/$', unassign_house, name='unassign'),
)
