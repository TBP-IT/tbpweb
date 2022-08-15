from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.forms import HiddenInput
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import UpdateView

from alumni.forms import AlumnusForm
from alumni.forms import AlumnusEditForm
from alumni.models import Alumnus
from alumni.models import DiscussionTopic
from alumni.models import TimeInvestment
from base.models import Major


class AlumnusListView(ListView):
    context_object_name = 'alumni'
    template_name = 'alumni/list.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('alumni.view_alumnus', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(AlumnusListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Alumnus.objects.select_related(
            'user__userprofile', 'user__collegestudentinfo').prefetch_related(
            'discussion_topics', 'user__collegestudentinfo__major',
            'user__collegestudentinfo__grad_term')

    def get_context_data(self, **kwargs):
        context = super(AlumnusListView, self).get_context_data(**kwargs)
        context['discussion_topics'] = DiscussionTopic.objects.all()
        context['majors'] = Major.objects.all()
        context['time_investment'] = TimeInvestment.objects.all()
        return context


class AlumnusCreateView(CreateView):
    form_class = AlumnusForm
    template_name = 'alumni/add_alumnus.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('alumni.add_alumnus', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(AlumnusCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Alumnus added!')
        return super(AlumnusCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(AlumnusCreateView, self).form_invalid(form)


class AlumnusEditView(UpdateView):
    context_object_name = 'alumnus'
    form_class = AlumnusEditForm
    model = Alumnus
    pk_url_kwarg = 'alum_pk'
    template_name = 'alumni/edit_alumnus.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        alumnus_user = Alumnus.objects.get(id=self.kwargs['alum_pk']).user
        edit_permission = self.request.user.has_perm('alumni.change_alumnus')
        if not (alumnus_user == self.request.user or edit_permission):
            raise PermissionDenied
        return super(AlumnusEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Changes saved!')
        return super(AlumnusEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(AlumnusEditView, self).form_invalid(form)

    def get_form(self, form_class=form_class):
        form = super(AlumnusEditView, self).get_form(form_class)
        form.fields['user'].widget = HiddenInput()
        return form
