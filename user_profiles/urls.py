from django.urls import patterns
from django.urls import url

from user_profiles.views import UserProfileDetailView
from user_profiles.views import UserProfileEditView
from user_profiles.views import UserProfilePictureEditView


urlpatterns = patterns(
    '',
    url(r'^edit/$', UserProfileEditView.as_view(), name='edit'),
    url(r'^picture/$', UserProfilePictureEditView.as_view(), name='edit-pic'),
    url(r'^u/(?P<username>[a-zA-Z0-9._-]+)/$', UserProfileDetailView.as_view(),
        name='detail'),
)
