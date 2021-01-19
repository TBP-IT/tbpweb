from chosen import forms as chosen_forms
from django import forms

from quark.base.fields import VisualDateWidget
from quark.base.forms import ChosenTermMixin
from quark.base.models import Term
from quark.project_reports.models import ProjectReport
from quark.user_profiles.fields import UserCommonNameChoiceField
from quark.user_profiles.fields import UserCommonNameMultipleChoiceField


class ProjectReportForm(ChosenTermMixin, forms.ModelForm):
    area = chosen_forms.ChosenChoiceField(
        choices=ProjectReport.PROJECT_AREA_CHOICES)
    author = UserCommonNameChoiceField()
    officer_list = UserCommonNameMultipleChoiceField(required=False)
    candidate_list = UserCommonNameMultipleChoiceField(required=False)
    member_list = UserCommonNameMultipleChoiceField(required=False)

    class Meta(object):
        model = ProjectReport
        exclude = ('first_completed_at', )
        widgets = {
            'date': VisualDateWidget(),
            'committee': chosen_forms.ChosenSelect()
        }


class ProjectReportBookExportForm(forms.Form):
    TERMS = Term.objects.filter(id__lte=Term.objects.get_current_term().id)
    TERM_CHOICES = [(term.id, term.verbose_name())
                    for term in TERMS.order_by('-id')]
    terms = forms.MultipleChoiceField(choices=TERM_CHOICES)
    presidents_letter = forms.CharField(
        widget=forms.Textarea, label='President\'s letter',
        help_text='Markdown format (do not use headers)')
