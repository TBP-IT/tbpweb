import datetime
import random
import string

from django.contrib.auth import get_user_model
from django.core.files import File
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from achievements.models import Achievement
from achievements.models import AchievementIcon
from achievements.models import UserAchievement
from base.models import Officer
from base.models import OfficerPosition
from base.models import Term
from courses.models import CourseInstance
from events.models import Event
from events.models import EventAttendance
from events.models import EventType
from exams.models import Exam
from project_reports.models import ProjectReport
from shortcuts import get_object_or_none
from syllabi.models import Syllabus


class AchievementAssignmentTest(TestCase):
    fixtures = ['test/term.yaml']

    def setUp(self):
        self.sample_user = get_user_model().objects.create_user(
            username='test', password='test', email='test@tbp.berkeley.edu',
            first_name="Test", last_name="Test")
        self.achievement, _ = Achievement.objects.get_or_create(
            name='test_achievement', short_name='test',
            description='test', points=0, goal=0, privacy='public',
            category='feats')
        self.achievements = UserAchievement.objects.filter(
            user=self.sample_user)

        self.fa2009 = Term.objects.get(term=Term.FALL, year='2009')
        self.sp2010 = Term.objects.get(term=Term.SPRING, year='2010')
        self.fa2010 = Term.objects.get(term=Term.FALL, year='2010')

    def test_assignment(self):
        # test to see that assigning the achievement creates an achievement
        # object in the database
        self.assertEqual(self.achievements.filter(
            achievement__short_name='test').count(), 0)
        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='test').count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='test', acquired=True).count(), 0)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='test', acquired=True).count(), 0)
        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='test', acquired=True).count(), 1)

    def test_update(self):
        # test to see that an achievement can be reset to not acquired and
        # that progress can be updated successfully
        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=True)
        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=False, progress=1)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='test', acquired=True).count(), 0)

        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=False, progress=2)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='test', acquired=True).count(), 0)
        user_achievement = UserAchievement.objects.get(
            achievement__short_name='test', user=self.sample_user)
        self.assertEqual(user_achievement.progress, 2)

    def test_first_term_stays_with_achievement(self):
        # test to make sure that getting the achievement in two different
        # semesters will keep the term as the first term in which the user
        # obtained it.

        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=False, term=self.fa2009)
        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=True, term=self.sp2010)

        # since the first achievement was just progress, the term will
        # be the first term where it was acquired - spring 2010
        self.assertEqual(self.achievements.filter(term=self.sp2010).count(), 1)

        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=True, term=self.fa2010)
        # since the achievement has already been acquired earlier, it
        # should retain the original term
        self.assertEqual(self.achievements.filter(term=self.sp2010).count(), 1)
        self.assertEqual(self.achievements.filter(term=self.fa2010).count(), 0)

    def test_terms_after_acquiring_dont_overwrite(self):
        # test to ensure that after receiving an achievement it will not be
        # overwritten if progress is obtained in a different semester

        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=True, term=self.sp2010)

        Achievement.objects.get(short_name='test').assign(
            self.sample_user, acquired=False, progress=1, term=self.fa2010)
        # since the achievement was acquired in a previous semester, it should
        # not be overwritten by progress acquired in another term
        self.assertEqual(self.achievements.filter(term=self.sp2010).count(), 1)
        self.assertEqual(self.achievements.filter(acquired=True).count(), 1)


