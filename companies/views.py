import datetime
import os
import StringIO
import zipfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ValidationError
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from quark.accounts.forms import PasswordResetForm
from quark.base.models import Major
from quark.companies.forms import CompanyFormWithExpiration
from quark.companies.forms import CompanyRepCreationForm
from quark.companies.models import Company
from quark.companies.models import CompanyRep
from quark.resumes.models import Resume
from quark.user_profiles.models import UserProfile


class IndustryLandingView(TemplateView):
    """Landing page for industry companies."""
    template_name = 'companies/landing.html'


class CompanyListView(ListView):
    """List all the companies that have accounts."""
    context_object_name = 'companies'
    model = Company
    template_name = 'companies/list.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('companies.view_companies', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyListView, self).dispatch(*args, **kwargs)


class CompanyDetailView(DetailView):
    """Show details for a company and its representatives."""
    model = Company
    pk_url_kwarg = 'company_pk'
    template_name = 'companies/detail.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('companies.change_company', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CompanyDetailView, self).get_context_data(**kwargs)
        context['reps'] = CompanyRep.objects.select_related('user').filter(
            company=self.object)
        return context


class CompanyCreateView(CreateView):
    """View for creating a new company profile."""
    form_class = CompanyFormWithExpiration
    success_url = reverse_lazy('companies:list')
    template_name = 'companies/create_company.html'
    object = None

    @method_decorator(login_required)
    @method_decorator(
        permission_required('companies.add_company', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        company = form.cleaned_data['name']
        msg = 'Successfully registered {}.'.format(company)
        messages.success(self.request, msg)
        return super(CompanyCreateView, self).form_valid(form)


class CompanyEditView(UpdateView):
    model = Company
    pk_url_kwarg = 'company_pk'
    success_url = reverse_lazy('companies:list')
    template_name = 'companies/edit.html'
    form_class = CompanyFormWithExpiration

    @method_decorator(login_required)
    @method_decorator(
        permission_required('companies.change_company', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyEditView, self).dispatch(*args, **kwargs)


class CompanyRepCreateView(CreateView):
    """View for creating a new account for a company representative.

    Upon successful completion of the creation form, an email is sent to the
    company representative to allow them to set the password for their account.
    """
    form_class = CompanyRepCreationForm
    # TODO(ehy): redirect to detail page, not to list page
    success_url = reverse_lazy('companies:list')
    template_name = 'companies/create_rep.html'
    object = None  # The User account created for the rep

    @method_decorator(login_required)
    @method_decorator(
        permission_required('companies.add_companyrep', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyRepCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()

        # Make sure the company rep has a user profile
        try:
            self.object.userprofile
        except UserProfile.DoesNotExist:
            UserProfile(user=self.object).save()

        username = self.object.get_username()
        company = form.cleaned_data['company']
        msg = ('Successfully created a new company rep account with the '
               'username {} for the company {}.'.format(username, company))
        messages.success(self.request, msg)

        # Use a password reset form to send the new company rep a password
        # reset email, so that they can choose their own password and log in
        pw_reset_form = PasswordResetForm({'username_or_email': username})
        if pw_reset_form.is_valid():
            email_template = 'accounts/password_set_initial_email.html'
            subject_template = 'accounts/password_set_initial_subject.txt'
            pw_reset_form.save(
                email_template_name=email_template,
                subject_template_name=subject_template)
        else:
            # Throw an error and log the form data and errors, since something
            # is wrong.
            error_msg = (
                u'Failed to send new company rep their password reset email. \n'
                'Form data: {data} \nForm Errors: {errors}'.format(
                    data=pw_reset_form.data,
                    errors=pw_reset_form.errors.items())
            )
            raise ValidationError(error_msg)
        return HttpResponseRedirect(self.get_success_url())


class CompanyRepDeleteView(DeleteView):
    """View for deleting a company representative."""
    model = CompanyRep
    pk_url_kwarg = 'rep_pk'
    context_object_name = 'rep'
    template_name = 'companies/delete_rep.html'

    def get_success_url(self):
        return reverse_lazy(
            'companies:company-detail',
            args=(self.get_object().company.pk,))

    @method_decorator(login_required)
    @method_decorator(
        permission_required(
            'companies.delete_companyrep', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CompanyRepDeleteView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        rep = self.get_object()
        rep.user.is_active = False
        rep.user.save()
        msg = 'Successfully deleted representative "{}".'.format(
            rep.user.get_full_name())
        messages.success(request, msg)
        return super(CompanyRepDeleteView, self).post(
            request, *args, **kwargs)


class ResumeListView(ListView):
    context_object_name = 'resumes'
    template_name = 'companies/resumes.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('resumes.view_resumes', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ResumeListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # TODO(ehy): get resumes from the past two semesters instead of
        # from the past year
        one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
        return Resume.objects.filter(
            verified=True, updated__gt=one_year_ago).select_related(
            'user__userprofile', 'user__collegestudentinfo',
            'user__collegestudentinfo__grad_term').prefetch_related(
            'user__collegestudentinfo__major').order_by('-updated')


class ResumeZipView(DetailView):
    model = Resume

    @method_decorator(login_required)
    @method_decorator(
        permission_required('resumes.view_resumes', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ResumeZipView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
        zip_path = os.path.join(settings.MEDIA_ROOT, 'resumes/resumes.zip')
        resumes = Resume.objects.filter(verified=True, updated__gt=one_year_ago)

        # Check if cached zip file is at least newer than the latest resume
        if os.path.exists(zip_path):
            creation_time = os.path.getctime(zip_path)
            zip_ctime = datetime.datetime.fromtimestamp(creation_time)
            latest_resume = max(resumes, key=lambda resume: resume.updated)
            if latest_resume.updated.replace(tzinfo=None) < zip_ctime:
                response = HttpResponse(FileWrapper(open(zip_path, 'r')),
                                        content_type='application/zip')
                response['Content-Disposition'] = 'attachment; \
                                                   filename=resumes.zip'
                return response

        # Generate a new zip file with updated resumes
        s_buffer = StringIO.StringIO()
        zip_file = zipfile.ZipFile(s_buffer, 'w')

        for major in Major.objects.all():
            major_resumes = resumes.filter(
                user__collegestudentinfo__major=major).select_related(
                    'user__userprofile', 'user__collegestudentinfo')
            resume_users_seen = dict()
            for resume in major_resumes:
                if resume.resume_file:
                    name_term = '{} {}'.format(
                        resume.user.userprofile.get_full_name(
                            include_middle_name=False),
                        resume.user.collegestudentinfo.grad_term)

                    # Check and account for matching file names
                    num_matching_filenames = resume_users_seen.get(name_term, 0)
                    if num_matching_filenames > 0:
                        zip_file.write(resume.resume_file.path,
                                       '{}/{} ({}).pdf'.format(
                                           major.short_name, name_term,
                                           num_matching_filenames))
                    else:
                        zip_file.write(resume.resume_file.path,
                                       major.short_name + '/' +
                                       name_term + '.pdf')
                    resume_users_seen[name_term] = num_matching_filenames + 1
        zip_file.close()

        # Write out newly generated zip file into resumes media directory
        with open(zip_path, 'w') as resumes_zip:
            resumes_zip.write(s_buffer.getvalue())
        response = HttpResponse(s_buffer.getvalue(),
                                content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=resumes.zip'
        return response
