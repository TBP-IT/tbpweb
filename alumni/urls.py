from django.conf.urls import patterns
from django.conf.urls import url
from quark.alumni.views import AlumnusCreateView
from quark.alumni.views import AlumnusEditView
from quark.alumni.views import AlumnusListView

urlpatterns = patterns(
    '',
    url(r'^$', AlumnusListView.as_view(), name='list'),
    url(r'^add/$', AlumnusCreateView.as_view(), name='add-alumnus'),
    url(r'^(?P<alum_pk>[0-9]+)/edit/$', AlumnusEditView.as_view(),
        name='edit-alumnus'),
)
