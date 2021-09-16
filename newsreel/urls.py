from django.urls import patterns
from django.urls import url

from newsreel.views import news_reorder
from newsreel.views import NewsCreateView
from newsreel.views import NewsDeleteView
from newsreel.views import NewsEditView
from newsreel.views import NewsListView


urlpatterns = patterns(
    '',
    url(r'^$', NewsListView.as_view(), name='list'),
    url(r'^add/$', NewsCreateView.as_view(), name='add'),
    url(r'^edit/(?P<news_pk>\d+)/$', NewsEditView.as_view(), name='edit'),
    url(r'^delete/(?P<news_pk>\d+)/$', NewsDeleteView.as_view(), name='delete'),
    url(r'^reorder/$', news_reorder, name='reorder'),
)