class EventAchievementsTest(TestCase):
    fixtures = ['achievement.yaml',
                'officer_position.yaml',
                'test/term.yaml']

    def setUp(self):
        self.sample_user = get_user_model().objects.create_user(
            username='test', password='test', email='test@tbp.berkeley.edu',
            first_name="Test", last_name="Test")
        self.achievements = UserAchievement.objects.filter(
            user=self.sample_user)

        self.sp2012 = Term.objects.get(term=Term.SPRING, year='2012')
        self.fa2012 = Term.objects.get(term=Term.FALL, year='2012')
        self.sp2013 = Term.objects.get(term=Term.SPRING, year='2013')
        self.fa2013 = Term.objects.get(term=Term.FALL, year='2013')

        self.bent, _ = EventType.objects.get_or_create(name="Bent Polishing")
        self.big_social, _ = EventType.objects.get_or_create(name="Big Social")
        self.prodev, _ = EventType.objects.get_or_create(
            name="Professional Development")
        self.service, _ = EventType.objects.get_or_create(
            name="Community Service")
        self.efutures, _ = EventType.objects.get_or_create(name="E Futures")
        self.fun, _ = EventType.objects.get_or_create(name="Fun")
        self.meeting, _ = EventType.objects.get_or_create(name="Meeting")
        self.info, _ = EventType.objects.get_or_create(name="Infosession")

    def create_event(self, event_type, name=None, term=None, attendance=True):
        if name is None:
            name = ''.join(
                random.choice(string.ascii_uppercase) for x in range(6))
        if term is None:
            term = self.sp2013

        event, _ = Event.objects.get_or_create(
            name=name,
            contact=self.sample_user,
            term=term,
            location="TBD",
            event_type=event_type,
            start_datetime=timezone.now(),
            end_datetime=timezone.now(),
            committee=OfficerPosition.objects.first())

        if attendance:
            EventAttendance.objects.get_or_create(event=event,
                                                  user=self.sample_user)

        return event

    def create_many_events(self, number, event_type, term=None,
                           attendance=True):
        if term is None:
            term = self.sp2013

        events = [Event(
            name='Event{:03d}'.format(i),
            event_type=event_type,
            term=term,
            contact=self.sample_user,
            location="TBD",
            start_datetime=timezone.now(),
            end_datetime=timezone.now(),
            committee=OfficerPosition.objects.first())
            for i in range(number)]

        Event.objects.bulk_create(events)

        if attendance:
            created_events = Event.objects.order_by('-created')[:number]
            attendances = [EventAttendance(user=self.sample_user, event=event)
                           for event in created_events]
            EventAttendance.objects.bulk_create(attendances)

    def test_25_lifetime_events(self):
        """Achievement for 25 lifetime events is obtained after 25th event.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend025events').count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend050events').count(), 0)

        self.create_many_events(23, event_type=self.fun, term=self.sp2012)
        self.create_event(event_type=self.fun, term=self.sp2012)

        twentyfive_achievement = UserAchievement.objects.get(
            achievement__short_name='attend025events', user=self.sample_user)
        self.assertFalse(twentyfive_achievement.acquired)
        self.assertEqual(twentyfive_achievement.progress, 24)

        self.create_event(event_type=self.fun, term=self.sp2012)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend025events',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend050events',
            acquired=False).count(), 1)

    def test_50_lifetime_events(self):
        """Achievement for 50 lifetime events is obtained after 50th event.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend050events').count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend078events').count(), 0)

        self.create_many_events(48, event_type=self.fun, term=self.sp2012)
        self.create_event(event_type=self.fun, term=self.sp2012)

        fifty_achievement = UserAchievement.objects.get(
            achievement__short_name='attend050events', user=self.sample_user)
        self.assertFalse(fifty_achievement.acquired)
        self.assertEqual(fifty_achievement.progress, 49)

        self.create_event(event_type=self.fun, term=self.sp2012)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend050events',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend078events',
            acquired=False).count(), 1)

    def test_78_lifetime_events(self):
        """Achievement for 78 lifetime events is obtained after the 78th event.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend078events').count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend100events').count(), 0)

        self.create_many_events(76, event_type=self.fun, term=self.sp2012)
        self.create_event(event_type=self.fun, term=self.sp2012)

        seventyeight_achievement = UserAchievement.objects.get(
            achievement__short_name='attend078events', user=self.sample_user)
        self.assertFalse(seventyeight_achievement.acquired)
        self.assertEqual(seventyeight_achievement.progress, 77)

        self.create_event(event_type=self.fun, term=self.sp2012)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend078events',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend100events',
            acquired=False).count(), 1)

    def test_100_lifetime_events(self):
        """Achievement for 100 lifetime events is obtained after 100th event.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend100events').count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend150events').count(), 0)

        self.create_many_events(98, event_type=self.fun, term=self.sp2012)
        self.create_event(event_type=self.fun, term=self.sp2012)

        hundred_achievement = UserAchievement.objects.get(
            achievement__short_name='attend100events', user=self.sample_user)
        self.assertFalse(hundred_achievement.acquired)
        self.assertEqual(hundred_achievement.progress, 99)

        self.create_event(event_type=self.fun, term=self.sp2012)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend100events',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend150events',
            acquired=False).count(), 1)

    def test_150_lifetime_events(self):
        """Achievement for 150 lifetime events is obtained after 150th event.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend150events').count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend200events').count(), 0)

        self.create_many_events(148, event_type=self.fun, term=self.sp2012)
        self.create_event(event_type=self.fun, term=self.sp2012)

        onefifty_achievement = UserAchievement.objects.get(
            achievement__short_name='attend150events', user=self.sample_user)
        self.assertFalse(onefifty_achievement.acquired)
        self.assertEqual(onefifty_achievement.progress, 149)

        self.create_event(event_type=self.fun, term=self.sp2012)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend150events',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend200events',
            acquired=False).count(), 1)

    def test_200_lifetime_events(self):
        """Achievement for 200 lifetime events is obtained after 200th event.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend200events').count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend300events').count(), 0)

        self.create_many_events(198, event_type=self.fun, term=self.sp2012)
        self.create_event(event_type=self.fun, term=self.sp2012)

        twohundred_achievement = UserAchievement.objects.get(
            achievement__short_name='attend200events', user=self.sample_user)
        self.assertFalse(twohundred_achievement.acquired)
        self.assertEqual(twohundred_achievement.progress, 199)

        self.create_event(event_type=self.fun, term=self.sp2012)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend200events',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend300events',
            acquired=False).count(), 1)

    def test_300_lifetime_events(self):
        """Achievement for 300 lifetime events is obtained after 300th events.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend300events').count(), 0)

        self.create_many_events(298, event_type=self.fun, term=self.sp2012)
        self.create_event(event_type=self.fun, term=self.sp2012)

        threehundred_achievement = UserAchievement.objects.get(
            achievement__short_name='attend300events', user=self.sample_user)
        self.assertFalse(threehundred_achievement.acquired)
        self.assertEqual(threehundred_achievement.progress, 299)

        self.create_event(event_type=self.fun, term=self.sp2012)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend300events',
            acquired=True).count(), 1)

    def test_lifetime_events_with_different_terms(self):
        """Achievements for lifetime events can be obtained by attending
        events in multiple different semesters.
        """
        self.create_many_events(24, event_type=self.fun, term=self.sp2012)
        self.create_event(event_type=self.fun, term=self.fa2012)

        achievement = UserAchievement.objects.get(
            achievement__short_name='attend025events', user=self.sample_user)
        self.assertTrue(achievement.acquired)
        self.assertEqual(achievement.term, self.fa2012)

    def test_lifetime_events_backfill(self):
        """Achievements for lifetime event attendance are awarded for the 25th
        event attended in real life, not the 25th object added to the DB.
        """
        self.create_many_events(23, event_type=self.bent, term=self.sp2013)
        self.create_event(event_type=self.prodev, term=self.sp2013)
        achievement = UserAchievement.objects.get(
            achievement__short_name='attend025events', user=self.sample_user)
        self.assertEqual(achievement.progress, 24)

        self.create_event(name='Event025',
                          event_type=self.fun, term=self.sp2012)

        achievement = UserAchievement.objects.get(
            achievement__short_name='attend025events', user=self.sample_user)

        self.assertTrue(achievement.acquired)
        self.assertEqual(achievement.term, self.sp2013)

    def test_salad_bowl(self):
        """The achievement for attending one event of each type in a semester
        may be awarded after missing an event of one type if an event of the
        same type is attended later in the semester.
        """
        self.create_event(name='Fun', event_type=self.fun, attendance=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_each_type',
            acquired=True).count(), 0)

        self.create_event(name='Bent', event_type=self.bent)
        self.create_event(name='Service', event_type=self.service)
        self.create_event(name='ProDev', event_type=self.prodev)
        self.create_event(name='Meeting', event_type=self.meeting)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_each_type',
            acquired=True).count(), 0)

        self.create_event(name='Fun2', event_type=self.fun, attendance=True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_each_type',
            acquired=True).count(), 1)

    def test_event_type_achievement(self):
        """The achievement for attending all events of a certain type in one
        semester can be awarded by attending all fun events, for example, in
        a later semester after not attending all in a previous semester.
        """
        self.create_event(name='Fun1',
                          event_type=self.fun,
                          attendance=False,
                          term=self.sp2012)
        self.create_event(name='Fun2',
                          event_type=self.fun,
                          attendance=True,
                          term=self.sp2012)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_all_fun', acquired=True).count(), 0)

        self.create_event(name='Fun3',
                          event_type=self.fun,
                          attendance=True,
                          term=self.fa2012)
        achievement = UserAchievement.objects.get(
            achievement__short_name='attend_all_fun', user=self.sample_user)
        self.assertTrue(achievement.acquired)
        self.assertEqual(achievement.term, self.fa2012)

    def test_d15_achievement(self):
        """The achievement for attending District 15 Conference is given
        for a member who attends an event titled D15.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_d15', acquired=True).count(), 0)

        self.create_event(name="D16", event_type=self.meeting)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_d15', acquired=True).count(), 0)

        self.create_event(name="D15", event_type=self.meeting,
                          attendance=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_d15', acquired=True).count(), 0)

        self.create_event(name="D15", event_type=self.meeting)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_d15', acquired=True).count(), 1)

    def test_d15_alt(self):
        """The D15 achievement can also be given for attending an event titled
        District 15 Conference.
        """
        self.create_event(name="District 15 Conference", event_type=self.fun)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_d15', acquired=True).count(), 1)

    def test_d15_alt2(self):
        """The D15 achievement can also be given for attending an event that
        includes the string 'D 15', such as D 15 Convention.
        """
        self.create_event(name="D 15 Convention", event_type=self.big_social)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_d15', acquired=True).count(), 1)

    def test_natl_convention_achievement(self):
        """The achievement for attending National Convention is awarded for
        attending an event where the title includes the phrase:
        'National Convention'
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_convention',
            acquired=True).count(), 0)

        self.create_event(name="D15 Convention", event_type=self.fun)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_convention',
            acquired=True).count(), 0)

        self.create_event(name="National Convention", event_type=self.fun,
                          attendance=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_convention',
            acquired=True).count(), 0)

        self.create_event(name="National Convention", event_type=self.fun)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_convention',
            acquired=True).count(), 1)

    def test_envelope_stuffing_achievement(self):
        """The achievement for attending Envelope Stuffing is awarded for
        attending an event where the title includes the phrase:
        'Envelope Stuffing'
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_envelope_stuffing',
            acquired=True).count(), 0)

        self.create_event(name="Envelope Stuffing", event_type=self.fun,
                          attendance=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_envelope_stuffing',
            acquired=True).count(), 0)

        self.create_event(name="Envelop Stuffing", event_type=self.fun)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_envelope_stuffing',
            acquired=True).count(), 0)

        self.create_event(name="Envelope Stuffing", event_type=self.fun)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='attend_envelope_stuffing',
            acquired=True).count(), 1)

    def test_berkeley_explosion_achievement(self):
        """The achievement for attending the Berkeley Explosion CM is awarded
        only for attending an event titled exactly 'Candidate Meeting' in the
        Fall 2013 term.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='berkeley_explosion',
            acquired=True).count(), 0)

        self.create_event(name="Candidate Meeting", event_type=self.meeting,
                          term=self.sp2012)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='berkeley_explosion',
            acquired=True).count(), 0)

        self.create_event(name="Candidate Meeting 2", event_type=self.meeting,
                          term=self.fa2013)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='berkeley_explosion',
            acquired=True).count(), 0)

        self.create_event(name="Candidate Meeting", event_type=self.meeting,
                          term=self.fa2013, attendance=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='berkeley_explosion',
            acquired=True).count(), 0)

        self.create_event(name="Candidate Meeting", event_type=self.meeting,
                          term=self.fa2013, attendance=True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='berkeley_explosion',
            acquired=True).count(), 1)

    def test_alphabet_attendance_achievement(self):
        """The achievement for attending events with all the letters of the
        alphabet in the titles is awarded for such, ignoring capitalization.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='alphabet_attendance',
            acquired=True).count(), 0)

        self.create_event(name="abcdefghijklm", event_type=self.fun)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='alphabet_attendance',
            acquired=True).count(), 0)

        self.create_event(name="NOPqrstuvwxyZ", event_type=self.meeting,
                          attendance=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='alphabet_attendance',
            acquired=True).count(), 0)

        self.create_event(name="noPqRstuvWxyz", event_type=self.info,
                          attendance=True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='alphabet_attendance',
            acquired=True).count(), 1)


