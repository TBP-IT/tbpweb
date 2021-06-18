from django.conf.urls import patterns
from django.conf.urls import url

from resumes.views import ResumeListView
from resumes.views import ResumeCritiqueView
from resumes.views import ResumeDownloadView
from resumes.views import ResumeEditView
from resumes.views import ResumeVerifyView


urlpatterns = patterns(
    '',
    url(r'^$', ResumeListView.as_view(), name='list'),
    url(r'^edit/$', ResumeEditView.as_view(), name='edit'),
    url(r'^download/$', ResumeDownloadView.as_view(), name='download'),
    url(r'^download/(?P<user_pk>\d+)/$',
        ResumeDownloadView.as_view(), name='download'),
    url(r'^critique/$', ResumeCritiqueView.as_view(), name='critique'),
    url(r'^verify/$', ResumeVerifyView.as_view(), name='verify'),
    )
