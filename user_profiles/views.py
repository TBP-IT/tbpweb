from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic import UpdateView

from quark.achievements.models import Achievement
from quark.base.models import Officer, Term
from quark.events.models import Event
from quark.quote_board.models import Quote
from quark.user_profiles.forms import UserProfileForm
from quark.user_profiles.forms import UserProfilePictureForm
from quark.user_profiles.models import UserProfile


class UserProfileDetailView(DetailView):
    context_object_name = 'profile'
    model = UserProfile
    template_name = 'user_profiles/detail.html'
    profile = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.profile = get_object_or_404(
            UserProfile, user__username=self.kwargs['username'])
        return super(UserProfileDetailView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        return self.profile

    def get_context_data(self, **kwargs):
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)
        college_student_info = self.profile.get_college_student_info()
        context['grad_term'] = college_student_info.grad_term.verbose_name()
        context['majors'] = college_student_info.major.all()

        status = 'Member'
        current_term = Term.objects.get_current_term()
        org_profile = self.profile.get_student_org_user_profile()
        if self.profile.is_candidate():
            status = 'Candidate'
        elif self.profile.is_officer(True):
            status = 'Officer'
            user_positions = org_profile.get_officer_positions(current_term)
            context['positions'] = user_positions
        context['status'] = status
        init_term = org_profile.initiation_term
        if init_term is not None:
            context['init_term'] = init_term.verbose_name()

        past_positions = Officer.objects.filter(
            user=self.profile.user, position__auxiliary=False,
            term__lt=current_term).select_related('position', 'term').order_by(
            '-term')
        context['past_positions'] = past_positions

        user_achievements = self.profile.user.userachievement_set.exclude(
            acquired=False).filter(
            achievement__privacy=Achievement.PRIVACY_PUBLIC).order_by('-term')
        user_points = 0
        for userachievement in user_achievements:
            user_points += userachievement.achievement.points
        context['user_points'] = user_points
        context['num_achievements'] = user_achievements.count()
        # displaying up to 5 most recent achievements
        context['achievements'] = user_achievements[:5]

        events = Event.objects.get_user_viewable(self.request.user).filter(
            cancelled=False).order_by('-end_datetime').select_related(
            'event_type')
        current_time = timezone.now()
        past_events = events.filter(end_datetime__lte=current_time)
        user_events = past_events.filter(
            eventattendance__user=self.profile.user)
        # displaying up to 20 most recent events attended
        context['events'] = user_events[:20]
        context['total_attendance'] = user_events.count()

        quotes = Quote.objects.filter(
            speakers__pk=self.profile.user.id).select_related(
            'submitter__userprofile').prefetch_related('speakers__userprofile')
        context['quotes'] = quotes[:3]

        return context


class UserProfileEditView(UpdateView):
    form_class = UserProfileForm
    success_url = reverse_lazy('user-profiles:edit')
    template_name = 'user_profiles/edit.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfileEditView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        return self.request.user.userprofile

    def form_valid(self, form):
        messages.success(self.request, 'Changes saved!')
        return super(UserProfileEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(UserProfileEditView, self).form_invalid(form)


class UserProfilePictureEditView(UserProfileEditView):
    form_class = UserProfilePictureForm
    success_url = reverse_lazy('user-profiles:edit-pic')
    template_name = 'user_profiles/edit_picture.html'
