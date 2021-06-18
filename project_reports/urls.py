from django.conf.urls import patterns
from django.conf.urls import url

from project_reports.views import ProjectReportCreateView
from project_reports.views import ProjectReportDeleteView
from project_reports.views import ProjectReportDetailView
from project_reports.views import ProjectReportEditView
from project_reports.views import ProjectReportListAllView
from project_reports.views import ProjectReportListView
from project_reports.views import ProjectReportBookExportView
from project_reports.views import ProjectReportBookDownloadView


urlpatterns = patterns(
    '',
    url(r'^$', ProjectReportListView.as_view(), name='list'),
    url(r'^(?P<pr_pk>\d+)/$', ProjectReportDetailView.as_view(),
        name='detail'),
    url(r'^(?P<pr_pk>\d+)/edit/$', ProjectReportEditView.as_view(),
        name='edit'),
    url(r'^(?P<pr_pk>\d+)/delete/$', ProjectReportDeleteView.as_view(),
        name='delete'),
    url(r'^add/$', ProjectReportCreateView.as_view(), name='add'),
    url(r'^all/$', ProjectReportListAllView.as_view(), name='list-all'),
    url(r'^export-book/$', ProjectReportBookExportView.as_view(),
        name='export-book'),
    url(r'^download-book/(?P<book_pk>\d+)/$',
        ProjectReportBookDownloadView.as_view(), name='download-book'),
)
