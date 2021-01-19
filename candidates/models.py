import collections
import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Sum

from quark.base.models import Term
from quark.events.models import Event
from quark.events.models import EventAttendance
from quark.events.models import EventSignUp
from quark.events.models import EventType
from quark.exams.models import Exam
from quark.syllabi.models import Syllabus
from quark.resumes.models import Resume


class Candidate(models.Model):
    """A candidate for a given term.

    Provides an interface for each candidate's progress, but
    only for a single term. To account for past progress, one will
    have to query multiple Candidate objects.
    """
    PHOTOS_LOCATION = 'candidates'

    def rename_photo(instance, filename):
        """Rename the photo to the candidate's username, and update the photo
        if it already exists.
        """
        # pylint: disable=E0213
        file_ext = os.path.splitext(filename)[1]
        filename = os.path.join(Candidate.PHOTOS_LOCATION,
                                str(instance.user.get_username()) + file_ext)
        full_path = os.path.join(settings.MEDIA_ROOT, filename)
        # if photo already exists, delete it so the new photo can use the
        # same name
        if os.path.exists(full_path):
            os.remove(full_path)
        return filename

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    term = models.ForeignKey(Term)
    initiated = models.BooleanField(default=False)
    photo = models.ImageField(blank=True, upload_to=rename_photo)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ('-term', 'user__userprofile')
        permissions = (
            ('can_initiate_candidates', 'Can mark candidates as initiated'),
        )
        unique_together = ('user', 'term')

    def get_progress(self, requirement_type=None):
        """Return a dictionary with keys "completed" and "required", which
        map to the number of completed requirements and the number that were
        required, respectively.

        If requirement_type is not specified, the method returns total progress
        for all requirements. If requirement is specified, only progress for
        the specific requirement type is returned.

        Useful for summary info, progress bars, and other visualizations.
        """
        if requirement_type is None:
            requirements = CandidateRequirement.objects.filter(term=self.term)
        else:
            requirements = CandidateRequirement.objects.filter(
                term=self.term, requirement_type=requirement_type)

        # Select-related to improve performance, fetching data for requirements
        # from multiple tables
        requirements.select_related(
            'eventcandidaterequirement',
            'eventcandidaterequirement__event_type',
            'challengecandidaterequirement',
            'challengecandidaterequirement__challenge_type',
            'examfilecandidaterequirement',
            'syllabuscandidaterequirement')

        # TODO(sjdemartini): Figure out a way to optimize fetching the progress
        # for event requirements and fetching CandidateRequirementProgress
        # objects in order to minimize number of queries

        progress = [req.get_progress(self) for req in requirements]
        completed = sum([x['completed'] for x in progress])
        required = sum([x['required'] for x in progress])
        return {'completed': completed, 'required': required}

    @staticmethod
    # pylint: disable=R0912
    # pylint: disable=R0914
    def get_progress_by_candidate(candidates, term):
        """
        Get the progress of a set of candidates. Returns a dictionary where
        the keys are candidates and the values are lists of dictionaries, one
        for each requirement. The dictionaries have the following keys:

            required: Number of items needed to satisfy the requirement
            completed: Number of items completed
            signed_up (event requirements only): Number of event sign ups that
                satisfy the requirement
            warning (event requirements only): True if there are not enough
                events remaining for the requirement to be satisfied
        """
        candidate_users = candidates.values_list('user', flat=True)
        candidate_ids_by_user_id = dict(candidates.values_list('user', 'id'))
        candidates_by_id = Candidate.objects.in_bulk(candidates.values_list(
            'id', flat=True))

        upcoming_events = Event.objects.get_upcoming().filter(
            term=term).select_related('event_type')
        requirements = CandidateRequirement.objects.filter(term=term)
        attendances = EventAttendance.objects.select_related(
            'event__event_type', 'user').filter(
            event__term=term, user__in=candidate_users)
        signups = EventSignUp.objects.select_related(
            'event__event_type', 'user').filter(
            event__term=term, user__in=candidate_users, unsignup=False).exclude(
            event__in=attendances.values_list('event', flat=True))

        attendances_by_candidate = {candidate: [] for candidate in candidates}
        signup_counters_by_candidate = {candidate: collections.Counter()
                                        for candidate in candidates}
        for attendance in attendances:
            candidate_id = candidate_ids_by_user_id[attendance.user.id]
            candidate = candidates_by_id[candidate_id]
            attendances_by_candidate[candidate].append(attendance)
        for signup in signups:
            candidate_id = candidate_ids_by_user_id[signup.user.id]
            candidate = candidates_by_id[candidate_id]
            signup_counter = signup_counters_by_candidate[candidate]
            signup_counter[signup.event.event_type.name] += 1

        # Get CandidateRequirementProgress objects for each candidate
        crp_objects = CandidateRequirementProgress.objects.filter(
            candidate__term=term, candidate__in=candidates).select_related(
            'candidate')

        try:
            elective_req = requirements.get(
                eventcandidaterequirement__event_type__name='Elective')
            requirements = requirements.exclude(id=elective_req.id)
            required_event_types = requirements.filter(
                requirement_type=CandidateRequirement.EVENT).values_list(
                'eventcandidaterequirement__event_type', flat=True)
            elective_event_types = EventType.objects.filter(
                eligible_elective=True).exclude(id__in=required_event_types)
        except CandidateRequirement.DoesNotExist:
            elective_req = None

        progress_by_candidate = {candidate: [] for candidate in candidates}

        # Dictionary of elective progresses
        elective_progress_by_candidate = {}

        # Calculate elective requirements satisfied by elective events (doesn't
        # include extra required events that count for electives).
        # TODO(ehy): this doesn't work when there isn't an elective requirement
        remaining_elective_events = len(upcoming_events.filter(
            event_type__in=elective_event_types))
        for candidate in candidates:
            elective_progress = {
                'requirement': elective_req,
                'completed': 0,
                'signed_up': 0,
                'warning': False,
                'remaining': remaining_elective_events,
                'required': elective_req.credits_needed
            }
            elective_progress_by_candidate[candidate] = elective_progress
            for attendance in attendances_by_candidate[candidate]:
                if attendance.event.event_type in elective_event_types:
                    elective_progress['completed'] += 1
            for event_type in elective_event_types:
                signup_counter = signup_counters_by_candidate[candidate]
                elective_progress['signed_up'] += signup_counter[
                    event_type.name]

        # Handle per-candidate elective requirements
        elective_crp_objects = crp_objects.filter(requirement=elective_req)
        for crp in elective_crp_objects:
            elective_progress = elective_progress_by_candidate[crp.candidate]
            elective_progress['completed'] += crp.manually_recorded_credits
            elective_progress['required'] = crp.alternate_credits_needed

        remaining = collections.Counter()
        for event in upcoming_events:
            remaining[event.event_type.name] += 1

        # Get all the information we need from the database
        for req in requirements:
            # Get the "completed" and "required" fields for each requirement
            req_progress_by_candidate = req.get_progress_by_candidate(
                candidates)

            if req.requirement_type == CandidateRequirement.EVENT:
                # Calculate event requirement statistics (electives, signups,
                # warnings, etc.) for each candidate
                for candidate, req_progress \
                        in req_progress_by_candidate.items():
                    req_progress['requirement'] = req
                    required = req_progress['required']
                    req_progress['warning'] = False
                    if required > 0:
                        completed = req_progress['completed']
                        total_possible = completed + remaining[req.get_name()]
                        if total_possible < required:
                            req_progress['warning'] = True
                        signup_counter = signup_counters_by_candidate[candidate]
                        num_signup = signup_counter[req.get_name()]
                        req_progress['signed_up'] = num_signup
                        req_progress['remaining'] = remaining[req.get_name()]
                        progress_by_candidate[candidate].append(req_progress)
                    event_type = req.eventcandidaterequirement.event_type
                    if event_type.eligible_elective:
                        elective_progress = elective_progress_by_candidate[
                            candidate]
                        elective_progress['remaining'] += remaining[
                            req.get_name()]

                        # Only count completed and signed-up non-elective events
                        # if they exceed the requirement.
                        extra_completed = max(0, completed - required)
                        not_completed = max(0, required - completed)
                        extra_signups = max(0, num_signup - not_completed)
                        elective_progress['completed'] += extra_completed
                        elective_progress['signed_up'] += extra_signups

            else:  # req is not an event requirement
                for candidate, req_progress \
                        in req_progress_by_candidate.items():
                    req_progress['requirement'] = req
                    progress_by_candidate[candidate].append(req_progress)

        # Trigger warnings for elective events
        for elective_progress in elective_progress_by_candidate.values():
            completed = elective_progress['completed']
            remaining = elective_progress['remaining']
            required = elective_progress['required']
            if completed + remaining < required:
                elective_progress['warning'] = True

        # Merge elective progresses with the others
        for candidate in candidates:
            elective_progress = elective_progress_by_candidate[candidate]
            progress_by_candidate[candidate].append(elective_progress)

        return progress_by_candidate

    def are_electives_required(self):
        """Return true if elective events are required; false otherwise."""
        event_reqs = CandidateRequirement.objects.filter(
            term=self.term,
            requirement_type=CandidateRequirement.EVENT)
        try:
            elective_req = event_reqs.get(
                eventcandidaterequirement__event_type__name='Elective')
        except CandidateRequirement.DoesNotExist:
            return False
        return elective_req.get_progress(self)['required'] > 0

    def __unicode__(self):
        return '{user} ({term})'.format(user=self.user, term=self.term)


