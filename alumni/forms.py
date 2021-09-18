from chosen import forms as chosen_forms
from django import forms
from alumni.models import Alumnus


class AlumnusForm(forms.ModelForm):
    class Meta(object):
        model = Alumnus
        fields = '__all__'
        widgets = {
            'user': chosen_forms.ChosenSelect()
        }


class AlumnusEditForm(AlumnusForm):
    def __init__(self, *args, **kwargs):
        super(AlumnusEditForm, self).__init__(*args, **kwargs)
