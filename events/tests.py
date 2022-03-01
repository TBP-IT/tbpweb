import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from base.models import Officer
from base.models import OfficerPosition
from base.models import Term
from candidates.models import Candidate
from events.forms import EventForm
from events.forms import EventCancelForm
from events.models import Event
from events.models import EventAttendance
from events.models import EventSignUp
from events.models import EventType
from project_reports.models import ProjectReport
from shortcuts import get_object_or_none
from user_profiles.models import StudentOrgUserProfile


@override_settings(USE_TZ=True)
class EventTesting(TestCase):
    """Define a common setUp and helper method for event testing.

    Subclassed below for ease of testing various aspects of events.
    """
    def setUp(self):
        Group.objects.create(name='Current Candidate')
        Group.objects.create(name='Member')

        self.user = get_user_model().objects.create_user(
            username='bentleythebent',
            email='it@tbp.berkeley.edu',
            password='testofficerpw',
            first_name='Bentley',
            last_name='Bent')

        self.committee = OfficerPosition(
            short_name='IT',
            long_name='Information Technology',
            rank=2,
            mailing_list='IT')
        self.committee.save()

        self.term = Term(term=Term.SPRING, year=2012, current=True)
        self.term.save()

        self.event_type, _ = EventType.objects.get_or_create(
            name='Test Event Type')

    def create_event(self, start_time, end_time, name='My Test Event',
                     restriction=Event.OFFICER):
        """Create, save, and return a new event."""
        event = Event(name=name,
                      event_type=self.event_type,
                      start_datetime=start_time,
                      end_datetime=end_time,
                      term=self.term,
                      location='A test location',
                      contact=self.user,
                      committee=self.committee,
                      restriction=restriction)
        event.save()
        return event

    def assert_can_view(self, event, user):
        """Assert that the given event can be viewed by the given user."""
        self.assertTrue(
            event.can_user_view(self.user),
            'Should be able to view {} event'.format(
                event.get_restriction_display()))

    def assert_cannot_view(self, event, user):
        """Assert that the given event cannot be viewed by the given user."""
        self.assertFalse(
            event.can_user_view(self.user),
            'Should not be able to view {} event'.format(
                event.get_restriction_display()))

    def assert_can_sign_up(self, event, user):
        """Assert that the given event can be viewed by the given user."""
        self.assertTrue(
            event.can_user_sign_up(self.user),
            'Should be able to sign up for {} event'.format(
                event.get_restriction_display()))

    def assert_cannot_sign_up(self, event, user):
        """Assert that the given event can be viewed by the given user."""
        self.assertFalse(
            event.can_user_sign_up(self.user),
            'Should not be able to sign up for {} event'.format(
                event.get_restriction_display()))