def candidate_post_save(sender, instance, created, **kwargs):
    """Ensure that a StudentOrgUserProfile exists for every Candidate,
    update the profile's 'initiation_term' field, and add the candidate to the
    appropriate group.

    If the candidate is marked as initiated, add the candidate to the Member
    group and remove the candidate from the Current Candidate group.
    If the candidate is marked as not initiated, remove the candidate from the
    Member group and add the candidate to the Current Candidate group if the
    candidate is initiating in the current term.

    Anyone who is a candidate in the student organization also needs a user
    profile as a student participating in that organization.

    The field in StudentOrgUserProfile is updated in two scenarios:
        - if Candidate marks the user as initiated.
        - if Candidate marks the user as _not_ initiated and
          StudentOrgUserProfile had recorded the user as initiated in the term
          corresponding to this Candidate object (in which case,
          StudentOrgUserProfile should now reflect that the user did not
          initiate)
    """
    # Avoid circular dependency by importing here:
    from quark.user_profiles.models import StudentOrgUserProfile

    student_org_profile, _ = StudentOrgUserProfile.objects.get_or_create(
        user=instance.user)

    candidate_group = Group.objects.get(name='Current Candidate')
    member_group = Group.objects.get(name='Member')

    if instance.initiated:
        student_org_profile.initiation_term = instance.term
        student_org_profile.save()
        instance.user.groups.add(member_group)
        instance.user.groups.remove(candidate_group)
    else:
        if student_org_profile.initiation_term == instance.term:
            student_org_profile.initiation_term = None
            student_org_profile.save()
        instance.user.groups.remove(member_group)
        if instance.term == Term.objects.get_current_term():
            instance.user.groups.add(candidate_group)
        else:
            instance.user.groups.remove(candidate_group)

