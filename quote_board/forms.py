from django import forms

from tbpweb.quote_board.models import Quote
from tbpweb.user_profiles.fields import UserCommonNameMultipleChoiceField


class QuoteForm(forms.ModelForm):
    speakers = UserCommonNameMultipleChoiceField()

    class Meta(object):
        model = Quote
        exclude = ('submitter',)
