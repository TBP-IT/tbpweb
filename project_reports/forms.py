from chosen import forms as chosen_forms
from django import forms

from base.fields import VisualDateWidget
from base.forms import ChosenTermMixin
from base.models import Term
from project_reports.models import ProjectReport
from user_profiles.fields import UserCommonNameChoiceField
from user_profiles.fields import UserCommonNameMultipleChoiceField


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
    terms = forms.MultipleChoiceField(choices=[(-1, "EMPTY")])
    presidents_letter = forms.CharField(
        widget=forms.Textarea, label='President\'s letter',
        help_text='Markdown format (do not use headers)')
    
    def __init__(self, *args, **kwargs):
        super(ProjectReportBookExportForm, self).__init__(*args, **kwargs)
        self.fields['terms'].choices = self.get_term_choices()
        
    
    def get_term_choices(self):
        before_and_current_terms = Term.objects.filter(id__lte=Term.objects.get_current_term().id).order_by('-id')
        return [(term.id, term.verbose_name()) for term in before_and_current_terms]