models.signals.post_save.connect(candidate_post_save, sender=Candidate)


class ChallengeTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        try:
            return self.get(name=name)
        except ChallengeType.DoesNotExist:
            return None


class ChallengeType(models.Model):
    name = models.CharField(max_length=60, unique=True)

    objects = ChallengeTypeManager()

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class Challenge(models.Model):
    """A challenge done by a Candidate.

    Challenges are requested by the Candidate upon completion and verified by
    the person who gave the candidate the challenge.
    """
    # Custom displays for the verified NullBooleanField
    VERIFIED_CHOICES = (
        (None, 'Pending'),
        (True, 'Approved'),
        (False, 'Denied'),
    )

    candidate = models.ForeignKey(Candidate)
    challenge_type = models.ForeignKey(ChallengeType)
    description = models.CharField(max_length=255)
    verifying_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text='Person who verified the challenge.')
    verified = models.NullBooleanField(choices=VERIFIED_CHOICES)
    reason = models.CharField(
        blank=True, max_length=255,
        help_text='Why is the challenge being approved or denied? (Optional)')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{candidate}: Challenge given by {user}'.format(
            candidate=self.candidate, user=self.verifying_user)

    class Meta(object):
        ordering = ('candidate', 'created')


class CandidateRequirement(models.Model):
    """A base for other requirements."""
    # Requirement Type constants
    EVENT = 'event'
    CHALLENGE = 'challenge'
    EXAM_FILE = 'exam'
    SYLLABUS = 'syllabus'
    RESUME = 'resume'
    MANUAL = 'manual'

    REQUIREMENT_TYPE_CHOICES = (
        (EVENT, 'Event'),
        (CHALLENGE, 'Challenge'),
        (EXAM_FILE, 'Exam File'),
        (SYLLABUS, 'Syllabus'),
        (RESUME, 'Resume'),
        (MANUAL, 'Other (manually verified)')
    )

    requirement_type = models.CharField(
        max_length=9, choices=REQUIREMENT_TYPE_CHOICES, db_index=True)
    credits_needed = models.IntegerField(
        help_text='Amount of credits needed to fulfill a candidate requirement')
    term = models.ForeignKey(Term)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_progress(self, candidate):
        """Return a dictionary with keys "completed" and "required", which
        map to the number of completed requirements and the number that were
        required, respectively, for the given candidate.
        """
        required = self.credits_needed

        if self.requirement_type == CandidateRequirement.EVENT:
            completed = self.eventcandidaterequirement.get_completed(candidate)
        elif self.requirement_type == CandidateRequirement.CHALLENGE:
            completed = self.challengecandidaterequirement.get_completed(
                candidate)
        elif self.requirement_type == CandidateRequirement.EXAM_FILE:
            completed = self.examfilecandidaterequirement.get_completed(
                candidate)
        elif self.requirement_type == CandidateRequirement.SYLLABUS:
            completed = self.syllabuscandidaterequirement.get_completed(
                candidate)
        elif self.requirement_type == CandidateRequirement.RESUME:
            completed = self.resumecandidaterequirement.get_completed(candidate)
        elif self.requirement_type == CandidateRequirement.MANUAL:
            # Actual credits earned is read from CandidateProgress below
            completed = 0
        else:
            raise NotImplementedError(
                'Unknown type {}'.format(self.requirement_type))

        # Check per-candidate overrides and exemptions
        try:
            progress = CandidateRequirementProgress.objects.get(
                candidate=candidate, requirement=self)
            completed += progress.manually_recorded_credits
            required = progress.alternate_credits_needed
        except CandidateRequirementProgress.DoesNotExist:
            pass

        return {'completed': completed, 'required': required}

    def get_progress_by_candidate(self, candidates):
        required = {candidate: self.credits_needed for candidate in candidates}

        if self.requirement_type == CandidateRequirement.EVENT:
            completed = self.eventcandidaterequirement \
                .get_completed_by_candidate(candidates)
        elif self.requirement_type == CandidateRequirement.CHALLENGE:
            completed = self.challengecandidaterequirement \
                .get_completed_by_candidate(candidates)
        elif self.requirement_type == CandidateRequirement.EXAM_FILE:
            completed = self.examfilecandidaterequirement \
                .get_completed_by_candidate(candidates)
        elif self.requirement_type == CandidateRequirement.RESUME:
            completed = self.resumecandidaterequirement \
                .get_completed_by_candidate(candidates)
        elif self.requirement_type == CandidateRequirement.SYLLABUS:
            completed = self.syllabuscandidaterequirement \
                .get_completed_by_candidate(candidates)
        elif self.requirement_type == CandidateRequirement.MANUAL:
            # Actual credits earned is read from CandidateProgress below
            completed = {candidate: 0 for candidate in candidates}
        else:
            raise NotImplementedError(
                'Unknown type {}'.format(self.requirement_type))

        # Check per-candidate overrides and exemptions
        crp_objects = CandidateRequirementProgress.objects.filter(
            candidate__in=candidates, requirement=self)
        for crp in crp_objects:
            completed[crp.candidate] += crp.manually_recorded_credits
            required[crp.candidate] = crp.alternate_credits_needed

        return {candidate: {'completed': completed[candidate],
                            'required': required[candidate]}
                for candidate in candidates}

    def get_name(self):
        """Return a name for the requirement based on the requirement type."""
        if self.requirement_type == CandidateRequirement.EVENT:
            return self.eventcandidaterequirement.event_type.name
        elif self.requirement_type == CandidateRequirement.CHALLENGE:
            return '{} Challenges'.format(
                self.challengecandidaterequirement.challenge_type.name)
        elif self.requirement_type == CandidateRequirement.EXAM_FILE:
            return 'Exam Files'
        elif self.requirement_type == CandidateRequirement.SYLLABUS:
            return 'Syllabus'
        elif self.requirement_type == CandidateRequirement.RESUME:
            return 'Resume'
        elif self.requirement_type == CandidateRequirement.MANUAL:
            return self.manualcandidaterequirement.name
        else:
            raise NotImplementedError(
                'Unknown type {}'.format(self.requirement_type))

    def __unicode__(self):
        return '{name}, {credits} required ({term})'.format(
            name=self.get_name(),
            credits=self.credits_needed, term=self.term)

    class Meta(object):
        ordering = ('-term', 'requirement_type')


