from django.conf.urls import patterns
from django.conf.urls import url

from videos.views import VideoCreateView
from videos.views import VideoListView
from videos.views import VideoTypeCreateView


urlpatterns = patterns(
    '',
    url(r'^$', VideoListView.as_view(), name='list'),
    url(r'^add/$', VideoCreateView.as_view(), name='add'),
    url(r'^addtype/$', VideoTypeCreateView.as_view(), name='addtype'),
)
