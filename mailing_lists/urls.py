from django.urls import re_path

from mailing_lists.views import MailingListsListAllView


urlpatterns = [
    re_path(r'^$', MailingListsListAllView.as_view(), name='list'),
]
