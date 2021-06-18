from django import forms

from quote_board.models import Quote
from user_profiles.fields import UserCommonNameMultipleChoiceField


class QuoteForm(forms.ModelForm):
    speakers = UserCommonNameMultipleChoiceField()

    class Meta(object):
        model = Quote
        exclude = ('submitter',)