class CourseFileAchievementsTest(TestCase):
    fixtures = ['achievement.yaml',
                'test/course_instance.yaml']

    def setUp(self):
        self.sample_user = get_user_model().objects.create_user(
            username='test', password='test', email='test@tbp.berkeley.edu',
            first_name='Test', last_name='Test')
        self.achievements = UserAchievement.objects.filter(
            user=self.sample_user)

    def create_exam(self, exam_number, exam_type,
                    submitter=None, course_instance=None, verified=True):
        if course_instance is None:
            course_instance = CourseInstance.objects.first()

        test_file = open('test.txt', 'w+')
        test_file.write('This is a test file.')

        exam, _ = Exam.objects.get_or_create(
            course_instance=course_instance,
            submitter=submitter,
            exam_number=exam_number,
            exam_type=exam_type,
            file_ext='.pdf',
            verified=verified,
            exam_file=File(test_file))

        return exam

    def create_syllabus(self, submitter=None, course_instance=None,
                        verified=True):
        if course_instance is None:
            course_instance = CourseInstance.objects.first()

        syllabus_file = open('test.txt', 'w+')
        syllabus_file.write('This is a syllabus file for testing.')

        syllabus, _ = Syllabus.objects.get_or_create(
            course_instance=course_instance,
            submitter=submitter,
            file_ext='.pdf',
            verified=verified,
            syllabus_file=File(syllabus_file))

        return syllabus

    def test_exam_submission_progress(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            progress__gte=1).count(), 0)

        self.create_exam('mt1', 'exam', self.sample_user)

        ten_course_file_achievement = UserAchievement.objects.get(
            achievement__short_name='upload_10_course_files',
            user=self.sample_user)
        twentyfive_file_achievement = UserAchievement.objects.get(
            achievement__short_name='upload_25_course_files',
            user=self.sample_user)
        fifty_course_file_achievement = UserAchievement.objects.get(
            achievement__short_name='upload_50_course_files',
            user=self.sample_user)

        self.assertEqual(ten_course_file_achievement.progress, 1)
        self.assertEqual(twentyfive_file_achievement.progress, 1)
        self.assertEqual(fifty_course_file_achievement.progress, 1)

    def test_exam_with_blank_submitter(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            progress__gte=1).count(), 0)

        self.create_exam('mt1', 'exam')  # No submitter specified

        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            progress__gte=1).count(), 0)

    def test_10_exams(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            acquired=True).count(), 0)

        for i in range(1, 5):
            exam_number = 'mt{}'.format(i)
            self.create_exam(exam_number, 'exam', self.sample_user)
            self.create_exam(exam_number, 'soln', self.sample_user)

        self.create_exam('final', 'exam', self.sample_user)
        ten_course_file_achievement = UserAchievement.objects.get(
            achievement__short_name='upload_10_course_files')
        self.assertFalse(ten_course_file_achievement.acquired)
        self.assertEqual(ten_course_file_achievement.progress, 9)

        self.create_exam('final', 'soln', self.sample_user)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            acquired=True).count(), 1)

    def test_25_exams(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_25_course_files',
            acquired=True).count(), 0)

        courses = (CourseInstance.objects.get(pk=10000),
                   CourseInstance.objects.get(pk=20000),
                   CourseInstance.objects.get(pk=30000),
                   )

        for i in range(1, 5):
            exam_number = 'mt{}'.format(i)
            self.create_exam(exam_number, 'exam', self.sample_user, courses[0])
            self.create_exam(exam_number, 'soln', self.sample_user, courses[0])
            self.create_exam(exam_number, 'exam', self.sample_user, courses[1])
            self.create_exam(exam_number, 'soln', self.sample_user, courses[1])
            self.create_exam(exam_number, 'exam', self.sample_user, courses[2])
            self.create_exam(exam_number, 'soln', self.sample_user, courses[2])

        twentyfive_file_achievement = UserAchievement.objects.get(
            achievement__short_name='upload_25_course_files')
        self.assertFalse(twentyfive_file_achievement.acquired)
        self.assertEqual(twentyfive_file_achievement.progress, 24)

        self.create_exam('final', 'exam', self.sample_user)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_25_course_files',
            acquired=True).count(), 1)

    def test_50_exams(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_50_course_files',
            acquired=True).count(), 0)

        courses = (CourseInstance.objects.get(pk=10000),
                   CourseInstance.objects.get(pk=20000),
                   CourseInstance.objects.get(pk=30000),
                   CourseInstance.objects.get(pk=40000),
                   CourseInstance.objects.get(pk=50000),
                   )

        for i in range(5):
            for j in range(1, 5):
                exam_number = 'mt{}'.format(j)
                self.create_exam(
                    exam_number, 'exam', self.sample_user, courses[i])
                self.create_exam(
                    exam_number, 'soln', self.sample_user, courses[i])

            self.create_exam('final', 'exam', self.sample_user, courses[i])
            if i < 4:
                self.create_exam('final', 'soln', self.sample_user, courses[i])

        fifty_course_file_achievement = UserAchievement.objects.get(
            achievement__short_name='upload_50_course_files')
        self.assertFalse(fifty_course_file_achievement.acquired)
        self.assertEqual(fifty_course_file_achievement.progress, 49)

        self.create_exam('final', 'soln', self.sample_user, courses[4])
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_50_course_files',
            acquired=True).count(), 1)

    def test_unverified_exams(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            progress__gte=1).count(), 0)

        exam = self.create_exam(
            'final', 'exam', self.sample_user, verified=False)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            progress__gte=1).count(), 0)

        exam.verified = True
        exam.save()

        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            progress__gte=1).count(), 1)

    def test_exams_and_syllabi(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            acquired=True).count(), 0)

        for i in range(1, 5):
            exam_number = 'mt{}'.format(i)
            self.create_exam(exam_number, 'exam', self.sample_user)
            self.create_exam(exam_number, 'soln', self.sample_user)

        self.create_syllabus(self.sample_user)
        ten_course_file_achievement = UserAchievement.objects.get(
            achievement__short_name='upload_10_course_files')
        self.assertFalse(ten_course_file_achievement.acquired)
        self.assertEqual(ten_course_file_achievement.progress, 9)

        self.create_exam('final', 'soln', self.sample_user)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='upload_10_course_files',
            acquired=True).count(), 1)