class EventTest(EventTesting):
    def test_eventtype_get_by_natural_key(self):
        event_type_name = 'New Test Event Type'
        EventType(name=event_type_name).save()
        event_type = EventType.objects.get_by_natural_key(event_type_name)
        self.assertEqual(event_type.name, event_type_name)

    def test_eventtype_get_by_natural_key_does_not_exist(self):
        event_type = EventType.objects.get_by_natural_key(
            'New Test Event Type')
        self.assertIsNone(event_type)

    def test_get_upcoming(self):
        # Create an event that hasn't started yet:
        start_time = timezone.now() + datetime.timedelta(hours=2)
        end_time = start_time + datetime.timedelta(hours=3)
        event = self.create_event(start_time, end_time)
        upcoming_events = Event.objects.get_upcoming()
        self.assertIn(event, upcoming_events)

        # Make the event be set to occur in a future term
        future_term = Term(term=self.term.term, year=(self.term.year + 1),
                           current=False)
        future_term.save()
        event.term = future_term
        event.save()
        self.assertIn(
            event, Event.objects.get_upcoming(current_term_only=False))
        self.assertNotIn(
            event, Event.objects.get_upcoming(current_term_only=True))

    def test_is_upcoming(self):
        # Create an event that hasn't started yet:
        start_time = timezone.now() + datetime.timedelta(hours=2)
        end_time = start_time + datetime.timedelta(hours=3)
        event = self.create_event(start_time, end_time)
        self.assertTrue(event.is_upcoming())
        upcoming_events = Event.objects.get_upcoming()
        self.assertIn(event, upcoming_events)
        self.assertEqual(1, upcoming_events.count())

        event.cancelled = True
        event.save()
        self.assertFalse(event.is_upcoming())
        upcoming_events = Event.objects.get_upcoming()
        self.assertEqual(0, upcoming_events.count())

        # Create an event that has already started but hasn't ended yet:
        start_time = timezone.now() - datetime.timedelta(hours=2)
        end_time = timezone.now() + datetime.timedelta(hours=3)
        event = self.create_event(start_time, end_time,
                                  name='My Ongoing Event')
        self.assertTrue(event.is_upcoming())
        event.cancelled = True
        event.save()
        self.assertFalse(event.is_upcoming())

        # Create an event that has already ended:
        start_time = timezone.now() - datetime.timedelta(days=2)
        end_time = start_time + datetime.timedelta(hours=3)
        event = self.create_event(start_time, end_time,
                                  name='My Old Event')
        self.assertFalse(event.is_upcoming())
        event.cancelled = True
        event.save()
        self.assertFalse(event.is_upcoming())

    def test_is_multiday(self):
        start_time = datetime.datetime(2015, 3, 14, 9, 26, 53, 59)
        start_time = timezone.make_aware(start_time,
                                         timezone.get_current_timezone())
        end_time = start_time + datetime.timedelta(days=1)
        event = self.create_event(start_time, end_time,
                                  name='My Multiday Event')
        self.assertTrue(event.is_multiday())

        end_time = start_time + datetime.timedelta(weeks=1)
        event = self.create_event(start_time, end_time,
                                  name='My Weeklong Event')
        self.assertTrue(event.is_multiday())

        # Create a very long event that does not span more than one day
        start_time = start_time.replace(hour=0, minute=1)
        end_time = start_time + datetime.timedelta(hours=23, minutes=50)
        event = self.create_event(start_time, end_time,
                                  name='My Non-multiday Event')
        self.assertFalse(event.is_multiday())

    def test_get_user_viewable(self):
        # self.user is just an ordinary user with no groups or special
        # permissions, so they should be able to view public, open, and
        # candidate events, but not member and officer events
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        event_public = self.create_event(
            start_time, end_time, restriction=Event.PUBLIC)
        event_open = self.create_event(
            start_time, end_time, restriction=Event.OPEN)
        event_candidate = self.create_event(
            start_time, end_time, restriction=Event.CANDIDATE)
        event_member = self.create_event(
            start_time, end_time, restriction=Event.MEMBER)
        event_officer = self.create_event(
            start_time, end_time, restriction=Event.OFFICER)

        visible_events = Event.objects.get_user_viewable(self.user)
        expected_events = [event_public, event_open, event_candidate]
        self.assertQuerysetEqual(visible_events,
                                 [repr(event) for event in expected_events],
                                 ordered=False)

        # Make this user a candidate, and view the permissions should stay
        # the same
        Candidate(user=self.user, term=self.term).save()
        visible_events = Event.objects.get_user_viewable(self.user)
        self.assertQuerysetEqual(visible_events,
                                 [repr(event) for event in expected_events],
                                 ordered=False)

        # Make this user an officer, and they should be able to see all
        # events
        Officer(user=self.user, position=self.committee, term=self.term).save()
        visible_events = Event.objects.get_user_viewable(self.user)
        expected_events.extend([event_member, event_officer])
        self.assertQuerysetEqual(visible_events,
                                 [repr(event) for event in expected_events],
                                 ordered=False)

    def test_can_user_view(self):
        # self.user is just an ordinary user with no groups or special
        # permissions, so they should be able to view public, open, and
        # candidate events, but not member and officer events
        restrictions = [Event.PUBLIC, Event.OPEN, Event.CANDIDATE,
                        Event.MEMBER, Event.OFFICER]

        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        event = self.create_event(start_time, end_time)
        for restriction in restrictions:
            event.restriction = restriction
            event.save()
            if restriction in Event.VISIBLE_TO_EVERYONE:
                self.assert_can_view(event, self.user)
            else:
                self.assert_cannot_view(event, self.user)

        # Make this user a candidate, and view the permissions should stay
        # the same
        Candidate(user=self.user, term=self.term).save()
        for restriction in restrictions:
            event.restriction = restriction
            event.save()
            if restriction in Event.VISIBLE_TO_EVERYONE:
                self.assert_can_view(event, self.user)
            else:
                self.assert_cannot_view(event, self.user)

        # Make this user an officer, and they should be able to see all
        # events
        Officer(user=self.user, position=self.committee, term=self.term).save()
        for restriction in restrictions:
            event.restriction = restriction
            event.save()
            self.assert_can_view(event, self.user)

    def test_can_user_sign_up(self):
        # self.user is just an ordinary user with no groups or special
        # permissions, so the user should only be able to sign up for public
        # events
        restrictions = [Event.PUBLIC, Event.OPEN, Event.CANDIDATE,
                        Event.MEMBER, Event.OFFICER]

        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        event = self.create_event(start_time, end_time)
        for restriction in restrictions:
            event.restriction = restriction
            event.save()
            if restriction == Event.PUBLIC:
                self.assert_can_sign_up(event, self.user)
            else:
                self.assert_cannot_sign_up(event, self.user)

        # Make this user a candidate, so the user should be able to sign up
        # for public and candidate events
        Candidate(user=self.user, term=self.term).save()
        for restriction in restrictions:
            event.restriction = restriction
            event.save()
            if restriction == Event.PUBLIC or restriction == Event.CANDIDATE:
                self.assert_can_sign_up(event, self.user)
            else:
                self.assert_cannot_sign_up(event, self.user)

        # Make this user an officer, so the user should be able to sign up
        # for all events except open events (which don't allow signups)
        Officer(user=self.user, position=self.committee, term=self.term).save()
        for restriction in restrictions:
            event.restriction = restriction
            event.save()
            if restriction == Event.OPEN:
                self.assert_cannot_sign_up(event, self.user)
            else:
                self.assert_can_sign_up(event, self.user)

    def test_user_multiple_sign_ups(self):
        """Multiple signups don't create multiple instances of EventSignUp."""
        # Create event
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        event = self.create_event(start_time, end_time,
                                  restriction=Event.PUBLIC)
        event.signup_limit = 2
        event.save()
        self.assertIsNotNone(event.pk)

        self.assertTrue(event.can_user_sign_up(self.user))
        self.assertTrue(self.client.login(
            username=self.user.username, password='testofficerpw'))

        signup_url = reverse('events:signup', kwargs={'event_pk': event.pk})
        signup_data = {'num_guests': 0, 'driving': 0, 'unsignup': False}
        self.assertEqual(0, EventSignUp.objects.filter(event=event).count())

        # Sign-up once. Ensure success
        response_1 = self.client.post(signup_url, signup_data, follow=True)
        self.assertEqual(200, response_1.status_code)
        self.assertEqual(1, EventSignUp.objects.filter(event=event).count())
        r1_get = self.client.get('/')
        self.assertEqual('Signup successful!',
                         str(list(r1_get.context['messages'])[0]))

        # Sign-up twice. Ensure update
        response_2 = self.client.post(signup_url, signup_data, follow=True)
        self.assertEqual(200, response_2.status_code)
        self.assertEqual(1, EventSignUp.objects.filter(event=event).count())
        r2_get = self.client.get('/')
        self.assertEqual('Signup updated!',
                         str(list(r2_get.context['messages'])[0]))

    def test_list_date(self):
        start_time = datetime.datetime(2015, 3, 14, 9, 26, 53, 59)
        start_time = timezone.make_aware(start_time,
                                         timezone.get_current_timezone())
        end_time = start_time + datetime.timedelta(hours=2)
        event = self.create_event(start_time, end_time,
                                  name='My Pi Day Event')
        self.assertEqual(event.list_date(), 'Sat, Mar 14')

        end_time = start_time + datetime.timedelta(days=1)
        event.end_datetime = end_time
        event.save()
        self.assertEqual(event.list_date(), 'Sat, Mar 14 - Sun, Mar 15')

        end_time = start_time + datetime.timedelta(days=3)
        event.end_datetime = end_time
        event.save()
        self.assertEqual(event.list_date(), 'Sat, Mar 14 - Tue, Mar 17')

    def test_list_time(self):
        start_time = datetime.datetime(2015, 3, 14, 9, 26, 53, 59)
        start_time = timezone.make_aware(start_time,
                                         timezone.get_current_timezone())
        end_time = start_time + datetime.timedelta(hours=2, minutes=6)
        event = self.create_event(start_time, end_time,
                                  name='My Pi Day Event')
        self.assertEqual(event.list_time(), '9:26 AM - 11:32 AM')

        end_time = start_time + datetime.timedelta(hours=11, minutes=2)
        event.end_datetime = end_time
        event.save()
        self.assertEqual(event.list_time(), '9:26 AM - 8:28 PM')

        end_time = start_time + datetime.timedelta(days=1, hours=11, minutes=2)
        event.end_datetime = end_time
        event.save()
        self.assertEqual(event.list_time(), '(3/14) 9:26 AM - (3/15) 8:28 PM')

        start_time = start_time.replace(hour=15, minute=14)
        end_time = start_time + datetime.timedelta(days=3, hours=5, minutes=29)
        event.start_datetime = start_time
        event.end_datetime = end_time
        event.save()
        self.assertEqual(event.list_time(), '(3/14) 3:14 PM - (3/17) 8:43 PM')

        event.end_datetime = event.start_datetime
        event.save()
        self.assertEqual(event.list_time(), 'TBA')

    def test_view_datetime(self):
        start_time = datetime.datetime(2015, 3, 14, 9, 26, 53, 59)
        start_time = timezone.make_aware(start_time,
                                         timezone.get_current_timezone())
        end_time = start_time + datetime.timedelta(hours=2, minutes=4)
        event = self.create_event(start_time, end_time,
                                  name='My Pi Day Event')
        self.assertEqual(event.view_datetime(),
                         'Sat, Mar 14 9:26 AM to 11:30 AM')

        end_time = start_time + datetime.timedelta(hours=11, minutes=2)
        event.end_datetime = end_time
        event.save()
        self.assertEqual(event.view_datetime(),
                         'Sat, Mar 14 9:26 AM to 8:28 PM')

        end_time = start_time + datetime.timedelta(days=1, hours=11, minutes=2)
        event.end_datetime = end_time
        event.save()
        self.assertEqual(event.view_datetime(),
                         'Sat, Mar 14 9:26 AM to Sun, Mar 15 8:28 PM')

        start_time = start_time.replace(hour=15, minute=14)
        end_time = start_time + datetime.timedelta(days=3, hours=5, minutes=29)
        event.start_datetime = start_time
        event.end_datetime = end_time
        event.save()
        self.assertEqual(event.view_datetime(),
                         'Sat, Mar 14 3:14 PM to Tue, Mar 17 8:43 PM')

        event.end_datetime = event.start_datetime
        event.save()
        self.assertEqual(event.view_datetime(), 'Sat, Mar 14 Time TBA')

    def test_string(self):
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        event = self.create_event(start_time, end_time,
                                  name=u'Test Unicode Name \u03a4\u0392\u03a0')
        # Unicode is TBP in Greek Capital Unicode
        event.description = (u'Some unicode description \u03a4\u0392\u03a0.\n'
                             u'more unicode \uf8ff')
        event.save()
        signup = EventSignUp(name='Edward', event=event, num_guests=0)
        signup.save()
        expected_str = u'{name} has signed up for {event_name}'.format(
            name=signup.name, event_name=event.name)
        self.assertEqual(expected_str, signup)

        signup.user = self.user
        signup.save()
        expected_str = u'{name} has signed up for {event_name}'.format(
            name=self.user.get_full_name(), event_name=event.name)
        self.assertEqual(expected_str, signup)

        signup.num_guests = 1
        signup.save()
        expected_str = u'{name} (+1) has signed up for {event_name}'.format(
            name=self.user.get_full_name(), event_name=event.name)
        self.assertEqual(expected_str, signup)

        signup.num_guests = 2
        signup.save()
        expected_str = u'{name} (+2) has signed up for {event_name}'.format(
            name=self.user.get_full_name(), event_name=event.name)
        self.assertEqual(expected_str, signup)

        signup.unsignup = True
        signup.save()
        expected_str = u'{name} (+2) has unsigned up for {event_name}'.format(
            name=self.user.get_full_name(), event_name=event.name)
        self.assertEqual(expected_str, signup)

        # Test that gcal url does not raise errors. Don't test expected url.
        event.get_gcal_event_url()

    def test_project_report_attendance(self):
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        event = self.create_event(start_time, end_time)
        project_report = ProjectReport.objects.create(
            term=self.term,
            date=datetime.date.today(),
            title='Test project report',
            author=self.user,
            committee=self.committee)
        event.project_report = project_report
        event.save()

        # self.user is neither an officer, a candidate, nor a member, so
        # recording attendance should not affect any attendance list
        attendance = EventAttendance.objects.create(
            user=self.user, event=event)
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

        attendance.delete()
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

        # Make this user a candidate, so recording attendance should affect
        # the candidate list
        Candidate(user=self.user, term=self.term).save()
        attendance = EventAttendance.objects.create(
            user=self.user, event=event)
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(
            project_report.candidate_list.all(), [repr(self.user)])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

        attendance.delete()
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

        # Make this user a member, so recording attendance should affect
        # the member list
        self.user.studentorguserprofile.initiation_term = self.term
        self.user.save()
        attendance = EventAttendance.objects.create(
            user=self.user, event=event)
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(
            project_report.member_list.all(), [repr(self.user)])

        attendance.delete()
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

        # Make this user an officer, so recording attendance should affect the
        # officer list
        Officer(user=self.user, position=self.committee, term=self.term).save()
        attendance = EventAttendance.objects.create(
            user=self.user, event=event)
        self.assertQuerysetEqual(
            project_report.officer_list.all(), [repr(self.user)])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

        attendance.delete()
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

    def test_multiple_project_report_attendances(self):
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(hours=2)
        event = self.create_event(start_time, end_time)
        project_report = ProjectReport.objects.create(
            term=self.term,
            date=datetime.date.today(),
            title='Test project report',
            author=self.user,
            committee=self.committee)
        event.project_report = project_report
        event.save()

        candidate1 = get_user_model().objects.create_user(
            username='fakecandidate1',
            email='it@tbp.berkeley.edu',
            password='candidate',
            first_name='Fake',
            last_name='Candidate1')
        Candidate(user=candidate1, term=self.term).save()
        candidate2 = get_user_model().objects.create_user(
            username='fakecandidate2',
            email='it@tbp.berkeley.edu',
            password='candidate',
            first_name='Fake',
            last_name='Candidate2')
        Candidate(user=candidate2, term=self.term).save()
        officer = get_user_model().objects.create_user(
            username='fakeofficer',
            email='it@tbp.berkeley.edu',
            password='officer',
            first_name='Fake',
            last_name='Officer')
        Officer(user=officer, position=self.committee, term=self.term).save()
        member = self.user
        StudentOrgUserProfile(user=member, initiation_term=self.term).save()
        member.save()

        officer_attendance = EventAttendance.objects.create(
            user=officer, event=event)
        self.assertQuerysetEqual(
            project_report.officer_list.all(), [repr(officer)])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

        candidate1_attendance = EventAttendance.objects.create(
            user=candidate1, event=event)
        self.assertQuerysetEqual(
            project_report.officer_list.all(), [repr(officer)])
        self.assertQuerysetEqual(
            project_report.candidate_list.all(), [repr(candidate1)])
        self.assertQuerysetEqual(project_report.member_list.all(), [])

        member_attendance = EventAttendance.objects.create(
            user=member, event=event)
        self.assertQuerysetEqual(
            project_report.officer_list.all(), [repr(officer)])
        self.assertQuerysetEqual(
            project_report.candidate_list.all(), [repr(candidate1)])
        self.assertQuerysetEqual(
            project_report.member_list.all(), [repr(member)])

        candidate2_attendance = EventAttendance.objects.create(
            user=candidate2, event=event)
        self.assertQuerysetEqual(
            project_report.officer_list.all(), [repr(officer)])
        self.assertQuerysetEqual(
            project_report.candidate_list.all(),
            [repr(candidate1), repr(candidate2)],
            ordered=False)
        self.assertQuerysetEqual(
            project_report.member_list.all(), [repr(member)])

        candidate1_attendance.delete()
        self.assertQuerysetEqual(
            project_report.officer_list.all(), [repr(officer)])
        self.assertQuerysetEqual(
            project_report.candidate_list.all(), [repr(candidate2)])
        self.assertQuerysetEqual(
            project_report.member_list.all(), [repr(member)])

        officer_attendance.delete()
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(
            project_report.candidate_list.all(), [repr(candidate2)])
        self.assertQuerysetEqual(
            project_report.member_list.all(), [repr(member)])

        candidate2_attendance.delete()
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(
            project_report.member_list.all(), [repr(member)])

        member_attendance.delete()
        self.assertQuerysetEqual(project_report.officer_list.all(), [])
        self.assertQuerysetEqual(project_report.candidate_list.all(), [])
        self.assertQuerysetEqual(project_report.member_list.all(), [])


