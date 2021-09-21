from django.urls import re_path
from candidates.views import CandidateCreateView, CandidateEditView, CandidateExportView, \
                             CandidateInitiationView, CandidateListView, CandidatePhotoView, \
                             CandidatePortalView, CandidateProgressView, \
                             CandidateProgressByReqView, CandidateProgressStatsView, \
                             CandidateRequirementsEditView, ChallengeVerifyView, \
                             ManualCandidateRequirementCreateView, update_candidate_initiation_status


urlpatterns = [
    re_path(r'^$', CandidateListView.as_view(), name='list'),
    re_path(r'^(?P<candidate_pk>\d+)/$', CandidateEditView.as_view(),
        name='edit'),
    re_path(r'^(?P<candidate_pk>\d+)/photo$', CandidatePhotoView.as_view(),
        name='photo'),
    re_path(r'^create/$', CandidateCreateView.as_view(), name='create'),
    re_path(r'^challenges/$', ChallengeVerifyView.as_view(), name='challenges'),
    re_path(r'^export/(?P<term_pk>\d+)/$', CandidateExportView.as_view(),
        name='export'),
    re_path(r'^initiation/$', CandidateInitiationView.as_view(),
        name='initiation'),
    re_path(r'^initiation/update/$', update_candidate_initiation_status,
        name='initiation-update'),
    re_path(r'^portal/$', CandidatePortalView.as_view(), name='portal'),
    re_path(r'^progress/$', CandidateProgressView.as_view(), name='progress'),
    re_path(r'^progress/by-req/$', CandidateProgressByReqView.as_view(),
        name='progress-by-req'),
    re_path(r'^progress/stats/$', CandidateProgressStatsView.as_view(),
        name='progress-stats'),
    re_path(r'^requirements/$',
        CandidateRequirementsEditView.as_view(), name='edit-requirements'),
    re_path(r'^requirements/add/$',
        ManualCandidateRequirementCreateView.as_view(), name='add-requirement'),
]
