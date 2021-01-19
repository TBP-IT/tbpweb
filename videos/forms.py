from chosen import forms as chosen_forms
from django import forms

from quark.videos.models import Video
from quark.videos.models import VideoType


class VideoForm(forms.ModelForm):
    class Meta(object):
        model = Video
        exclude = ['video_file']
        widgets = {
            'term': chosen_forms.ChosenSelect(),
            'video_type': chosen_forms.ChosenSelect()
        }


class VideoTypeForm(forms.ModelForm):
    class Meta(object):
        model = VideoType
        fields = ('name', 'abbreviation')
