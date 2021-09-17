from django.urls import re_path

from resumes.views import ResumeListView
from resumes.views import ResumeCritiqueView
from resumes.views import ResumeDownloadView
from resumes.views import ResumeEditView
from resumes.views import ResumeVerifyView


urlpatterns = [
    re_path(r'^$', ResumeListView.as_view(), name='list'),
    re_path(r'^edit/$', ResumeEditView.as_view(), name='edit'),
    re_path(r'^download/$', ResumeDownloadView.as_view(), name='download'),
    re_path(r'^download/(?P<user_pk>\d+)/$',
        ResumeDownloadView.as_view(), name='download'),
    re_path(r'^critique/$', ResumeCritiqueView.as_view(), name='critique'),
    re_path(r'^verify/$', ResumeVerifyView.as_view(), name='verify'),
]
