from django import forms

from quark.newsreel.models import News


class NewsForm(forms.ModelForm):
    class Meta(object):
        model = News
        fields = ('title', 'blurb', 'image')

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields['image'].required = False
