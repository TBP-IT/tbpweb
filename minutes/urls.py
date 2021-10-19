from django.urls import re_path

from minutes.views import MinutesListView
from minutes.views import MinutesCreateView
from minutes.views import MinutesDetailView
from minutes.views import MinutesEditView
from minutes.views import MinutesUploadView


urlpatterns = [
    re_path(r'^$', MinutesListView.as_view(), name='list'),
    re_path(r'^(?P<minute_id>\d+)/$', MinutesDetailView.as_view(), name='detail'),
    re_path(r'^edit/(?P<minute_id>\d+)/$', MinutesEditView.as_view(), name='edit'),
    re_path(r'^add/$', MinutesCreateView.as_view(), name='add'),
    re_path(r'^upload/$', MinutesUploadView.as_view(), name='upload')
]
