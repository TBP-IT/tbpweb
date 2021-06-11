from django.conf.urls import patterns
from django.conf.urls import url

from tbpweb.candidates.views import CandidateCreateView
from tbpweb.candidates.views import CandidateEditView
from tbpweb.candidates.views import CandidateExportView
from tbpweb.candidates.views import CandidateInitiationView
from tbpweb.candidates.views import CandidateListView
from tbpweb.candidates.views import CandidatePhotoView
from tbpweb.candidates.views import CandidatePortalView
from tbpweb.candidates.views import CandidateProgressView
from tbpweb.candidates.views import CandidateProgressByReqView
from tbpweb.candidates.views import CandidateProgressStatsView
from tbpweb.candidates.views import CandidateRequirementsEditView
from tbpweb.candidates.views import ChallengeVerifyView
from tbpweb.candidates.views import ManualCandidateRequirementCreateView
from tbpweb.candidates.views import update_candidate_initiation_status


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
