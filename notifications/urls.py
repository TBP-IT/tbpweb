from django.urls import patterns
from django.urls import url

from notifications.views import clear_notification


urlpatterns = patterns(
    '',
    url(r'^clear/(?P<notification_pk>\d+)/$', clear_notification, name='clear'),
)