class EventCandidateRequirement(CandidateRequirement):
    """Requirement for attending events of a certain type."""
    event_type = models.ForeignKey(EventType)

    def save(self, *args, **kwargs):
        """Override save handler to ensure that requirement_type is correct."""
        self.requirement_type = CandidateRequirement.EVENT
        super(EventCandidateRequirement, self).save(*args, **kwargs)

    def get_completed(self, candidate):
        """Return the number of credits completed by candidate."""
        events_attended = Event.objects.filter(
            eventattendance__user=candidate.user,
            term=candidate.term,
            event_type=self.event_type)
        return events_attended.aggregate(
            total=Sum('requirements_credit'))['total'] or 0

    def get_completed_by_candidate(self, candidates):
        """
        Return a dictionary where the keys are candidates and the values are
        the number of credits completed by each candidate.
        """
        candidates_by_id = Candidate.objects.in_bulk(candidates.values_list(
            'id', flat=True))
        attendances = EventAttendance.objects.filter(
            user__candidate__in=candidates, event__term=self.term,
            event__event_type=self.event_type)
        credits_by_candidate = attendances.values_list(
            'user__candidate', 'event__requirements_credit')

        completed_by_candidate = {candidate: 0 for candidate in candidates}
        for candidate_id, credit in credits_by_candidate:
            candidate = candidates_by_id.get(candidate_id)
            # Some users are candidates in multiple terms, so exclude the ones
            # that aren't in this term.
            if candidate:
                completed_by_candidate[candidate] += credit

        return completed_by_candidate

    class Meta(object):
        ordering = ('-term', 'requirement_type', 'event_type')


