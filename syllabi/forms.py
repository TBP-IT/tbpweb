from chosen import forms as chosen_forms
from django import forms
from django.db.models import Count
from django.utils.safestring import mark_safe

from quark.base.forms import ChosenTermMixin
from quark.courses.models import Course
from quark.courses.models import CourseInstance
from quark.courses.models import Department
from quark.courses.models import Instructor
from quark.syllabi.models import Syllabus
from quark.syllabi.models import SyllabusFlag
from quark.syllabi.models import InstructorSyllabusPermission
from quark.shortcuts import get_file_mimetype
from quark.shortcuts import get_object_or_none


class SyllabusForm(ChosenTermMixin, forms.ModelForm):
    """Used as a base for UploadForm and EditForm."""
    department = chosen_forms.ChosenModelChoiceField(
        queryset=Department.objects.all())
    course_number = forms.CharField()
    instructors = chosen_forms.ChosenModelMultipleChoiceField(
        queryset=Instructor.objects.all())

    course_instance = None  # set by set_course_instance
    syllabus_instructors = None  # set by set_course_instance

    class Meta(object):
        model = Syllabus
        fields = ()

    def __init__(self, *args, **kwargs):
        super(SyllabusForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'department', 'course_number', 'instructors', 'term']

    def set_course_instance(self, cleaned_data):
        """Check if a course is valid and whether a course instance exists
        with the exact instructors given, and create a course instance if one
        doesn't exist.
        """
        department = self.cleaned_data.get('department')
        course_number = self.cleaned_data.get('course_number')
        term = self.cleaned_data.get('term')

        course = get_object_or_none(
            Course, department=department, number=course_number)
        if not course:
            error_msg = '{department} {number} does not exist.'.format(
                department=department, number=course_number)
            self._errors['department'] = self.error_class([error_msg])
            self._errors['course_number'] = self.error_class([error_msg])
            raise forms.ValidationError('Invalid course')

        # check instructors to prevent trying to iterate over nothing
        self.syllabus_instructors = self.cleaned_data.get('instructors')
        if not self.syllabus_instructors:
            raise forms.ValidationError('Please fill out all fields.')

        course_instance = CourseInstance.objects.annotate(
            count=Count('instructors')).filter(
            count=len(self.syllabus_instructors),
            term=term,
            course=course)
        for instructor in self.syllabus_instructors:
            course_instance = course_instance.filter(instructors=instructor)
        if course_instance.exists():
            course_instance = course_instance.get()
        else:
            course_instance = CourseInstance.objects.create(
                term=term, course=course)
            course_instance.instructors.add(*self.syllabus_instructors)
            course_instance.save()
        self.course_instance = course_instance

    def save(self, *args, **kwargs):
        """Add a course instance to the syllabus."""
        self.instance.course_instance = self.course_instance
        return super(SyllabusForm, self).save(*args, **kwargs)


class UploadForm(SyllabusForm):
    # Remove the "Unknown" choice when uploading
    syllabus_file = forms.FileField(
        label='File (PDF only please)',
        widget=forms.FileInput(attrs={'accept': 'application/pdf'}))
    agreed = forms.BooleanField(required=True, label=mark_safe(
        'I agree, per campus policy on Course Note-Taking and Materials '
        '(available <a href="http://campuspol.chance.berkeley.edu/policies/'
        'coursenotes.pdf">here</a>), that I am allowed to upload '
        'this document.'))

    class Meta(SyllabusForm.Meta):
        fields = SyllabusForm.Meta.fields + ('syllabus_file',)

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder += ['syllabus_file', 'agreed']

    def clean_syllabus_file(self):
        """Check if uploaded syllabus file is of an acceptable format."""
        syllabus_file = self.cleaned_data.get('syllabus_file')
        if get_file_mimetype(syllabus_file) != 'application/pdf':
            raise forms.ValidationError('Uploaded file must be a PDF file.')
        return syllabus_file

    def clean(self):
        """Check if uploaded syllabus already exists."""
        cleaned_data = super(UploadForm, self).clean()
        self.set_course_instance(cleaned_data)
        duplicates = Syllabus.objects.filter(
            course_instance=self.course_instance)
        if duplicates.exists():
            raise forms.ValidationError(
                'This syllabus already exists in the database.')
        return cleaned_data

    def save(self, *args, **kwargs):
        """Check if professors are blacklisted."""
        for instructor in self.syllabus_instructors:
            permission = get_object_or_none(
                InstructorSyllabusPermission, instructor=instructor)
            if permission and permission.permission_allowed is False:
                self.instance.blacklisted = True
        return super(UploadForm, self).save(*args, **kwargs)


class EditForm(SyllabusForm):
    class Meta(SyllabusForm.Meta):
        fields = SyllabusForm.Meta.fields + ('verified',)

    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.fields['department'].initial = (
            self.instance.course_instance.course.department)
        self.fields['course_number'].initial = (
            self.instance.course_instance.course.number)
        self.fields['instructors'].initial = (
            self.instance.course_instance.instructors.all())
        self.fields['term'].initial = self.instance.course_instance.term
        self.fields.keyOrder += ['verified']

    def clean(self):
        """Check if an syllabus already exists with the new changes,
        excluding the current syllabus being edited.
        """
        cleaned_data = super(EditForm, self).clean()
        self.set_course_instance(cleaned_data)
        duplicates = Syllabus.objects.filter(
            course_instance=self.course_instance).exclude(
            pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError(
                'This syllabus already exists in the database. '
                'Please double check and delete as necessary.')
        return cleaned_data


class FlagForm(forms.ModelForm):
    class Meta(object):
        model = SyllabusFlag
        fields = ('reason',)


class FlagResolveForm(forms.ModelForm):
    class Meta(object):
        model = SyllabusFlag
        fields = ('resolution',)
