import collections
import csv
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic.base import ContextMixin
from django.views.generic.base import TemplateView
from django.views.generic.base import View
from django.views.generic.edit import FormView

from base.models import Term
from base.views import TermParameterMixin
from candidates.models import Candidate, CandidateRequirement, CandidateRequirementProgress, Challenge, \
                              ChallengeType, ChallengeCandidateRequirement, EventCandidateRequirement, \
                              ExamFileCandidateRequirement, ManualCandidateRequirement, \
                              ResumeCandidateRequirement, SyllabusCandidateRequirement
from candidates.forms import CandidateCreationForm
from candidates.forms import CandidateUserProfileForm
from candidates.forms import CandidatePhotoForm
from candidates.forms import CandidateRequirementProgressFormSet
from candidates.forms import CandidateRequirementFormSet
from candidates.forms import ChallengeForm
from candidates.forms import ChallengeVerifyFormSet
from candidates.forms import ManualCandidateRequirementForm
from events.models import Event
from events.models import EventType
from exams.models import Exam
from houses.models import House
from notifications.models import Notification
from resumes.models import Resume
from syllabi.models import Syllabus
from shortcuts import get_object_or_none
from user_profiles.models import UserProfile
from utils.ajax import json_response


class CandidateContextMixin(ContextMixin):
    """Mixin for getting the candidate, events, challenges, and exams for
    the context dictionary. Used in candidate management and candidate portal.
    """
    # pylint: disable=R0914
    def get_context_data(self, **kwargs):
        context = super(CandidateContextMixin, self).get_context_data(**kwargs)
        candidate = kwargs.get('candidate')
        context['candidate'] = candidate

        attended_events_by_type = collections.defaultdict(list)
        past_signup_events_by_type = collections.defaultdict(list)
        future_signup_events_by_type = collections.defaultdict(list)
        attended_elective_events = []
        future_signup_elective_events = []

        attended_events = Event.objects.select_related(
            'event_type').filter(
            eventattendance__user=candidate.user,
            term=candidate.term,
            cancelled=False)
        for event in attended_events:
            attended_events_by_type[event.event_type.name].append(event)

        signup_events = Event.objects.select_related(
            'event_type').filter(
            eventsignup__user=candidate.user,
            eventsignup__unsignup=False,
            term=candidate.term,
            cancelled=False).exclude(
            pk__in=attended_events.values_list('pk', flat=True))

        current_time = timezone.now()
        past_signup_events = signup_events.filter(
            end_datetime__lte=current_time)
        future_signup_events = signup_events.filter(
            end_datetime__gt=current_time)

        for event in past_signup_events:
            past_signup_events_by_type[event.event_type.name].append(event)

        for event in future_signup_events:
            future_signup_events_by_type[event.event_type.name].append(event)

        event_reqs = CandidateRequirement.objects.filter(
            term=candidate.term,
            requirement_type=CandidateRequirement.EVENT)
        try:
            elective_req = event_reqs.get(
                eventcandidaterequirement__event_type__name='Elective')
        except CandidateRequirement.DoesNotExist:
            elective_req = None

        # If at least 1 elective event is required and the candidate has
        # attended at least the required amount of events for an event type,
        # extra events will count as elective events. Any future sign ups will
        # also be displayed under elective events instead of that event type.
        if (elective_req and
                elective_req.get_progress(candidate)['required'] > 0):
            for event_req in event_reqs:
                req_progress = event_req.get_progress(candidate)
                event_type = event_req.eventcandidaterequirement.event_type
                extra = req_progress['completed'] - req_progress['required']
                if extra >= 0 and event_type.eligible_elective:
                    attended_elective_events += attended_events_by_type[
                        event_type.name][req_progress['required']:]
                    attended_events_by_type[
                        event_type.name] = attended_events_by_type[
                        event_type.name][:req_progress['required']]
                    future_signup_elective_events += (
                        future_signup_events_by_type[event_type.name])
                    future_signup_events_by_type[event_type.name] = []

        # Count events that are eligible as electives that don't have any
        # requirements
        non_required_event_types = EventType.objects.filter(
            eligible_elective=True).exclude(
            eventcandidaterequirement__pk__in=event_reqs.values_list(
                'pk', flat=True))
        attended_elective_events += list(attended_events.filter(
            event_type__in=non_required_event_types))
        future_signup_elective_events += list(future_signup_events.filter(
            event_type__in=non_required_event_types))

        context['attended_events'] = attended_events_by_type
        context['past_signup_events'] = past_signup_events_by_type
        context['future_signup_events'] = future_signup_events_by_type
        context['attended_elective_events'] = attended_elective_events
        context['future_signup_elective_events'] = future_signup_elective_events

        requested_challenges = {}
        challenge_types = ChallengeType.objects.values_list('name', flat=True)
        for challenge_type in challenge_types:
            requested_challenges[challenge_type] = []
        challenges = Challenge.objects.select_related(
            'challenge_type', 'verifying_user__userprofile').filter(
            candidate=candidate)
        for challenge in challenges:
            requested_challenges[challenge.challenge_type.name].append(
                challenge)
        context['challenges'] = requested_challenges

        approved_exams = Exam.objects.get_approved().filter(
            submitter=candidate.user)
        context['approved_exams'] = approved_exams
        approved_exam_pks = [exam.pk for exam in approved_exams]
        unapproved_exams = Exam.objects.filter(
            submitter=candidate.user).exclude(pk__in=approved_exam_pks)
        context['unverified_exams'] = unapproved_exams.filter(verified=False,
                                                              blacklisted=False)
        context['blacklisted_exams'] = unapproved_exams.filter(
            blacklisted=True)

        approved_syllabi = Syllabus.objects.get_approved().filter(
            submitter=candidate.user)
        context['approved_syllabi'] = approved_syllabi
        approved_syllabus_pks = [syllabus.pk for syllabus in approved_syllabi]
        unapproved_syllabi = Syllabus.objects.filter(
            submitter=candidate.user).exclude(pk__in=approved_syllabus_pks)
        context['unverified_syllabi'] = unapproved_syllabi.filter(
            verified=False, blacklisted=False)
        context['blacklisted_syllabi'] = unapproved_syllabi.filter(
            blacklisted=True)

        try:
            context['resume_status'] = Resume.objects.get(
                user=candidate.user).get_verified_display()
        except Resume.DoesNotExist:
            context['resume_status'] = 'Not uploaded'

        return context


