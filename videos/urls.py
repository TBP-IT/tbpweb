from django.urls import re_path

from videos.views import VideoCreateView
from videos.views import VideoListView
from videos.views import VideoTypeCreateView


urlpatterns = [
    re_path(r'^$', VideoListView.as_view(), name='list'),
    re_path(r'^add/$', VideoCreateView.as_view(), name='add'),
    re_path(r'^addtype/$', VideoTypeCreateView.as_view(), name='addtype'),
]
