from django.urls import patterns
from django.urls import url

from candidates.views import CandidateCreateView
from candidates.views import CandidateEditView
from candidates.views import CandidateExportView
from candidates.views import CandidateInitiationView
from candidates.views import CandidateListView
from candidates.views import CandidatePhotoView
from candidates.views import CandidatePortalView
from candidates.views import CandidateProgressView
from candidates.views import CandidateProgressByReqView
from candidates.views import CandidateProgressStatsView
from candidates.views import CandidateRequirementsEditView
from candidates.views import ChallengeVerifyView
from candidates.views import ManualCandidateRequirementCreateView
from candidates.views import update_candidate_initiation_status


urlpatterns = patterns(
    '',
    url(r'^$', CandidateListView.as_view(), name='list'),
    url(r'^(?P<candidate_pk>\d+)/$', CandidateEditView.as_view(),
        name='edit'),
    url(r'^(?P<candidate_pk>\d+)/photo$', CandidatePhotoView.as_view(),
        name='photo'),
    url(r'^create/$', CandidateCreateView.as_view(), name='create'),
    url(r'^challenges/$', ChallengeVerifyView.as_view(), name='challenges'),
    url(r'^export/(?P<term_pk>\d+)/$', CandidateExportView.as_view(),
        name='export'),
    url(r'^initiation/$', CandidateInitiationView.as_view(),
        name='initiation'),
    url(r'^initiation/update/$', update_candidate_initiation_status,
        name='initiation-update'),
    url(r'^portal/$', CandidatePortalView.as_view(), name='portal'),
    url(r'^progress/$', CandidateProgressView.as_view(), name='progress'),
    url(r'^progress/by-req/$', CandidateProgressByReqView.as_view(),
        name='progress-by-req'),
    url(r'^progress/stats/$', CandidateProgressStatsView.as_view(),
        name='progress-stats'),
    url(r'^requirements/$',
        CandidateRequirementsEditView.as_view(), name='edit-requirements'),
    url(r'^requirements/add/$',
        ManualCandidateRequirementCreateView.as_view(), name='add-requirement'),
)
