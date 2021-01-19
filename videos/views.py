from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import ListView

from quark.videos.forms import VideoForm
from quark.videos.forms import VideoTypeForm
from quark.videos.models import Video
from quark.videos.models import VideoType


class VideoCreateView(CreateView):
    form_class = VideoForm
    model = Video
    success_url = reverse_lazy('videos:list')
    template_name = 'videos/add.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('videos.add_video', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(VideoCreateView, self).dispatch(*args, **kwargs)


class VideoListView(ListView):
    context_object_name = 'video_items'
    model = Video
    template_name = 'videos/list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if user.userprofile and user.userprofile.is_member():
            return super(VideoListView, self).dispatch(*args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(VideoListView, self).get_context_data(**kwargs)
        video_lists = {}

        for video in Video.objects.all():
            if video.term in video_lists:
                video_lists.get(video.term).append(video)
            else:
                video_lists[video.term] = [video]

        # sort videos by semester, with most recent semesters at the top
        context['video_lists'] = OrderedDict(sorted(
            video_lists.items(), key=lambda x: x[0].id, reverse=True))
        return context


class VideoTypeCreateView(CreateView):
    form_class = VideoTypeForm
    model = VideoType
    success_url = reverse_lazy('videos:add')
    template_name = 'videos/addtype.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('videos.add_videotype', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(VideoTypeCreateView, self).dispatch(*args, **kwargs)
