from django.urls import re_path

from project_reports.views import ProjectReportCreateView
from project_reports.views import ProjectReportDeleteView
from project_reports.views import ProjectReportDetailView
from project_reports.views import ProjectReportEditView
from project_reports.views import ProjectReportListAllView
from project_reports.views import ProjectReportListView
from project_reports.views import ProjectReportBookExportView
from project_reports.views import ProjectReportBookDownloadView


urlpatterns = [
    re_path(r'^$', ProjectReportListView.as_view(), name='list'),
    re_path(r'^(?P<pr_pk>\d+)/$', ProjectReportDetailView.as_view(),
        name='detail'),
    re_path(r'^(?P<pr_pk>\d+)/edit/$', ProjectReportEditView.as_view(),
        name='edit'),
    re_path(r'^(?P<pr_pk>\d+)/delete/$', ProjectReportDeleteView.as_view(),
        name='delete'),
    re_path(r'^add/$', ProjectReportCreateView.as_view(), name='add'),
    re_path(r'^all/$', ProjectReportListAllView.as_view(), name='list-all'),
    re_path(r'^export-book/$', ProjectReportBookExportView.as_view(),
        name='export-book'),
    re_path(r'^download-book/(?P<book_pk>\d+)/$',
        ProjectReportBookDownloadView.as_view(), name='download-book'),
]
