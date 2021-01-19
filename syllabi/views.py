import mimetypes

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_bytes
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from quark.syllabi.forms import EditForm
from quark.syllabi.forms import FlagForm
from quark.syllabi.forms import FlagResolveForm
from quark.syllabi.forms import UploadForm
from quark.syllabi.models import Syllabus
from quark.syllabi.models import SyllabusFlag
from quark.syllabi.models import InstructorSyllabusPermission


class SyllabusUploadView(CreateView):
    form_class = UploadForm
    template_name = 'syllabi/upload.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SyllabusUploadView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """Assign submitter to the syllabus."""
        form.instance.submitter = self.request.user
        messages.success(
            self.request, 'Syllabus uploaded! It will need to verified first '
            'before it becomes visible to everyone.')
        return super(SyllabusUploadView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(SyllabusUploadView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('courses:course-department-list')


class SyllabusDownloadView(DetailView):
    """View for downloading syllabi."""
    model = Syllabus
    object = None
    pk_url_kwarg = 'syllabus_pk'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # If the syllabus is not approved, check whether the user has permission
        # to view it. If not, raise a 404 instead of PermissionDenied because
        # the syllabus is not supposed to "exist" if it is not approved.
        if (not self.object.is_approved()
                and not self.request.user.has_perm('syllabi.view_all_syllabi')):
            raise Http404

        mime_type, _ = mimetypes.guess_type(self.object.syllabus_file.name)
        response = HttpResponse(
            FileWrapper(self.object.syllabus_file),
            content_type=mime_type)
        response['Content-Disposition'] = 'inline;filename="{syllabus}"'.format(
            syllabus=smart_bytes(
                self.object.get_download_file_name(), encoding='ascii'))
        return response


class SyllabusReviewListView(ListView):
    """Show all syllabi that are unverified or have flags."""
    context_object_name = 'syllabi'
    template_name = 'syllabi/review.html'
    flagged_syllabi = None
    unverified_syllabi = None

    @method_decorator(login_required)
    @method_decorator(
        permission_required('syllabi.change_syllabus', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        non_blacklisted_syllabi = Syllabus.objects.filter(blacklisted=False)
        self.unverified_syllabi = non_blacklisted_syllabi.filter(verified=False)
        self.flagged_syllabi = non_blacklisted_syllabi.filter(flags__gt=0)
        return super(SyllabusReviewListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return (self.unverified_syllabi | self.flagged_syllabi).select_related(
            'course_instance__term',
            'course_instance__course__department').prefetch_related(
            'course_instance__instructors')

    def get_context_data(self, **kwargs):
        context = super(SyllabusReviewListView, self).get_context_data(**kwargs)
        context['unverified_syllabus_count'] = self.unverified_syllabi.count()
        context['flagged_syllabus_count'] = self.flagged_syllabi.count()
        context['blacklisted_syllabi'] = Syllabus.objects.filter(
            blacklisted=True).select_related(
            'course_instance__term',
            'course_instance__course__department').prefetch_related(
            'course_instance__instructors')
        return context


class SyllabusEditView(UpdateView):
    form_class = EditForm
    context_object_name = 'syllabus'
    template_name = 'syllabi/edit.html'
    syllabus = None

    @method_decorator(login_required)
    @method_decorator(
        permission_required('syllabi.change_syllabus', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        self.syllabus = get_object_or_404(Syllabus,
                                          pk=self.kwargs['syllabus_pk'])
        return super(SyllabusEditView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return self.syllabus

    def get_context_data(self, **kwargs):
        context = super(SyllabusEditView, self).get_context_data(**kwargs)
        context['flags'] = SyllabusFlag.objects.filter(syllabus=self.syllabus)
        context['permissions'] = InstructorSyllabusPermission.objects.filter(
            instructor__in=self.syllabus.instructors)
        context['is_pdf'] = mimetypes.guess_type(
            self.object.syllabus_file.name)[0] == 'application/pdf'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Changes saved!')
        return super(SyllabusEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(SyllabusEditView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('syllabi:edit', kwargs={'syllabus_pk': self.syllabus.pk})


class SyllabusDeleteView(DeleteView):
    context_object_name = 'syllabi'
    model = Syllabus
    pk_url_kwarg = 'syllabus_pk'
    template_name = 'syllabi/delete.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('syllabi.delete_syllabus', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SyllabusDeleteView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Syllabus deleted!')
        return super(SyllabusDeleteView, self).form_valid(form)

    def get_success_url(self):
        return reverse('syllabi:review')


class SyllabusFlagCreateView(CreateView):
    form_class = FlagForm
    template_name = 'syllabi/flag.html'
    syllabus = None

    def dispatch(self, *args, **kwargs):
        self.syllabus = get_object_or_404(Syllabus,
                                          pk=self.kwargs['syllabus_pk'])
        return super(SyllabusFlagCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SyllabusFlagCreateView, self).get_context_data(**kwargs)
        context['syllabus'] = self.syllabus
        return context

    def form_valid(self, form):
        """Flag syllabus if valid data is posted."""
        form.instance.syllabus = self.syllabus
        messages.success(self.request, 'Syllabus flag created!')
        return super(SyllabusFlagCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(SyllabusFlagCreateView, self).form_invalid(form)

    def get_success_url(self):
        """Go to the course page corresponding to the flagged syllabus."""
        slug = self.syllabus.course.department.slug
        return reverse('courses:course-detail',
                       kwargs={'dept_slug': slug,
                               'course_num': self.syllabus.course.number})


class SyllabusFlagResolveView(UpdateView):
    form_class = FlagResolveForm
    context_object_name = 'flag'
    model = SyllabusFlag
    object = None
    pk_url_kwarg = 'flag_pk'
    template_name = 'syllabi/resolve.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('syllabi.change_syllabusflag',
                            raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(SyllabusFlagResolveView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.object = self.get_object()  # get the flag object

        # If the syllabus pk provided in the URL doesn't match the syllabus
        # for which this flag is addressing, redirect
        # to the proper address for the flag
        if self.kwargs['syllabus_pk'] != str(self.object.syllabus.pk):
            return redirect('syllabi:flag-resolve',
                            syllabus_pk=self.object.syllabus.pk,
                            flag_pk=self.object.pk)
        else:
            return super(SyllabusFlagResolveView, self).get(self,
                                                            *args, **kwargs)

    def form_valid(self, form):
        """Resolve flag if valid data is posted."""
        form.instance.resolved = True
        messages.success(self.request, 'Syllabus flag resolved!')
        return super(SyllabusFlagResolveView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(SyllabusFlagResolveView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('syllabi:edit',
                       kwargs={'syllabus_pk': self.kwargs['syllabus_pk']})
