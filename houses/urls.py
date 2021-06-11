from django.conf.urls import patterns
from django.conf.urls import url

from tbpweb.houses.views import assign_house
from tbpweb.houses.views import HouseMembersEditView
from tbpweb.houses.views import HouseMembersListView
from tbpweb.houses.views import unassign_house


urlpatterns = patterns(
    '',
    url(r'^$', HouseMembersListView.as_view(), name='list'),
    url(r'^assign/$', assign_house, name='assign'),
    url(r'^edit/$', HouseMembersEditView.as_view(), name='edit'),
    url(r'^unassign/$', unassign_house, name='unassign'),
)
