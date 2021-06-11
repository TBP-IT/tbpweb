from django.conf.urls import patterns
from django.conf.urls import url

from tbpweb.exams.views import ExamDeleteView
from tbpweb.exams.views import ExamDownloadView
from tbpweb.exams.views import ExamEditView
from tbpweb.exams.views import ExamFlagCreateView
from tbpweb.exams.views import ExamFlagResolveView
from tbpweb.exams.views import ExamReviewListView
from tbpweb.exams.views import ExamUploadView


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
