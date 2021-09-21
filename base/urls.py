from django.urls import path

from .views import HomePageView, ITToolsView, OfficerContactExportView, OfficersListView, OfficerPortalView, ProcrastinationView

app_name = 'base'
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('officers/', OfficersListView.as_view(), name='officers'),
    path('officers/contacts/', OfficerContactExportView.as_view(),
        name='officer-contacts'),
    # TODO(sjdemartini): Restrict the pages below with proper permissions
    path('officer-portal/', OfficerPortalView.as_view(),
        name='officer-portal'),
    path('it-tools/', ITToolsView.as_view(), name='it-tools'),
    path('procrastination/', ProcrastinationView.as_view(),
        name='procrastination'),
    # TODO(sjdemartini): Add a Members database view
]

