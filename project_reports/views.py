from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.base import View

from quark.base.models import Term
from quark.base.views import TermParameterMixin
from quark.project_reports.forms import ProjectReportForm
from quark.project_reports.forms import ProjectReportBookExportForm
from quark.project_reports.models import ProjectReport
from quark.project_reports.models import ProjectReportBook

from datetime import date
from markdown import markdown
import multiprocessing
import tblib.pickling_support

tblib.pickling_support.install()


class ProjectReportCreateView(CreateView):
    form_class = ProjectReportForm
    success_url = reverse_lazy('project_reports:list')
    template_name = 'project_reports/add.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('project_reports.add_projectreport',
                            raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProjectReportCreateView, self).dispatch(
            *args, **kwargs)

    def get_initial(self):
        current_term = Term.objects.get_current_term()
        return {'author': self.request.user,  # usable since login_required
                'term': current_term.id if current_term else None}


class ProjectReportDeleteView(DeleteView):
    context_object_name = 'project_report'
    model = ProjectReport
    pk_url_kwarg = 'pr_pk'
    success_url = reverse_lazy('project_reports:list')
    template_name = 'project_reports/delete.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('project_reports.delete_projectreport',
                            raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProjectReportDeleteView, self).dispatch(
            *args, **kwargs)


class ProjectReportDetailView(DetailView):
    context_object_name = 'project_report'
    model = ProjectReport
    pk_url_kwarg = 'pr_pk'
    template_name = 'project_reports/detail.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('project_reports.view_project_reports',
                            raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProjectReportDetailView, self).dispatch(
            *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProjectReportDetailView, self).get_context_data(
            **kwargs)

        context['description_html'] = markdown(
            context['project_report'].description)
        context['purpose_html'] = markdown(
            context['project_report'].purpose)
        context['organization_html'] = markdown(
            context['project_report'].organization)
        context['cost_html'] = markdown(
            context['project_report'].cost)
        context['problems_html'] = markdown(
            context['project_report'].problems)
        context['results_html'] = markdown(
            context['project_report'].results)

        return context


class ProjectReportEditView(UpdateView):
    context_object_name = 'project_report'
    form_class = ProjectReportForm
    model = ProjectReport
    pk_url_kwarg = 'pr_pk'
    template_name = 'project_reports/edit.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        author = ProjectReport.objects.get(id=self.kwargs['pr_pk']).author
        perm1 = self.request.user.has_perm(
            'project_reports.change_projectreport')
        perm2 = author == self.request.user
        if not (perm1 or perm2):
            raise PermissionDenied
        return super(ProjectReportEditView, self).dispatch(
            *args, **kwargs)


class ProjectReportListView(TermParameterMixin, ListView):
    """View for showing all project reports from a given term.

    Term is specified via URL parameter, using the TermParameterMixin.
    """
    context_object_name = 'project_reports'
    template_name = 'project_reports/list.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('project_reports.view_project_reports',
                            raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProjectReportListView, self).dispatch(
            *args, **kwargs)

    def get_queryset(self):
        return ProjectReport.objects.filter(
            term=self.display_term).select_related(
            'author__userprofile', 'committee')

    def get_context_data(self, **kwargs):
        context = super(ProjectReportListView, self).get_context_data(**kwargs)

        finished_project_reports = ProjectReport.objects.filter(
            term=self.display_term, complete=True)
        context['num_finished_prs'] = finished_project_reports.count()
        context['total_word_count'] = 0
        for project_report in finished_project_reports:
            context['total_word_count'] += project_report.word_count()

        context['num_due_prs'] = ProjectReport.objects.filter(
            term=self.display_term, date__lt=date.today()).count()

        return context


class ProjectReportListAllView(ListView):
    """View for showing all project reports from all terms."""
    context_object_name = 'project_reports'
    model = ProjectReport
    template_name = 'project_reports/list.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('project_reports.view_project_reports',
                            raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProjectReportListAllView, self).dispatch(
            *args, **kwargs)


class ProjectReportBookExportView(FormView):
    form_class = ProjectReportBookExportForm
    template_name = 'project_reports/export_book.html'

    def __init__(self, *args, **kwargs):
        self.pr_book = None
        super(ProjectReportBookExportView, self).__init__(
            *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectReportBookExportView, self).dispatch(
            *args, **kwargs)

    def form_valid(self, form):
        terms = [Term.objects.get(id=pk) for pk in form.cleaned_data['terms']]
        self.pr_book = ProjectReportBook(
            user=self.request.user,
            presidents_letter=form.cleaned_data['presidents_letter'])
        self.pr_book.save()
        self.pr_book.terms.add(*terms)

        def command():
            from django.db import connection
            connection.close()
            call_command('generate_pr_book', self.pr_book.id)

        multiprocessing.Process(target=command).start()

        return super(ProjectReportBookExportView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project_reports:download-book',
                            kwargs={'book_pk': self.pr_book.id})


class ProjectReportBookDownloadView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectReportBookDownloadView, self).dispatch(
            *args, **kwargs)

    def get(self, request, *args, **kwargs):
        book_pk = kwargs.pop('book_pk')
        pr_book = ProjectReportBook.objects.get(id=book_pk)
        if pr_book.exception:
            # Re-raise the delayed exception from the failed subprocess
            pr_book.exception.re_raise()
        elif not pr_book.pdf:
            return render(request, 'project_reports/download_book.html', {})
        else:
            response = HttpResponse(
                pr_book.pdf,
                content_type='application/pdf')
            response['Content-Disposition'] = \
                'attachment; filename=book{}.pdf'.format(book_pk)
            return response
