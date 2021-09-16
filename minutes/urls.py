from django.urls import patterns
from django.urls import url

from minutes.views import MinutesListView
from minutes.views import MinutesCreateView
from minutes.views import MinutesDetailView
from minutes.views import MinutesEditView
from minutes.views import MinutesUploadView


urlpatterns = patterns(
    '',
    url(r'^$', MinutesListView.as_view(), name='list'),
    url(r'^(?P<minute_id>\d+)/$', MinutesDetailView.as_view(), name='detail'),
    url(r'^edit/(?P<minute_id>\d+)/$', MinutesEditView.as_view(), name='edit'),
    url(r'^add/$', MinutesCreateView.as_view(), name='add'),
    url(r'^upload/$', MinutesUploadView.as_view(), name='upload')
)