class CandidateListView(TermParameterMixin, ListView):
    context_object_name = 'candidates'
    template_name = 'candidates/list.html'

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.change_candidate', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CandidateListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Candidate.objects.filter(term=self.display_term).select_related(
            'user__userprofile', 'user__collegestudentinfo').prefetch_related(
            'user__collegestudentinfo__major')


class CandidatePhotoView(UpdateView):
    context_object_name = 'candidate'
    form_class = CandidatePhotoForm
    model = Candidate
    pk_url_kwarg = 'candidate_pk'
    template_name = 'candidates/photo.html'

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.change_candidate', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CandidatePhotoView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Candidate photo uploaded!')
        return super(CandidatePhotoView, self).form_valid(form)

    def get_success_url(self):
        return reverse('candidates:edit',
                       kwargs={'candidate_pk': self.object.pk})


class CandidateCreateView(TemplateView):
    """View for adding a new candidate. Inherits from TemplateView rather than
    CreateView because two forms (CandidateCreationForm and
    CandidateUserProfileForm) are being mixed together."""

    template_name = 'candidates/create.html'
    success_url = reverse_lazy('candidates:list')
    object = None  # The new Candidate object

    def get_fields(self, cand_form, userprofile_form):
        """The User and UserProfile forms both have name and email fields, and
        we want those fields to be grouped together, so we need to manually
        order them."""
        initial_fields = [cand_form['username'], cand_form['email'],
                          userprofile_form['alt_email'],
                          cand_form['password1'], cand_form['password2'],
                          cand_form['first_name'],
                          userprofile_form['preferred_name'],
                          userprofile_form['middle_name'],
                          cand_form['last_name']]

        excluded_fields = ['alt_email', 'preferred_name', 'middle_name']

        final_fields = [userprofile_form[field] for field in
                        userprofile_form.fields if field not in
                        excluded_fields]

        return initial_fields + final_fields

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.add_candidate', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CandidateCreateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        cand_form = CandidateCreationForm()
        userprofile_form = CandidateUserProfileForm()
        return self.render_to_response(self.get_context_data(
            cand_form=cand_form, userprofile_form=userprofile_form,
            form_fields=self.get_fields(cand_form, userprofile_form)))

    def post(self, request, *args, **kwargs):
        cand_form = CandidateCreationForm(self.request.POST)
        userprofile_form = CandidateUserProfileForm(self.request.POST)
        if cand_form.is_valid() and userprofile_form.is_valid():
            # The CandidateUserProfileForm needs to be remade with the same
            # data, but with the new user's UserProfile as its instance
            return self.form_valid(cand_form, self.request.POST)
        else:
            return self.form_invalid(cand_form, userprofile_form)

    def form_valid(self, cand_form, post_data):
        self.object = cand_form.save()
        try:
            userprofile_form = CandidateUserProfileForm(
                post_data, instance=self.object.user.userprofile)
        except UserProfile.DoesNotExist:
            UserProfile(user=self.object.user).save()
            userprofile_form = CandidateUserProfileForm(
                post_data, instance=self.object.user.userprofile)

        # pylint: disable=E1103
        userprofile_form.is_valid()
        userprofile_form.save()

        cand_name = self.object.user.userprofile.get_full_name()
        msg = 'Successfully registered the candidate {}.'.format(cand_name)
        messages.success(self.request, msg)
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, cand_form, userprofile_form):
        return self.render_to_response(self.get_context_data(
            cand_form=cand_form, userprofile_form=userprofile_form,
            form_fields=self.get_fields(cand_form, userprofile_form)))


