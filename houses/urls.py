from django.urls import re_path

from houses.views import assign_house
from houses.views import HouseMembersEditView
from houses.views import HouseMembersListView
from houses.views import unassign_house


urlpatterns = [
    re_path(r'^$', HouseMembersListView.as_view(), name='list'),
    re_path(r'^assign/$', assign_house, name='assign'),
    re_path(r'^edit/$', HouseMembersEditView.as_view(), name='edit'),
    re_path(r'^unassign/$', unassign_house, name='unassign'),
]