class ChallengeCandidateRequirement(CandidateRequirement):
    """Requirement for completing challenges issued by officers."""
    challenge_type = models.ForeignKey(ChallengeType)

    def save(self, *args, **kwargs):
        """Override save handler to ensure that requirement_type is correct."""
        self.requirement_type = CandidateRequirement.CHALLENGE
        super(ChallengeCandidateRequirement, self).save(*args, **kwargs)

    def get_completed(self, candidate):
        """Return the number of credits completed by candidate."""
        return Challenge.objects.filter(
            candidate=candidate,
            challenge_type=self.challenge_type,
            verified=True).count()

    def get_completed_by_candidate(self, candidates):
        """
        Return a dictionary of the number of credits completed by each
        candidate.
        """
        challenges = Challenge.objects.filter(
            candidate__in=candidates,
            challenge_type=self.challenge_type,
            verified=True).select_related('candidate')
        completed_by_candidate = {candidate: 0 for candidate in candidates}
        for challenge in challenges:
            completed_by_candidate[challenge.candidate] += 1
        return completed_by_candidate

    class Meta(object):
        ordering = ('-term', 'requirement_type', 'challenge_type')


class ExamFileCandidateRequirement(CandidateRequirement):
    """Requirement for uploading exam files to the site."""
    def save(self, *args, **kwargs):
        """Override save handler to ensure that requirement_type is correct."""
        self.requirement_type = CandidateRequirement.EXAM_FILE
        super(ExamFileCandidateRequirement, self).save(*args, **kwargs)

    def get_completed(self, candidate):
        """Returns the number of credits completed by candidate"""
        return Exam.objects.get_approved().filter(
            submitter=candidate.user).count()

    def get_completed_by_candidate(self, candidates):
        candidates_by_id = Candidate.objects.in_bulk(candidates.values_list(
            'id', flat=True))
        exams = Exam.objects.get_approved().filter(
            submitter__candidate__in=candidates)
        exam_candidates = exams.values_list(
            'submitter__candidate', flat=True)
        completed_by_candidate = {candidate: 0 for candidate in candidates}
        for candidate_id in exam_candidates:
            candidate = candidates_by_id.get(candidate_id)
            if candidate:
                completed_by_candidate[candidate] += 1

        return completed_by_candidate


