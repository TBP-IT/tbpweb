from django.urls import patterns
from django.urls import url

from exams.views import ExamDeleteView
from exams.views import ExamDownloadView
from exams.views import ExamEditView
from exams.views import ExamFlagCreateView
from exams.views import ExamFlagResolveView
from exams.views import ExamReviewListView
from exams.views import ExamUploadView


urlpatterns = patterns(
    '',
    url(r'^review/$', ExamReviewListView.as_view(), name='review'),
    url(r'^upload/$', ExamUploadView.as_view(), name='upload'),
    url(r'^(?P<exam_pk>\d+)/edit/$', ExamEditView.as_view(), name='edit'),
    url(r'^(?P<exam_pk>\d+)/delete/$', ExamDeleteView.as_view(), name='delete'),
    url(r'^(?P<exam_pk>\d+)/download/$', ExamDownloadView.as_view(),
        name='download'),
    url(r'^(?P<exam_pk>\d+)/flag/$', ExamFlagCreateView.as_view(), name='flag'),
    url(r'^(?P<exam_pk>\d+)/flag/(?P<flag_pk>\d+)/$',
        ExamFlagResolveView.as_view(), name='flag-resolve'),
)
