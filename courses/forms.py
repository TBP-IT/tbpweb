from chosen import forms as chosen_forms
from django import forms

from courses.models import Instructor
from courses.models import Course
from exams.models import InstructorPermission
from shortcuts import get_object_or_none


class InstructorForm(forms.ModelForm):
    class Meta(object):
        model = Instructor
        fields = '__all__'
        widgets = {
            'department': chosen_forms.ChosenSelect()
        }


class InstructorEditForm(InstructorForm):
    permission_allowed = forms.NullBooleanField(
        required=False,
        label='Permission allowed for exams',
        help_text='Has this instructor given permission to post exams?')
    correspondence = forms.CharField(
        widget=forms.Textarea, required=False,
        help_text=('Reason for why exam-posting permission was or was not '
                   'granted.'))

    permission = None

    def __init__(self, *args, **kwargs):
        super(InstructorEditForm, self).__init__(*args, **kwargs)
        self.permission = get_object_or_none(
            InstructorPermission, instructor=self.instance)
        if self.permission:
            self.fields['permission_allowed'].initial = (
                self.permission.permission_allowed)
            self.fields['correspondence'].initial = (
                self.permission.correspondence)

    def save(self, *args, **kwargs):
        permission_allowed = self.cleaned_data.get('permission_allowed')
        if permission_allowed is not None:
            if not self.permission:
                self.permission = InstructorPermission(
                    instructor=self.instance)
            self.permission.permission_allowed = permission_allowed
            self.permission.correspondence = self.cleaned_data.get(
                'correspondence')
            self.permission.save()
        return super(InstructorEditForm, self).save(*args, **kwargs)


class CourseForm(forms.ModelForm):
    class Meta(object):
        model = Course
        fields = '__all__'
        widgets = {
            'department': chosen_forms.ChosenSelect()
        }


class CourseEditForm(CourseForm):

    # permission_allowed = forms.NullBooleanField(
    #     required=False,
    #     label='Permission allowed for exams',
    #     help_text='Has this instructor given permission to post exams?')
    # correspondence = forms.CharField(
    #     widget=forms.Textarea, required=False,
    #     help_text=('Reason for why exam-posting permission was or was not '
    #                'granted.'))

    permission = None

    def __init__(self, *args, **kwargs):
        super(CourseEditForm, self).__init__(*args, **kwargs)
        # self.permission = get_object_or_none(
        #     InstructorPermission, instructor=self.instance)
        # if self.permission:
        #     self.fields['permission_allowed'].initial = (
        #         self.permission.permission_allowed)
        #     self.fields['correspondence'].initial = (
        #         self.permission.correspondence)

    def save(self, *args, **kwargs):
        # permission_allowed = self.cleaned_data.get('permission_allowed')
        # if permission_allowed is not None:
        #     if not self.permission:
        #         self.permission = InstructorPermission(
        #             instructor=self.instance)
        #     self.permission.permission_allowed = permission_allowed
        #     self.permission.correspondence = self.cleaned_data.get(
        #         'correspondence')
        #     self.permission.save()
        return super(CourseEditForm, self).save(*args, **kwargs)