class EventFormsTest(EventTesting):
    def setUp(self):
        # Call superclass setUp first:
        EventTesting.setUp(self)

        start_datetime = timezone.now()
        start_datetime = start_datetime.replace(
            month=3, day=14, year=2015, hour=9, minute=26)
        end_datetime = start_datetime + datetime.timedelta(hours=2)
        self.event = self.create_event(start_datetime, end_datetime)

        # Create string formats for start and end times:
        # Note that we separate date and time into separate strings to be used
        # as input to the SplitDateTimeWidget for the DateTimeField, since
        # the widget splits input into two separate form fields.
        self.start_date = '{:%Y-%m-%d}'.format(self.event.start_datetime)
        self.start_time = '{:%I:%M%p}'.format(self.event.start_datetime)
        self.end_date = '{:%Y-%m-%d}'.format(self.event.end_datetime)
        self.end_time = '{:%I:%M%p}'.format(self.event.end_datetime)

    def create_basic_event_form(self, extra_fields=None):
        """Returns an event form with some of the common fields filled out.

        The extra_fields kwarg is used to pass a dictionary of additional
        fields to include when creating the form.  Note that without specifying
        some additional fields, the form returned is not a valid form, as event
        start and end times are required fields.
        """
        fields = {'name': self.event.name,
                  'event_type': self.event.event_type.pk,
                  'term': self.event.term.pk,
                  'contact': self.user.pk,
                  'committee': self.event.committee.pk,
                  'restriction': Event.OFFICER,
                  'location': self.event.location,
                  'requirements_credit': self.event.requirements_credit,
                  'max_guests_per_person': self.event.max_guests_per_person,
                  'signup_limit': self.event.signup_limit}
        if extra_fields:
            fields.update(extra_fields)
        return EventForm(fields)

    def test_clean(self):
        form = EventForm()
        # Blank form should be invalid:
        self.assertFalse(form.is_valid())

        # Create a form with all fields logically/properly filled out:
        form = self.create_basic_event_form(
            {'start_datetime_0': self.start_date,
             'start_datetime_1': self.start_time,
             'end_datetime_0': self.end_date,
             'end_datetime_1': self.end_time})
        self.assertTrue(form.is_valid())

        # Create an invalid form with invalid input for start and/or end time:
        start_error = ['Your start time is not in the proper format.']
        end_error = ['Your end time is not in the proper format.']
        end_before_start = ['Your event is scheduled to end before it starts.']
        # Missing start and end times:
        form = self.create_basic_event_form()
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('start_datetime', None),
                         start_error)
        self.assertEqual(form.errors.get('end_datetime', None),
                         end_error)

        # Missing start time:
        form = self.create_basic_event_form(
            {'end_datetime_0': self.end_date,
             'end_datetime_1': self.end_time})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('start_datetime', None),
                         start_error)
        self.assertIsNone(form.errors.get('end_datetime', None))

        # Invalid (non-datetime) end time:
        # (Note that the same validation error will occur if end_datetime not
        # specified.)
        form = self.create_basic_event_form(
            {'start_datetime_0': self.start_date,
             'start_datetime_1': self.start_time,
             'end_datetime_0': 'not a date',
             'end_datetime_1': 'not a time'})
        self.assertFalse(form.is_valid())
        self.assertIsNone(form.errors.get('start_datetime', None))
        self.assertEqual(form.errors.get('end_datetime', None),
                         end_error)

        # Create a form with event end time before start time:
        form = self.create_basic_event_form(
            {'start_datetime_0': self.end_date,
             'start_datetime_1': self.end_time,
             'end_datetime_0': self.start_date,
             'end_datetime_1': self.start_time})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get('start_datetime', None),
                         end_before_start)
        self.assertEqual(form.errors.get('end_datetime', None),
                         end_before_start)

    def test_autocreate_project_report(self):
        """ Ensures that when an EventForm is saved, a project report
        corresponding to that event is created, depending on the needs_pr
        field.
        """
        # Create the fields for an Event, based on the event created in setUp,
        # simply with a different event name
        event_name_no_pr = 'My Event Without a PR'
        event_name_pr = 'My Event With a PR'
        fields = {'name': event_name_no_pr,
                  'event_type': self.event.event_type.pk,
                  'term': self.event.term.pk,
                  'contact': self.user.pk,
                  'committee': self.event.committee.pk,
                  'restriction': Event.OFFICER,
                  'location': self.event.location,
                  'requirements_credit': self.event.requirements_credit,
                  'max_guests_per_person': self.event.max_guests_per_person,
                  'signup_limit': self.event.signup_limit,
                  'start_datetime_0': self.start_date,
                  'start_datetime_1': self.start_time,
                  'end_datetime_0': self.end_date,
                  'end_datetime_1': self.end_time,
                  'needs_pr': False}

        # Ensure that saving the EventForm creates the event and that no
        # project report is created:
        EventForm(fields).save()
        event = get_object_or_none(Event, name=event_name_no_pr)
        self.assertIsNotNone(event)
        self.assertIsNone(event.project_report)
        self.assertFalse(ProjectReport.objects.all().exists())

        # Create event with form, requiring project report, and ensure PR
        # is created:
        fields.update({'name': event_name_pr,
                       'needs_pr': True})
        EventForm(fields).save()
        event = get_object_or_none(Event, name=event_name_pr)
        self.assertIsNotNone(event)
        self.assertTrue(ProjectReport.objects.all().exists())
        project_report = ProjectReport.objects.all()[0]

        # Check the properties of both the event and project report to ensure
        # that they were saved and match our form
        self.assertEqual(event.name, event_name_pr)
        self.assertEqual(project_report.title, event_name_pr)

        self.assertEqual(event.start_datetime.date(),
                         self.event.start_datetime.date())
        self.assertEqual(project_report.date,
                         self.event.start_datetime.date())

        self.assertEqual(event.contact, self.user)
        self.assertEqual(project_report.author, self.user)

        self.assertEqual(event.term, self.event.term)
        self.assertEqual(project_report.term, self.event.term)

        self.assertEqual(project_report, event.project_report)

    def test_form_modifying_project_report(self):
        """ Ensures that when an EventForm is saved and a project report (PR)
        already exists for that event, that the PR is updated if the event
        still needs it or the PR is deleted if not.
        """
        # Fill out the form for the existing event and require a PR:
        fields = {'name': self.event.name,
                  'event_type': self.event.event_type.pk,
                  'term': self.event.term.pk,
                  'contact': self.user.pk,
                  'committee': self.event.committee.pk,
                  'restriction': Event.OFFICER,
                  'location': self.event.location,
                  'requirements_credit': self.event.requirements_credit,
                  'max_guests_per_person': self.event.max_guests_per_person,
                  'signup_limit': self.event.signup_limit,
                  'start_datetime_0': self.start_date,
                  'start_datetime_1': self.start_time,
                  'end_datetime_0': self.end_date,
                  'end_datetime_1': self.end_time,
                  'needs_pr': True}
        form = EventForm(data=fields, instance=self.event)
        # Ensure that saving the EventForm for the existing event creates a PR:
        self.assertIsNone(self.event.project_report)  # No PR yet
        form.save()
        self.assertIsNotNone(self.event.project_report)  # Now has a PR
        project_report = ProjectReport.objects.all().get()
        self.assertEquals(self.event.project_report, project_report)
        self.assertEquals(self.event.name, project_report.title)

        # Ensure that saving a new version of the EventForm with an update to
        # an event field updates the existing event PR
        new_name = 'My New Event Name'
        fields.update({'name': new_name})
        form = EventForm(data=fields, instance=self.event)
        form.save()
        self.assertEquals(new_name, self.event.name)
        project_report = ProjectReport.objects.all().get()
        self.assertEquals(self.event.name, project_report.title)

        # Now modify the form to mark that a project report is not needed,
        # ensure that the PR is deleted when the form is saved
        fields.update({'needs_pr': False})
        form = EventForm(data=fields, instance=self.event)
        form.save()
        self.assertFalse(ProjectReport.objects.all().exists())
        self.assertIsNone(self.event.project_report)

    def setup_cancel_event(self, extra_fields=None, delete_pr=True):
        """ Creates a basic event and returns a cancellation form.

        The extra_fields kwarg is used to pass a dictionary of additional
        fields to include when creating the form. Note that an event name
        should be supplied to the extra args to allow for a valid event.
        """
        fields = {'event_type': self.event.event_type.pk,
                  'term': self.event.term.pk,
                  'contact': self.user.pk,
                  'committee': self.event.committee.pk,
                  'restriction': Event.OFFICER,
                  'location': self.event.location,
                  'requirements_credit': self.event.requirements_credit,
                  'max_guests_per_person': self.event.max_guests_per_person,
                  'signup_limit': self.event.signup_limit,
                  'start_datetime_0': self.start_date,
                  'start_datetime_1': self.start_time,
                  'end_datetime_0': self.end_date,
                  'end_datetime_1': self.end_time,
                  'needs_pr': False}
        d_fields = {'delete_report': True}
        no_d_fields = {'delete_report': False}
        if extra_fields:
            fields.update(extra_fields)
        EventForm(fields).save()
        if delete_pr:
            return EventCancelForm(d_fields)
        else:
            return EventCancelForm(no_d_fields)

    def test_cancel_event_no_pr(self):
        """ Ensure that a simple event with no project report is cancelled."""
        event_name_no_pr = 'My Event Without a PR'
        c_form = self.setup_cancel_event(
            extra_fields={'name': event_name_no_pr},
            delete_pr=False)
        event = get_object_or_none(Event, name=event_name_no_pr)
        self.assertIsNone(event.project_report)
        c_form.event = event
        # Call is_valid to put cleaned data for the test.
        self.assertTrue(c_form.is_valid())
        self.assertTrue(event.cancelled)

    def test_cancel_event_no_pr_del(self):
        """ Event cancellation should proceed smoothly if a delete is
        request with no project report.
        """
        event_name_no_pr_del = 'My Event Without a PR, Try Delete'
        c_form = self.setup_cancel_event(
            extra_fields={'name': event_name_no_pr_del},
            delete_pr=True)
        event = get_object_or_none(Event, name=event_name_no_pr_del)
        self.assertIsNone(event.project_report)
        c_form.event = event
        self.assertTrue(c_form.is_valid())
        self.assertTrue(event.cancelled)

    def test_cancel_event_pr_del(self):
        """ Ensure an event is cancelled and the project report is deleted."""
        event_name_pr_del = 'My Event With a PR to Delete'
        c_form = self.setup_cancel_event(
            extra_fields={'name': event_name_pr_del, 'needs_pr': True},
            delete_pr=True)
        event = get_object_or_none(Event, name=event_name_pr_del)
        self.assertIsNotNone(event.project_report)
        c_form.event = event
        self.assertTrue(c_form.is_valid())
        self.assertIsNone(event.project_report)
        self.assertTrue(event.cancelled)

    def test_cancel_event_pr_save(self):
        """ Ensure an event is cancelled but the project report is saved."""
        event_name_pr_save = 'My Event With a PR to Save'
        c_form = self.setup_cancel_event(
            extra_fields={'name': event_name_pr_save, 'needs_pr': True},
            delete_pr=False)
        event = get_object_or_none(Event, name=event_name_pr_save)
        c_form.event = event
        self.assertTrue(c_form.is_valid())
        self.assertIsNotNone(event.project_report)
        self.assertTrue(event.cancelled)
