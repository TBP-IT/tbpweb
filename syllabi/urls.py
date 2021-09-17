from django.urls import re_path

from syllabi.views import SyllabusDeleteView
from syllabi.views import SyllabusDownloadView
from syllabi.views import SyllabusEditView
from syllabi.views import SyllabusFlagCreateView
from syllabi.views import SyllabusFlagResolveView
from syllabi.views import SyllabusReviewListView
from syllabi.views import SyllabusUploadView


urlpatterns = [
    re_path(r'^review/$', SyllabusReviewListView.as_view(), name='review'),
    re_path(r'^upload/$', SyllabusUploadView.as_view(), name='upload'),
    re_path(r'^(?P<syllabus_pk>\d+)/edit/$',
        SyllabusEditView.as_view(), name='edit'),
    re_path(r'^(?P<syllabus_pk>\d+)/delete/$',
        SyllabusDeleteView.as_view(), name='delete'),
    re_path(r'^(?P<syllabus_pk>\d+)/download/$',
        SyllabusDownloadView.as_view(), name='download'),
    re_path(r'^(?P<syllabus_pk>\d+)/flag/$',
        SyllabusFlagCreateView.as_view(), name='flag'),
    re_path(r'^(?P<syllabus_pk>\d+)/flag/(?P<flag_pk>\d+)/$',
        SyllabusFlagResolveView.as_view(), name='flag-resolve'),
]