class SyllabusCandidateRequirement(CandidateRequirement):
    """Requirement for uploading syllabi to the site."""
    def save(self, *args, **kwargs):
        """Override save handler to ensure that requirement_type is correct."""
        self.requirement_type = CandidateRequirement.SYLLABUS
        super(SyllabusCandidateRequirement, self).save(*args, **kwargs)

    def get_completed(self, candidate):
        """Returns the number of credits completed by candidate"""
        return Syllabus.objects.get_approved().filter(
            submitter=candidate.user).count()

    def get_completed_by_candidate(self, candidates):
        candidates_by_id = Candidate.objects.in_bulk(
            candidates.values_list('id', flat=True))
        syllabi = Syllabus.objects.get_approved().filter(
            submitter__candidate__in=candidates)
        syllabi_candidates = syllabi.values_list(
            'submitter__candidate', flat=True)
        completed_by_candidate = {candidate: 0 for candidate in candidates}
        for candidate_id in syllabi_candidates:
            candidate = candidates_by_id[candidate_id]
            if candidate in candidates:
                completed_by_candidate[candidate] = 1

        return completed_by_candidate


class ResumeCandidateRequirement(CandidateRequirement):
    """Requirement for uploading a resume to the site."""
    def save(self, *args, **kwargs):
        """Override save handler to ensure that requirement_type is correct."""
        self.requirement_type = CandidateRequirement.RESUME
        super(ResumeCandidateRequirement, self).save(*args, **kwargs)

    def get_completed(self, candidate):
        return Resume.objects.filter(user=candidate.user, verified=True).count()

    def get_completed_by_candidate(self, candidates):
        candidates_by_id = Candidate.objects.in_bulk(
            candidates.values_list('id', flat=True))
        resumes = Resume.objects.filter(
            user__candidate__in=candidates, verified=True)
        resume_candidates = resumes.values_list('user__candidate', flat=True)
        completed_by_candidate = {candidate: 0 for candidate in candidates}
        for candidate_id in resume_candidates:
            candidate = candidates_by_id[candidate_id]
            if candidate in candidates:
                completed_by_candidate[candidate] = 1

        return completed_by_candidate


class ManualCandidateRequirement(CandidateRequirement):
    name = models.CharField(max_length=60, db_index=True)

    def save(self, *args, **kwargs):
        """Override save handler to ensure that requirement_type is correct."""
        self.requirement_type = CandidateRequirement.MANUAL
        super(ManualCandidateRequirement, self).save(*args, **kwargs)

    class Meta(object):
        ordering = ('-term', 'requirement_type', 'name')


class CandidateRequirementProgress(models.Model):
    """Track one candidate's progress towards one requirement.

    For MANUAL requirements, the manually_recorded_credits field is set
    manually. For EVENT and other auto requirements, both the
    manually_recorded_credits and the alternate_credits_needed fields may be
    used as manual adjustments.
    """
    candidate = models.ForeignKey(Candidate)
    requirement = models.ForeignKey(CandidateRequirement)
    manually_recorded_credits = models.IntegerField(
        default=0, help_text='Additional credits that go toward fulfilling a '
        'candidate requirement')
    alternate_credits_needed = models.IntegerField(
        default=0, help_text='Alternate amount of credits needed to fulfill a '
        'candidate requirement')
    comments = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '{candidate}: {req}'.format(
            candidate=self.candidate, req=self.requirement)

    class Meta(object):
        ordering = ('requirement', 'candidate')
        verbose_name_plural = 'candidate requirement progresses'
