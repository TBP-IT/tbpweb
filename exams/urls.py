from django.urls import re_path

from exams.views import ExamDeleteView
from exams.views import ExamDownloadView
from exams.views import ExamEditView
from exams.views import ExamFlagCreateView
from exams.views import ExamFlagResolveView
from exams.views import ExamReviewListView
from exams.views import ExamUploadView


urlpatterns = [
    re_path(r'^review/$', ExamReviewListView.as_view(), name='review'),
    re_path(r'^upload/$', ExamUploadView.as_view(), name='upload'),
    re_path(r'^(?P<exam_pk>\d+)/edit/$', ExamEditView.as_view(), name='edit'),
    re_path(r'^(?P<exam_pk>\d+)/delete/$', ExamDeleteView.as_view(), name='delete'),
    re_path(r'^(?P<exam_pk>\d+)/download/$', ExamDownloadView.as_view(),
        name='download'),
    re_path(r'^(?P<exam_pk>\d+)/flag/$', ExamFlagCreateView.as_view(), name='flag'),
    re_path(r'^(?P<exam_pk>\d+)/flag/(?P<flag_pk>\d+)/$',
        ExamFlagResolveView.as_view(), name='flag-resolve'),
]
