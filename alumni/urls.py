from django.urls import re_path
from alumni.views import AlumnusCreateView, AlumnusEditView, AlumnusListView

urlpatterns = [
    re_path(r'^$', AlumnusListView.as_view(), name='list'),
    re_path(r'^add/$', AlumnusCreateView.as_view(), name='add-alumnus'),
    re_path(r'^(?P<alum_pk>[0-9]+)/edit/$', AlumnusEditView.as_view(),
        name='edit-alumnus'),
]
