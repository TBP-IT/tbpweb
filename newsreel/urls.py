from django.urls import re_path

from newsreel.views import news_reorder
from newsreel.views import NewsCreateView
from newsreel.views import NewsDeleteView
from newsreel.views import NewsEditView
from newsreel.views import NewsListView


urlpatterns = [
    re_path(r'^$', NewsListView.as_view(), name='list'),
    re_path(r'^add/$', NewsCreateView.as_view(), name='add'),
    re_path(r'^edit/(?P<news_pk>\d+)/$', NewsEditView.as_view(), name='edit'),
    re_path(r'^delete/(?P<news_pk>\d+)/$', NewsDeleteView.as_view(), name='delete'),
    re_path(r'^reorder/$', news_reorder, name='reorder'),
]