class MetaAchievementsTest(TestCase):
    fixtures = ['achievement.yaml',
                'test/term.yaml']

    def setUp(self):
        self.sample_user = get_user_model().objects.create_user(
            username='test', password='test', email='test@tbp.berkeley.edu',
            first_name='Test', last_name='Test')
        self.achievements = UserAchievement.objects.filter(
            user=self.sample_user)

        self.sp2009 = Term.objects.get(term=Term.SPRING, year=2009)
        self.fa2009 = Term.objects.get(term=Term.FALL, year=2009)

    def test_15_achievements(self):
        other_achievements = Achievement.objects.exclude(
            short_name='acquire_15_achievements')

        self.assertEqual(self.achievements.filter(
            achievement__short_name='acquire_15_achievements',
            acquired=True).count(), 0)

        if len(other_achievements) >= 15:
            for i in range(0, 14):
                other_achievements[i].assign(self.sample_user, term=self.sp2009)

            self.assertEqual(self.achievements.filter(
                achievement__short_name='acquire_15_achievements',
                acquired=True).count(), 0)
            fifteen_achievement = UserAchievement.objects.get(
                achievement__short_name='acquire_15_achievements',
                user=self.sample_user)
            self.assertEqual(fifteen_achievement.progress, 14)

            other_achievements[14].assign(self.sample_user, term=self.sp2009)

            self.assertEqual(self.achievements.filter(
                achievement__short_name='acquire_15_achievements',
                acquired=True).count(), 1)

    def test_multiple_term_achievements(self):
        other_achievements = Achievement.objects.exclude(
            short_name='acquire_15_achievements')

        self.assertEqual(self.achievements.filter(
            achievement__short_name='acquire_15_achievements',
            acquired=True).count(), 0)

        if len(other_achievements) >= 15:
            for i in range(0, 10):
                other_achievements[i].assign(self.sample_user, term=self.sp2009)

            for i in range(10, 15):
                other_achievements[i].assign(self.sample_user, term=self.fa2009)

            self.assertEqual(self.achievements.filter(
                achievement__short_name='acquire_15_achievements',
                acquired=True).count(), 1)

            fifteen_achievement = UserAchievement.objects.get(
                achievement__short_name='acquire_15_achievements',
                user=self.sample_user)
            self.assertEqual(fifteen_achievement.term, self.fa2009)

    def test_unacquired_achievements(self):
        other_achievements = Achievement.objects.exclude(
            short_name='acquire_15_achievements')

        self.assertEqual(self.achievements.filter(
            achievement__short_name='acquire_15_achievements',
            acquired=True).count(), 0)

        if len(other_achievements) >= 15:
            for i in range(0, 15):
                other_achievements[i].assign(
                    self.sample_user, term=self.sp2009, acquired=False)

            self.assertEqual(self.achievements.filter(
                achievement__short_name='acquire_15_achievements',
                acquired=True).count(), 0)

            for i in range(-1, -16, -1):
                other_achievements[-i].assign(
                    self.sample_user, term=self.fa2009)

            self.assertEqual(self.achievements.filter(
                achievement__short_name='acquire_15_achievements',
                acquired=True).count(), 1)

    def test_icon_creation_achievement(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='create_01_icons',
            acquired=True).count(), 0)

        achievement = Achievement.objects.all()[0]
        achievement.icon, _ = AchievementIcon.objects.get_or_create(
            image='test.png', creator=self.sample_user)
        achievement.save()

        self.assertEqual(self.achievements.filter(
            achievement__short_name='create_01_icons',
            acquired=True).count(), 1)

    def test_five_icon_creation_achievement(self):
        self.assertEqual(self.achievements.filter(
            achievement__short_name='create_05_icons',
            acquired=True).count(), 0)

        for i in range(0, 4):
            achievement = Achievement.objects.all()[i]
            achievement.icon, _ = AchievementIcon.objects.get_or_create(
                image='test{}.png'.format(i), creator=self.sample_user)
            achievement.save()

        five_icon_achievement = UserAchievement.objects.get(
            achievement__short_name='create_05_icons',
            user=self.sample_user)

        self.assertEqual(five_icon_achievement.progress, 4)

        achievement = Achievement.objects.all()[4]
        achievement.icon, _ = AchievementIcon.objects.get_or_create(
            image='test4.png', creator=self.sample_user)
        achievement.save()

        self.assertEqual(self.achievements.filter(
            achievement__short_name='create_05_icons',
            acquired=True).count(), 1)

    def test_cots_mots_oots_achievement(self):
        """The achievement for winning COTS, MOTS, and OOTS is given when the
        user has acquired the three corresponding achievements.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='cots_mots_oots',
            acquired=True).count(), 0)

        cots_achievement = get_object_or_none(Achievement, short_name='cots')
        mots_achievement = get_object_or_none(Achievement, short_name='mots')
        oots_achievement = get_object_or_none(Achievement, short_name='oots')

        # assign cots and oots and check that achievement is not given
        cots_achievement.assign(self.sample_user)
        oots_achievement.assign(self.sample_user)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='cots_mots_oots',
            acquired=True).count(), 0)

        # assign mots and achievement should be assigned
        mots_achievement.assign(self.sample_user)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='cots_mots_oots',
            acquired=True).count(), 1)


class OfficerAchievementsTest(TestCase):
    fixtures = ['achievement.yaml',
                'officer_position.yaml',
                'test/term.yaml']

    def setUp(self):
        self.sample_user = get_user_model().objects.create_user(
            username='test', password='test', email='test@tbp.berkeley.edu',
            first_name="Test", last_name="Test")
        self.achievements = UserAchievement.objects.filter(
            user=self.sample_user)

        self.sp2009 = Term.objects.get(term=Term.SPRING, year=2009)
        self.fa2009 = Term.objects.get(term=Term.FALL, year=2009)
        self.sp2010 = Term.objects.get(term=Term.SPRING, year=2010)
        self.fa2010 = Term.objects.get(term=Term.FALL, year=2010)
        self.sp2011 = Term.objects.get(term=Term.SPRING, year=2011)
        self.fa2011 = Term.objects.get(term=Term.FALL, year=2011)
        self.sp2012 = Term.objects.get(term=Term.SPRING, year=2012)
        self.fa2012 = Term.objects.get(term=Term.FALL, year=2012)
        self.sp2013 = Term.objects.get(term=Term.SPRING, year=2013)
        self.fa2013 = Term.objects.get(term=Term.FALL, year=2013)

        self.house_leader = OfficerPosition.objects.get(
            short_name='house-leaders')
        self.historian = OfficerPosition.objects.get(short_name='historian')
        self.infotech = OfficerPosition.objects.get(short_name='it')
        self.vicepres = OfficerPosition.objects.get(short_name='vp')
        self.president = OfficerPosition.objects.get(short_name='president')

    def create_officer(self, user, position, term=None, is_chair=False):
        if term is None:
            term = self.fa2013
        Officer.objects.get_or_create(user=user, position=position, term=term,
                                      is_chair=is_chair)

    def test_number_of_officer_semesters(self):
        # first officer semester
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester01').count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester08').count(), 0)
        self.create_officer(self.sample_user, self.historian, self.sp2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester01').count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester08').count(), 1)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester01',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester02',
            acquired=True).count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester03',
            acquired=True).count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester04',
            acquired=True).count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester05',
            acquired=True).count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester06',
            acquired=True).count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester07',
            acquired=True).count(), 0)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester08',
            acquired=True).count(), 0)

    def test_second_officer_term(self):
        # second officer semester gets second achievement
        self.create_officer(self.sample_user, self.historian, self.sp2009)
        self.create_officer(self.sample_user, self.vicepres, self.fa2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester02',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester03',
            acquired=True).count(), 0)
        threeachievement = UserAchievement.objects.get(
            achievement__short_name='officersemester03', user=self.sample_user)
        self.assertEqual(threeachievement.progress, 2)

    def test_multiple_positions_same_semester(self):
        # two officer positions in same semester don't give achievement
        self.create_officer(self.sample_user, self.historian, self.fa2009)
        self.create_officer(self.sample_user, self.infotech, self.fa2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester01',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='officersemester02',
            acquired=True).count(), 0)
        fiveachievement = UserAchievement.objects.get(
            achievement__short_name='officersemester05', user=self.sample_user)
        self.assertEqual(fiveachievement.progress, 1)

    def test_chair_semester(self):
        # being chair gives chair1committee
        self.create_officer(self.sample_user, self.historian, self.sp2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='chair1committee', acquired=True).count(),
            0)

        self.create_officer(self.sample_user, self.infotech, self.sp2009, True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='chair1committee', acquired=True).count(),
            1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='chair2committees',
            acquired=False).count(), 1)

    def test_2_different_chair_semesters(self):
        # being chair of 2 different cmmitteees gives chair2committees
        self.create_officer(self.sample_user, self.historian, self.sp2009,
                            True)
        self.create_officer(self.sample_user, self.infotech, self.fa2009, True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='chair2committees',
            acquired=True).count(), 1)

    def test_twice_chair_of_same_committee(self):
        # being chair of the same committee twice doesn't give chair2committees
        self.create_officer(self.sample_user, self.infotech, self.fa2009, True)
        self.create_officer(self.sample_user, self.infotech, self.sp2010, True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='chair2committees',
            acquired=True).count(), 0)

    def test_three_diff_positions(self):
        # having three different officer positions confers the achievement
        self.create_officer(self.sample_user, self.infotech, self.fa2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='three_unique_positions',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.historian, self.sp2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='three_unique_positions',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.vicepres, self.fa2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='three_unique_positions',
            acquired=True).count(), 1)

    def test_three_same_positions(self):
        # having some repeats within the 3 does not confer achievement
        self.create_officer(self.sample_user, self.infotech, self.fa2009)
        self.create_officer(self.sample_user, self.infotech, self.sp2010)
        self.create_officer(self.sample_user, self.vicepres, self.fa2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='three_unique_positions',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.vicepres, self.sp2011)
        self.create_officer(self.sample_user, self.infotech, self.fa2011)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='three_unique_positions',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.historian, self.sp2012)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='three_unique_positions',
            acquired=True).count(), 1)

    def test_two_and_three_in_a_row(self):
        # being the same position 3x in a row confers both achievements
        self.create_officer(self.sample_user, self.infotech, self.sp2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='twice_same_position',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.infotech, self.fa2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='twice_same_position',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='thrice_same_position',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.infotech, self.sp2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='thrice_same_position',
            acquired=True).count(), 1)

    def test_broken_streaks(self):
        # an officer being the same position thrice but not in a row does
        # not confer the achievement
        self.create_officer(self.sample_user, self.infotech, self.sp2009)
        self.create_officer(self.sample_user, self.historian, self.fa2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='twice_same_position',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.infotech, self.sp2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='twice_same_position',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.infotech, self.fa2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='twice_same_position',
            acquired=True).count(), 1)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='thrice_same_position',
            acquired=True).count(), 0)

    def test_multiple_streaks(self):
        # an officer being two positions each twice in a row gets it
        self.create_officer(self.sample_user, self.infotech, self.sp2009)
        self.create_officer(self.sample_user, self.infotech, self.fa2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='two_repeated_positions',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.historian, self.sp2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='two_repeated_positions',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.historian, self.fa2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='two_repeated_positions',
            acquired=True).count(), 1)

    def test_same_committee_two_different_streaks(self):
        # two repeated positions need to be different positions
        self.create_officer(self.sample_user, self.infotech, self.sp2009)
        self.create_officer(self.sample_user, self.infotech, self.fa2009)
        self.create_officer(self.sample_user, self.historian, self.sp2010)
        self.create_officer(self.sample_user, self.infotech, self.fa2010)
        self.create_officer(self.sample_user, self.infotech, self.sp2011)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='two_repeated_positions',
            acquired=True).count(), 0)

    def test_straight_to_the_top_vp(self):
        # becoming vp in 2 semesters gives this achievement
        self.create_officer(self.sample_user, self.historian, self.sp2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='straighttothetop',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.vicepres, self.fa2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='straighttothetop',
            acquired=True).count(), 1)

    def test_straight_to_the_top_pres(self):
        # becoming pres in 3 semesters also gives this achievement
        self.create_officer(self.sample_user, self.historian, self.sp2009)
        self.create_officer(self.sample_user, self.historian, self.fa2009)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='straighttothetop',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.president, self.sp2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='straighttothetop',
            acquired=True).count(), 1)

    def test_late_to_the_top(self):
        # becoming vp after 2 semesters or pres after 3 does not give it
        self.create_officer(self.sample_user, self.historian, self.sp2009)
        self.create_officer(self.sample_user, self.historian, self.fa2009)
        self.create_officer(self.sample_user, self.vicepres, self.sp2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='straighttothetop',
            acquired=True).count(), 0)

        self.create_officer(self.sample_user, self.president, self.fa2010)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='straighttothetop',
            acquired=True).count(), 0)


class ProjectReportAchievementsTest(TestCase):
    fixtures = ['achievement.yaml',
                'test/term.yaml',
                'officer_position.yaml']

    def setUp(self):
        self.sample_user = get_user_model().objects.create_user(
            username='test', password='test', email='test@tbp.berkeley.edu',
            first_name="Test", last_name="Test")
        self.achievements = UserAchievement.objects.filter(
            user=self.sample_user)

        self.sp2012 = Term.objects.get(term=Term.SPRING, year=2012)
        self.fa2012 = Term.objects.get(term=Term.FALL, year=2012)
        self.sp2013 = Term.objects.get(term=Term.SPRING, year=2013)
        self.fa2013 = Term.objects.get(term=Term.FALL, year=2013)

    def write_pr(self, author, term=None, complete=False):
        if term is None:
            term = self.sp2013

        project_report, _ = ProjectReport.objects.get_or_create(
            term=term,
            date=datetime.date.today(),
            title=''.join(
                random.choice(string.ascii_uppercase) for x in range(6)),
            author=author,
            committee=OfficerPosition.objects.first(),
            complete=complete)

        return project_report

    def test01projectreports(self):
        """The achievement for writing a project report is given when the user
        has written a project report with complete=True.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_01_project_reports',
            acquired=True).count(), 0)

        self.write_pr(author=self.sample_user, term=self.fa2012, complete=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_01_project_reports',
            acquired=True).count(), 0)

        self.write_pr(author=self.sample_user, term=self.fa2012, complete=True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_01_project_reports',
            acquired=True).count(), 1)

    def test05projectreports(self):
        """The achievement for writing 5 project reports is given when the user
        has written five project reports with complete=True.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_05_project_reports',
            acquired=True).count(), 0)

        for _ in range(4):
            self.write_pr(author=self.sample_user, term=self.fa2012,
                          complete=True)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_05_project_reports',
            acquired=True).count(), 0)
        fiveprachievement = UserAchievement.objects.get(
            achievement__short_name='write_05_project_reports',
            user=self.sample_user)
        self.assertEqual(fiveprachievement.progress, 4)

        self.write_pr(author=self.sample_user, term=self.sp2013, complete=False)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_05_project_reports',
            acquired=True).count(), 0)

        self.write_pr(author=self.sample_user, term=self.sp2013, complete=True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_05_project_reports',
            acquired=True).count(), 1)

    def test15projectreports(self):
        """The achievement for writing twenty project reports is given when the
        user has written 20 project reports with complete=True.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_15_project_reports',
            acquired=True).count(), 0)

        for _ in range(14):
            self.write_pr(author=self.sample_user, term=self.fa2012,
                          complete=True)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_15_project_reports',
            acquired=True).count(), 0)
        fifteenprachievement = UserAchievement.objects.get(
            achievement__short_name='write_15_project_reports',
            user=self.sample_user)
        self.assertEqual(fifteenprachievement.progress, 14)

        self.write_pr(author=self.sample_user, term=self.fa2012, complete=True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_15_project_reports',
            acquired=True).count(), 1)

    def test_assignment_on_pr_completion(self):
        """The achievement for writing a project report is given when a project
        report is created with complete=False, and later changed to
        complete=True.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_01_project_reports',
            acquired=True).count(), 0)

        self.write_pr(author=self.sample_user, term=self.fa2012, complete=False)

        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_01_project_reports',
            acquired=True).count(), 0)

        project_report = ProjectReport.objects.get(
            author=self.sample_user, term=self.fa2012)

        project_report.complete = True
        project_report.save()

        self.assertEqual(self.achievements.filter(
            achievement__short_name='write_01_project_reports',
            acquired=True).count(), 1)

    def test_alphabet_pr_achievement(self):
        """The achievement for using all the letters of the alphabet is given
        to a user regardless of capitalization or splitting the letters up
        amongst different fields, and only for completed project reports.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='alphabet_project_report',
            acquired=True).count(), 0)

        self.write_pr(author=self.sample_user, term=self.fa2012, complete=False)

        project_report = ProjectReport.objects.get(
            author=self.sample_user, term=self.fa2012)

        project_report.title = 'abcdEf'
        project_report.other_group = 'ggGhiI'
        project_report.description = 'J'
        project_report.purpose = 'klmNoPq'
        project_report.organization = 'rst'
        project_report.cost = 'uv'
        project_report.problems = 'wxY'
        project_report.results = 'z'
        project_report.save()

        self.assertEqual(self.achievements.filter(
            achievement__short_name='alphabet_project_report',
            acquired=True).count(), 0)

        project_report.complete = True
        project_report.save()

        self.assertEqual(self.achievements.filter(
            achievement__short_name='alphabet_project_report',
            acquired=True).count(), 1)

    @freeze_time('2014-05-01')
    def test_pr_procrastination(self):
        """The achievement for procrastinating on a project report is given
        if a user completes the project report at least 60 days after the event
        is held.
        """
        self.assertEqual(self.achievements.filter(
            achievement__short_name='project_report_procrastination',
            acquired=True).count(), 0)

        self.write_pr(author=self.sample_user, term=self.fa2012, complete=True)
        self.assertEqual(self.achievements.filter(
            achievement__short_name='project_report_procrastination',
            acquired=True).count(), 0)

        self.write_pr(author=self.sample_user, term=self.sp2013, complete=False)

        project_report = ProjectReport.objects.get(
            author=self.sample_user, term=self.sp2013)

        # set the event date to 59 days ago, achievement still not given
        project_report.date = datetime.date.today() - datetime.timedelta(59)
        project_report.complete = True
        project_report.save()

        self.assertEqual(self.achievements.filter(
            achievement__short_name='project_report_procrastination',
            acquired=True).count(), 0)

        # set the event date to 60 days, 30 seconds ago
        project_report.date = datetime.date.today() - datetime.timedelta(60, 30)
        project_report.save()

        self.assertEqual(self.achievements.filter(
            achievement__short_name='project_report_procrastination',
            acquired=True).count(), 1)
