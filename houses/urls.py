from django.urls import path

from houses.views import assign_house
from houses.views import HouseMembersEditView
from houses.views import HouseMembersListView
from houses.views import unassign_house


urlpatterns = [
    path('', HouseMembersListView.as_view(), name='list'),
    path('assign/', assign_house, name='assign'),
    path('edit/', HouseMembersEditView.as_view(), name='edit'),
    path('unassign/', unassign_house, name='unassign'),
]
