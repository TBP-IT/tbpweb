from django.conf.urls import patterns
from django.conf.urls import url

from quark.candidates.views import CandidateCreateView
from quark.candidates.views import CandidateEditView
from quark.candidates.views import CandidateExportView
from quark.candidates.views import CandidateInitiationView
from quark.candidates.views import CandidateListView
from quark.candidates.views import CandidatePhotoView
from quark.candidates.views import CandidatePortalView
from quark.candidates.views import CandidateProgressView
from quark.candidates.views import CandidateProgressByReqView
from quark.candidates.views import CandidateProgressStatsView
from quark.candidates.views import CandidateRequirementsEditView
from quark.candidates.views import ChallengeVerifyView
from quark.candidates.views import ManualCandidateRequirementCreateView
from quark.candidates.views import update_candidate_initiation_status


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