class CandidateEditView(FormView, CandidateContextMixin):
    form_class = CandidateRequirementProgressFormSet
    template_name = 'candidates/edit.html'
    candidate = None
    progress_list = None
    requirements = None

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.change_candidate', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        self.candidate = get_object_or_404(
            Candidate, pk=self.kwargs['candidate_pk'])
        self.requirements = CandidateRequirement.objects.filter(
            term=self.candidate.term).select_related(
            'eventcandidaterequirement',
            'eventcandidaterequirement__event_type',
            'challengecandidaterequirement',
            'challengecandidaterequirement__challenge_type',
            'examfilecandidaterequirement')

        # Create a list of progresses that at each index contains either a
        # progress corresponding to a requirement or None if there is no
        # progress for the corresponding requirement
        self.progress_list = []
        progress_index = 0

        progresses = CandidateRequirementProgress.objects.filter(
            candidate=self.candidate)
        num_progresses = progresses.count()

        for req in self.requirements:
            # Progresses are ordered the same way as requirements,
            # so all progresses will be correctly checked in the loop
            if progress_index < num_progresses:
                progress = progresses[progress_index]
                if progress.requirement == req:
                    self.progress_list.append(progress)
                    progress_index += 1
                    continue
            self.progress_list.append(None)

        return super(CandidateEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        """Set the term in the form."""
        kwargs = super(CandidateEditView, self).get_form_kwargs(**kwargs)
        kwargs['candidate_term'] = self.candidate.term
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['candidate'] = self.candidate
        context = super(CandidateEditView, self).get_context_data(**kwargs)
        formset = self.get_form(self.form_class)

        upcoming_events = Event.objects.get_upcoming()

        remaining = collections.Counter()
        for event in upcoming_events:
            remaining[event.event_type.name] += 1

        # Initialize req_types to contain lists for every requirement type
        req_types = {}
        for req in CandidateRequirement.REQUIREMENT_TYPE_CHOICES:
            req_types[req[0]] = []

        for i, req in enumerate(self.requirements):
            progress = self.progress_list[i]
            form = formset[i]
            req_progress = req.get_progress(self.candidate)
            completed = req_progress['completed']
            credits_needed = req_progress['required']

            entry = {
                'completed': completed,
                'credits_needed': credits_needed,
                'requirement': req,
                'form': form
            }

            req_type = req.requirement_type
            if req.requirement_type == CandidateRequirement.EVENT:
                entry['upcoming'] = remaining[req.get_name()]
                if completed + entry['upcoming'] - credits_needed < 0:
                    entry['warning'] = True

            form.initial['alternate_credits_needed'] = credits_needed
            form.initial['manually_recorded_credits'] = 0
            if progress:
                form.instance = progress
                form.initial['comments'] = progress.comments
                form.initial['manually_recorded_credits'] = completed

            req_types[req_type].append(entry)

        context['req_types'] = req_types
        return context

    def form_valid(self, form):
        """Check every form individually in the formset:

        Do nothing if a progress doesn't exist and credits_needed == 0
        Create a progress if one doesn't exist and credits_needed != 0
        Edit a progress if one exists and credits_needed != 0
        """
        for i, requirement in enumerate(self.requirements):
            current_form = form[i]
            progress = self.progress_list[i]
            manually_recorded_credits = current_form.cleaned_data.get(
                'manually_recorded_credits')
            alternate_credits_needed = current_form.cleaned_data.get(
                'alternate_credits_needed')
            comments = current_form.cleaned_data.get('comments')

            if ((alternate_credits_needed != requirement.credits_needed or
                 manually_recorded_credits != 0)):
                if progress:
                    # Update the progress that already exists
                    progress.manually_recorded_credits = (
                        manually_recorded_credits)
                    progress.alternate_credits_needed = alternate_credits_needed
                    progress.comments = comments
                    progress.save()
                else:
                    # Create a new progress based on the form fields only if a
                    # new progress needs to be created
                    current_form.instance.candidate = self.candidate
                    current_form.instance.requirement = requirement
                    current_form.save()
        messages.success(self.request, 'Changes saved!')
        return super(CandidateEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(CandidateEditView, self).form_invalid(form)

    def get_success_url(self):
        return reverse(
            'candidates:edit', kwargs={'candidate_pk': self.candidate.pk})


class ChallengeVerifyView(TermParameterMixin, FormView):
    form_class = ChallengeVerifyFormSet
    template_name = 'candidates/challenges.html'

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.change_challenge', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ChallengeVerifyView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self, **kwargs):
        """Set the user and term in the form."""
        kwargs = super(ChallengeVerifyView, self).get_form_kwargs(**kwargs)
        kwargs['display_term'] = self.display_term
        kwargs['user'] = self.request.user
        return kwargs

    def get_form(self, form_class):
        """Initialize each form in the formset with a challenge."""
        formset = super(ChallengeVerifyView, self).get_form(form_class)
        challenges = Challenge.objects.select_related(
            'candidate__user__userprofile', 'challenge_type').filter(
            verifying_user=self.request.user, candidate__term=self.display_term)
        for i, challenge in enumerate(challenges):
            formset[i].instance = challenge
            formset[i].initial = {
                'verified': challenges[i].verified,
                'reason': challenges[i].reason}
        return formset

    def form_valid(self, form):
        """Check every form individually in the formset."""
        for challenge_form in form:
            challenge_form.save()
        messages.success(self.request, 'Changes saved!')
        return super(ChallengeVerifyView, self).form_valid(form)

    def get_success_url(self):
        return reverse('candidates:challenges')


class CandidateRequirementsEditView(FormView):
    form_class = CandidateRequirementFormSet
    template_name = 'candidates/edit_requirements.html'
    challenge_types = None
    current_term = None
    event_types = None
    req_lists = None

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.add_candidaterequirement',
        'candidates.change_candidaterequirement', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        self.current_term = Term.objects.get_current_term()
        self.event_types = EventType.objects.all()
        self.challenge_types = ChallengeType.objects.all()

        # Initialize req_lists to contain lists for every requirement type
        self.req_lists = {}
        for req in CandidateRequirement.REQUIREMENT_TYPE_CHOICES:
            self.req_lists[req[0]] = []

        event_reqs = EventCandidateRequirement.objects.filter(
            term=self.current_term)
        # Create a list of requirements that at each index contains either a
        # requirement corresponding to an event type or None if there is no
        # requirement for the corresponding event type
        req_index = 0
        for event_type in self.event_types:
            if req_index < event_reqs.count():
                req = event_reqs[req_index]
                if req.event_type == event_type:
                    self.req_lists[CandidateRequirement.EVENT].append(req)
                    req_index += 1
                    continue
            self.req_lists[CandidateRequirement.EVENT].append(None)

        challenge_reqs = ChallengeCandidateRequirement.objects.filter(
            term=self.current_term)
        # Create a list of requirements that at each index contains either a
        # requirement corresponding to an challenge type or None if there is no
        # requirement for the corresponding challenge type
        req_index = 0
        for challenge_type in self.challenge_types:
            if req_index < challenge_reqs.count():
                req = challenge_reqs[req_index]
                if req.challenge_type == challenge_type:
                    self.req_lists[CandidateRequirement.CHALLENGE].append(req)
                    req_index += 1
                    continue
            self.req_lists[CandidateRequirement.CHALLENGE].append(None)

        exam_req = get_object_or_none(
            ExamFileCandidateRequirement, term=self.current_term)
        self.req_lists[CandidateRequirement.EXAM_FILE].append(exam_req)

        syllabus_req = get_object_or_none(
            SyllabusCandidateRequirement, term=self.current_term)
        self.req_lists[CandidateRequirement.SYLLABUS].append(syllabus_req)

        resume_req = get_object_or_none(
            ResumeCandidateRequirement, term=self.current_term)
        self.req_lists[CandidateRequirement.RESUME].append(resume_req)

        manual_reqs = ManualCandidateRequirement.objects.filter(
            term=self.current_term)
        for manual_req in manual_reqs:
            self.req_lists[CandidateRequirement.MANUAL].append(manual_req)

        return super(CandidateRequirementsEditView, self).dispatch(
            *args, **kwargs)

    def get_context_data(self, **kwargs):
        def get_entry(name, req, form):
            """Helper method that returns a dictionary containing a requirement
            name and a form, to be used for each requirement in the template.
            """
            entry = {'requirement': name, 'form': form}
            form.initial['credits_needed'] = 0
            if req:
                form.instance = req
                form.initial['credits_needed'] = req.credits_needed
            return entry

        context = super(CandidateRequirementsEditView, self).get_context_data(
            **kwargs)
        context['term'] = self.current_term
        formset = self.get_form(self.form_class)
        form_index = 0

        # Initialize req_types to contain lists for every requirement type
        req_types = {}
        for req in CandidateRequirement.REQUIREMENT_TYPE_CHOICES:
            req_types[req[0]] = []

        for i, event_type in enumerate(self.event_types):
            req = self.req_lists[CandidateRequirement.EVENT][i]
            form = formset[form_index]
            entry = get_entry(event_type.name, req, form)
            req_types[CandidateRequirement.EVENT].append(entry)
            form_index += 1

        for i, challenge_type in enumerate(self.challenge_types):
            req = self.req_lists[CandidateRequirement.CHALLENGE][i]
            form = formset[form_index]
            entry = get_entry(challenge_type.name, req, form)
            req_types[CandidateRequirement.CHALLENGE].append(entry)
            form_index += 1

        req = self.req_lists[CandidateRequirement.EXAM_FILE][0]
        form = formset[form_index]
        entry = get_entry('', req, form)
        req_types[CandidateRequirement.EXAM_FILE].append(entry)
        form_index += 1

        req = self.req_lists[CandidateRequirement.SYLLABUS][0]
        form = formset[form_index]
        entry = get_entry('', req, form)
        req_types[CandidateRequirement.SYLLABUS].append(entry)
        form_index += 1

        req = self.req_lists[CandidateRequirement.RESUME][0]
        form = formset[form_index]
        entry = get_entry('', req, form)
        req_types[CandidateRequirement.RESUME].append(entry)
        form_index += 1

        for req in self.req_lists[CandidateRequirement.MANUAL]:
            form = formset[form_index]
            entry = get_entry(req.name, req, form)
            req_types[CandidateRequirement.MANUAL].append(entry)
            form_index += 1

        context['req_types'] = req_types
        return context

    # pylint: disable=R0912
    def form_valid(self, form):
        """Check every form individually in the formset:

        Do nothing if a requirement doesn't exist and credits_needed == 0
        Create a requirement if one doesn't exist and credits_needed != 0
        Edit a requirement if one exists and credits_needed != 0
        Delete a requirement if one exists and credits_needed == 0
        """
        form_index = 0

        for i, event_type in enumerate(self.event_types):
            req = self.req_lists[CandidateRequirement.EVENT][i]
            current_form = form[form_index]
            credits_needed = current_form.cleaned_data.get('credits_needed')
            if credits_needed != 0:
                if req:
                    req.credits_needed = credits_needed
                    req.save()
                else:
                    EventCandidateRequirement.objects.get_or_create(
                        requirement_type=CandidateRequirement.EVENT,
                        credits_needed=credits_needed, term=self.current_term,
                        event_type=event_type)
            else:
                if req:
                    req.delete()
            form_index += 1

        for i, challenge_type in enumerate(self.challenge_types):
            req = self.req_lists[CandidateRequirement.CHALLENGE][i]
            current_form = form[form_index]
            credits_needed = current_form.cleaned_data.get('credits_needed')
            if credits_needed != 0:
                if req:
                    req.credits_needed = credits_needed
                    req.save()
                else:
                    ChallengeCandidateRequirement.objects.get_or_create(
                        requirement_type=CandidateRequirement.CHALLENGE,
                        credits_needed=credits_needed, term=self.current_term,
                        challenge_type=challenge_type)
            else:
                if req:
                    req.delete()
            form_index += 1

        req = self.req_lists[CandidateRequirement.EXAM_FILE][0]
        current_form = form[form_index]
        credits_needed = current_form.cleaned_data.get('credits_needed')
        if credits_needed != 0:
            if req:
                req.credits_needed = credits_needed
                req.save()
            else:
                ExamFileCandidateRequirement.objects.get_or_create(
                    requirement_type=CandidateRequirement.EXAM_FILE,
                    credits_needed=credits_needed, term=self.current_term)
        else:
            if req:
                req.delete()
        form_index += 1

        req = self.req_lists[CandidateRequirement.SYLLABUS][0]
        current_form = form[form_index]
        credits_needed = current_form.cleaned_data.get('credits_needed')
        if credits_needed != 0:
            if req:
                req.credits_needed = credits_needed
                req.save()
            else:
                SyllabusCandidateRequirement.objects.get_or_create(
                    requirement_type=CandidateRequirement.SYLLABUS,
                    credits_needed=credits_needed, term=self.current_term)
        else:
            if req:
                req.delete()
        form_index += 1

        req = self.req_lists[CandidateRequirement.RESUME][0]
        current_form = form[form_index]
        credits_needed = current_form.cleaned_data.get('credits_needed')
        if credits_needed != 0:
            if req:
                req.credits_needed = credits_needed
                req.save()
            else:
                ResumeCandidateRequirement.objects.get_or_create(
                    requirement_type=CandidateRequirement.RESUME,
                    credits_needed=credits_needed, term=self.current_term)
        else:
            if req:
                req.delete()
        form_index += 1

        for req in self.req_lists[CandidateRequirement.MANUAL]:
            credits_needed = form[form_index].cleaned_data.get('credits_needed')
            if credits_needed != 0:
                req.credits_needed = credits_needed
                req.save()
            else:
                req.delete()
            form_index += 1

        messages.success(self.request, 'Changes saved!')
        return super(CandidateRequirementsEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(CandidateRequirementsEditView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('candidates:edit-requirements')


class ManualCandidateRequirementCreateView(CreateView):
    form_class = ManualCandidateRequirementForm
    template_name = 'candidates/add_manual_requirement.html'
    display_req_type = 'Manual'

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.add_candidaterequirement', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ManualCandidateRequirementCreateView, self).dispatch(
            *args, **kwargs)

    def form_valid(self, form):
        """Set the term of the requirement to the current term."""
        form.instance.term = Term.objects.get_current_term()
        messages.success(self.request, '{req_type} requirement created!'.format(
            req_type=self.display_req_type))
        return super(
            ManualCandidateRequirementCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(
            ManualCandidateRequirementCreateView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('candidates:edit-requirements')


class CandidatePortalView(CreateView, CandidateContextMixin):
    """The view for the candidate portal, which is also used for creating
    challenges.
    """
    form_class = ChallengeForm
    template_name = 'candidates/portal.html'
    candidate = None
    current_term = None

    @method_decorator(login_required)
    # TODO(ericdwang): Make sure that only candidates can access this view
    def dispatch(self, *args, **kwargs):
        self.current_term = Term.objects.get_current_term()
        self.candidate = get_object_or_404(
            Candidate, user=self.request.user, term=self.current_term)
        return super(CandidatePortalView, self).dispatch(
            *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['candidate'] = self.candidate
        context = super(CandidatePortalView, self).get_context_data(**kwargs)
        requirements = CandidateRequirement.objects.filter(
            term=self.current_term).select_related(
            'eventcandidaterequirement',
            'eventcandidaterequirement__event_type',
            'challengecandidaterequirement',
            'challengecandidaterequirement__challenge_type',
            'examfilecandidaterequirement')

        # Initialize req_types to contain lists for every requirement type
        req_types = {}
        for req in CandidateRequirement.REQUIREMENT_TYPE_CHOICES:
            req_types[req[0]] = []

        for req in requirements:
            req_progress = req.get_progress(self.candidate)

            entry = {
                'completed': req_progress['completed'],
                'credits_needed': req_progress['required'],
                'requirement': req
            }
            req_type = req.requirement_type
            req_types[req_type].append(entry)

        context['req_types'] = req_types
        return context

    def form_valid(self, form):
        """Set the candidate of the challenge to the requester.

        Also create a notification and send a verification email to the
        verifying user.
        """
        form.instance.candidate = self.candidate
        challenge = form.save()
        candidate_name = self.candidate.user.userprofile.get_common_name()

        Notification.objects.create(
            user=challenge.verifying_user,
            status=Notification.NEUTRAL,
            content_type=ContentType.objects.get_for_model(Challenge),
            object_pk=challenge.pk,
            title='Challenge Verification Request',
            subtitle='{} challenge by {}'.format(
                challenge.challenge_type, candidate_name),
            description=challenge.description,
            url=reverse('candidates:challenges'))

        subject = 'Challenge Verification Request from {}'.format(
            candidate_name)
        body = render_to_string(
            'candidates/challenge_verification_email.html',
            {'candidate': candidate_name,
             'challenge': challenge})
        message = EmailMessage(
            subject=subject,
            body=body,
            to=[challenge.verifying_user.userprofile.get_preferred_email()])
        message.send(fail_silently=True)

        messages.success(self.request, 'Challenge requested!')
        return super(CandidatePortalView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(CandidatePortalView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('candidates:portal')


class CandidateInitiationView(CandidateListView):
    """View for marking candidates as initiated, granting member status."""
    template_name = 'candidates/initiation.html'

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.can_initiate_candidates', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CandidateInitiationView, self).dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        return super(CandidateInitiationView, self).get_queryset(
            *args, **kwargs).select_related('user__userprofile', 'term')


class CandidateProgressMixin(TermParameterMixin, ContextMixin):
    display_house = None

    def dispatch(self, request, *args, **kwargs):
        house_pk = request.GET.get('house', '')
        if house_pk:
            self.display_house = get_object_or_none(House, id=house_pk)
            if self.display_house is None:
                # Bad request
                return render(request, template_name='400.html', status=400)

        return super(CandidateProgressMixin, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CandidateProgressMixin, self).get_context_data(**kwargs)
        context['houses'] = House.objects.all()
        context['display_house'] = self.display_house

        candidates = Candidate.objects.filter(term=self.display_term)

        progress_by_candidate = Candidate.get_progress_by_candidate(
            candidates, self.display_term)

        # Exclude candidates not in the selected house
        for candidate in progress_by_candidate.keys():
            if self.display_house and \
                    self.display_house.id not in \
                    candidate.user.housemember.filter(
                        term=self.display_term).values_list(
                            'house', flat=True):
                del progress_by_candidate[candidate]

        context['progress'] = {}
        for candidate, progress in progress_by_candidate.items():
            candidate_progress = {
                'requirements': progress,
                'all_requirements_complete': True
            }
            context['progress'][candidate] = candidate_progress

            for progress_item in progress:
                if progress_item['completed'] < progress_item['required']:
                    candidate_progress['all_requirements_complete'] = False
                    break

        return context


class CandidateProgressView(TemplateView, CandidateProgressMixin):
    template_name = 'candidates/progress.html'
    display_house = None

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.change_candidate', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(CandidateProgressView, self).dispatch(
            request, *args, **kwargs)


class CandidateProgressByReqView(TemplateView, CandidateProgressMixin):
    template_name = 'candidates/progress_by_req.html'
    display_req = None

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.change_candidate', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        req_pk = request.GET.get('req', '')
        if req_pk:
            self.display_req = get_object_or_none(
                CandidateRequirement, id=req_pk)
            if self.display_req is None:
                # Bad request
                return render(request, template_name='400.html', status=400)

        return super(CandidateProgressByReqView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CandidateProgressByReqView, self).get_context_data(
            **kwargs)
        context['display_req'] = self.display_req

        progress = context['progress']

        # Dictionary of lists of (candidate, req_progress) tuples, keyed
        # by requirement
        progresses_by_req = {}
        req_info_by_name = {}
        for candidate, progress_item in progress.items():
            for req_progress in progress_item['requirements']:
                requirement = req_progress['requirement']
                # Exclude progresses with the wrong requirement
                if self.display_req and self.display_req != requirement:
                    continue
                req_name = requirement.get_name()
                if req_name not in progresses_by_req:
                    progresses_by_req[req_name] = []
                    is_event_req = (requirement.requirement_type ==
                                    requirement.EVENT)
                    remaining = req_progress['remaining'] if is_event_req \
                        else None
                    req_info_by_name[req_name] = {
                        'is_event_req': is_event_req,
                        'remaining': remaining,
                        'req_obj': requirement,
                    }
                num_unfinished = req_progress['required'] - \
                    req_progress['completed']
                progresses_by_req[req_name].append(
                    (candidate, req_progress, num_unfinished))

        context['progresses_by_req'] = [(req_name,
                                         req_info_by_name[req_name],
                                         progresses)
                                        for req_name, progresses
                                        in progresses_by_req.items()]
        return context


class CandidateProgressStatsView(TemplateView, CandidateProgressMixin):
    template_name = 'candidates/progress_stats.html'

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.change_candidate', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CandidateProgressStatsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CandidateProgressStatsView, self).get_context_data(
            **kwargs)

        progress = context['progress']
        progress_by_req = {}
        total_unfinished = 0
        for progress_item in progress.values():
            for req_progress in progress_item['requirements']:
                req_name = req_progress['requirement'].get_name()
                completed = req_progress['completed']
                required = req_progress['required']
                unfinished = max(0, required - completed)
                if req_name not in progress_by_req:
                    progress_by_req[req_name] = {'unfinished': 0}
                progress_by_req[req_name]['unfinished'] += unfinished
                total_unfinished += unfinished
        for req_name in progress_by_req:
            progress_by_req[req_name]['unfinished'] /= float(len(progress))
        total_unfinished /= float(len(progress))
        context['progress_by_req'] = progress_by_req
        context['total_unfinished'] = total_unfinished

        return context


class CandidateExportView(View):
    """View for exporting the list of candidates as a CSV file."""

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'candidates.change_candidate', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CandidateExportView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="candidates.csv"'
        writer = csv.writer(response)
        writer.writerow(['Last name', 'First name', 'Middle name', 'Email',
                         'Standing', 'Graduation date', 'Major'])

        current_term = Term.objects.get(id=kwargs['term_pk'])
        candidates = Candidate.objects.filter(
            term=current_term).select_related(
            'user', 'user__userprofile',
            'user__collegestudentinfo__major',
            'user__collegestudentinfo__start_term',
            'user__collegestudentinfo').order_by(
            'user__last_name')
        for candidate in candidates:
            start_term = candidate.user.collegestudentinfo.start_term
            candidate_year = current_term.year - start_term.year + 1
            if Term(year=start_term.year, term=current_term.term) < start_term:
                candidate_year -= 1

            # Not entirely correct, but this is the best we can do with the
            # information we have.
            candidate_standing = 'Junior' if candidate_year <= 2 else 'Senior'

            candidate_majors = candidate.user.collegestudentinfo.major
            candidate_major_list = candidate_majors.values_list(
                'long_name', flat=True)

            writer.writerow(
                [candidate.user.last_name,
                 candidate.user.first_name,
                 candidate.user.userprofile.middle_name,
                 candidate.user.email,
                 candidate_standing,
                 candidate.user.collegestudentinfo.grad_term.verbose_name(),
                 '/'.join(candidate_major_list)])

        return response


@require_POST
@permission_required('candidates.can_initiate_candidates', raise_exception=True)
def update_candidate_initiation_status(request):
    """Endpoint for updating a candidate's initiation status.

    The post parameters "candidate" and "initiated" specify the candidate (by
    Candidate pk) and their new initiation status, respectively.
    """
    candidate_pk = request.POST.get('candidate')
    if not candidate_pk:
        return json_response(status=404)
    candidate = get_object_or_none(Candidate, pk=candidate_pk)
    initiated = json.loads(request.POST.get('initiated'))
    if not candidate or initiated is None:
        return json_response(status=400)

    candidate.initiated = initiated
    candidate.save(update_fields=['initiated'])
    # TODO(sjdemartini): Update relevant mailing lists, moving initiated
    # candidates off of the candidates list and onto the members list.
    return json_response()
