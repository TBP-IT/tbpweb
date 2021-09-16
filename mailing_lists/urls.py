from django.urls import patterns
from django.urls import url

from mailing_lists.views import MailingListsListAllView


urlpatterns = patterns(
    '',
    url(r'^$', MailingListsListAllView.as_view(), name='list'),
)
