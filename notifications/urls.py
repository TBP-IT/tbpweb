from django.urls import re_path

from notifications.views import clear_notification


urlpatterns = [
    re_path(r'^clear/(?P<notification_pk>\d+)/$', clear_notification, name='clear'),
]
