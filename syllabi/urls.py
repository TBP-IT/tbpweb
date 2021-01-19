from django.conf.urls import patterns
from django.conf.urls import url

from quark.syllabi.views import SyllabusDeleteView
from quark.syllabi.views import SyllabusDownloadView
from quark.syllabi.views import SyllabusEditView
from quark.syllabi.views import SyllabusFlagCreateView
from quark.syllabi.views import SyllabusFlagResolveView
from quark.syllabi.views import SyllabusReviewListView
from quark.syllabi.views import SyllabusUploadView


urlpatterns = patterns(
    '',
    url(r'^review/$', SyllabusReviewListView.as_view(), name='review'),
    url(r'^upload/$', SyllabusUploadView.as_view(), name='upload'),
    url(r'^(?P<syllabus_pk>\d+)/edit/$',
        SyllabusEditView.as_view(), name='edit'),
    url(r'^(?P<syllabus_pk>\d+)/delete/$',
        SyllabusDeleteView.as_view(), name='delete'),
    url(r'^(?P<syllabus_pk>\d+)/download/$',
        SyllabusDownloadView.as_view(), name='download'),
    url(r'^(?P<syllabus_pk>\d+)/flag/$',
        SyllabusFlagCreateView.as_view(), name='flag'),
    url(r'^(?P<syllabus_pk>\d+)/flag/(?P<flag_pk>\d+)/$',
        SyllabusFlagResolveView.as_view(), name='flag-resolve'),
)
