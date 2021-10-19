from django.urls import re_path

from user_profiles.views import UserProfileDetailView
from user_profiles.views import UserProfileEditView
from user_profiles.views import UserProfilePictureEditView


urlpatterns = [
    re_path(r'^edit/$', UserProfileEditView.as_view(), name='edit'),
    re_path(r'^picture/$', UserProfilePictureEditView.as_view(), name='edit-pic'),
    re_path(r'^u/(?P<username>[a-zA-Z0-9._-]+)/$', UserProfileDetailView.as_view(),
        name='detail'),
]
