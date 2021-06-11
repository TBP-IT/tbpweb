from django.conf.urls import patterns
from django.conf.urls import url

from tbpweb.syllabi.views import SyllabusDeleteView
from tbpweb.syllabi.views import SyllabusDownloadView
from tbpweb.syllabi.views import SyllabusEditView
from tbpweb.syllabi.views import SyllabusFlagCreateView
from tbpweb.syllabi.views import SyllabusFlagResolveView
from tbpweb.syllabi.views import SyllabusReviewListView
from tbpweb.syllabi.views import SyllabusUploadView


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
