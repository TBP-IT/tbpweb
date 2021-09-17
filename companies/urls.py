from django.urls import re_path

from companies.views import CompanyCreateView
from companies.views import CompanyDetailView
from companies.views import CompanyEditView
from companies.views import CompanyListView
from companies.views import CompanyRepCreateView
from companies.views import CompanyRepDeleteView
from companies.views import IndustryLandingView
from companies.views import ResumeListView
from companies.views import ResumeZipView


urlpatterns = [
    re_path(r'^$', IndustryLandingView.as_view(), name='landing'),
    re_path(r'^companies/$', CompanyListView.as_view(), name='list'),
    re_path(r'^companies/(?P<company_pk>\d+)/$', CompanyDetailView.as_view(),
        name='company-detail'),
    re_path(r'^companies/create/$', CompanyCreateView.as_view(),
        name='company-create'),
    re_path(r'^companies/edit/(?P<company_pk>\d+)/$', CompanyEditView.as_view(),
        name='company-edit'),
    re_path(r'^companies/rep-create/$', CompanyRepCreateView.as_view(),
        name='rep-create'),
    re_path(r'^companies/rep-delete/(?P<rep_pk>\d+)/$',
        CompanyRepDeleteView.as_view(), name='rep-delete'),
    re_path(r'^resumes/$', ResumeListView.as_view(),
        name='resumes'),
    re_path(r'^resumes/download-all-resumes/$', ResumeZipView.as_view(),
        name='download-all-resumes'),

    # TODO(sjdemartini): Add views for companies to manage their own contact
    # information and company info (e.g., website and logo)
]
