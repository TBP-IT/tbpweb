from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.test.utils import override_settings

from base.models import Officer
from base.models import OfficerPosition
from base.models import Term
from candidates.models import Candidate
from shortcuts import get_object_or_none
from user_profiles.fields import UserCommonNameChoiceField
from user_profiles.fields import UserCommonNameMultipleChoiceField
from user_profiles.models import CollegeStudentInfo
from user_profiles.models import StudentOrgUserProfile
from user_profiles.models import UserProfile

class UserInfoTestCase(TestCase):
    """A TestCase which provides a useful setUp method for creating common
    user info used in multiple test cases.
    """
    def setUp(self):
        Group.objects.create(name='Current Candidate')
        Group.objects.create(name='Member')

        self.user_model = get_user_model()

        self.user = self.user_model.objects.create_user(
            'test_user', 'it@tbp.berkeley.edu', 'testpw')
        self.first_name = 'Edward'
        self.last_name = 'Williams'
        self.user.first_name = self.first_name
        self.user.last_name = self.last_name
        self.user.save()

        # Re-fetch the user from the DB to avoid issues with the current
        # object having a stale reference to their corresponding userprofile
        self.user = self.user_model.objects.get(pk=self.user.pk)

        self.term = Term(term=Term.SPRING, year=2013, current=True)
        self.term.save()
        self.term_old = Term(term=Term.SPRING, year=2012)
        self.term_old.save()

        self.committee = OfficerPosition(
            short_name='it',
            long_name='Information Technology (test)',
            rank=2,
            mailing_list='IT')
        self.committee.save()


class UserProfilesTest(UserInfoTestCase):
    def setUp(self):
        super(UserProfilesTest, self).setUp()
        # There should be a one-to-one relation to a UserProfile created on
        # User post-save
        self.profile = self.user.userprofile

    def test_user_post_save_profile_creation(self):
        # Test that a user profile is tied to the created user after the
        # user is created
        self.assertEqual(self.profile, UserProfile.objects.get(user=self.user))

    @override_settings(HOSTNAME='example.com')
    def test_get_preferred_email(self):
        # When the user is not an officer:
        self.assertEqual(self.profile.get_preferred_email(), self.user.email)

        # With an alternate email address specified:
        test_email = 'test_' + self.user.email
        self.profile.alt_email = test_email
        self.profile.save()

        # user email (if not empty) is still preferred over alt_email:
        self.assertEqual(self.profile.get_preferred_email(), self.user.email)

        # Remove user email, keeping alternate email:
        self.user.email = ''
        self.user.save()
        self.assertEqual(self.profile.get_preferred_email(), test_email)

        # When the user is an officer (using the settings-defined hostname as
        # the email address domain):
        Officer(user=self.user, position=self.committee, term=self.term,
                is_chair=True).save()
        self.assertEqual(self.profile.get_preferred_email(),
                         '{}@example.com'.format(self.user.get_username()))

    def test_save_preferred_name(self):
        # Check that the preferred name was set as the user's first name on
        # save:
        self.assertEqual(self.profile.preferred_name, self.first_name)

        # Ensure that the preferred name can still be set and persists
        preferred_name = 'Bob'
        self.profile.preferred_name = preferred_name
        self.profile.save()
        self.assertEqual(self.profile.preferred_name, preferred_name)

    def test_name_methods(self):
        # Name methods with only first and last name
        full_name = '%s %s' % (self.first_name, self.last_name)
        self.assertEqual(self.profile.get_full_name(), full_name)
        self.assertEqual(self.profile.get_common_name(), full_name)

        # With middle name
        middle_name = 'Robert'
        self.profile.middle_name = middle_name
        self.profile.save()
        common_name = full_name
        full_name = '%s %s %s' % (self.first_name, middle_name, self.last_name)
        self.assertEqual(self.profile.get_full_name(), full_name)
        self.assertEqual(self.profile.get_full_name(verbose=True), full_name)
        self.assertEqual(self.profile.get_full_name(include_middle_name=False),
                         common_name)
        self.assertEqual(self.profile.get_common_name(), common_name)

        # Adding a preferred name:
        preferred_name = 'Bob'
        self.profile.preferred_name = preferred_name
        self.profile.save()
        common_name = '%s %s' % (preferred_name, self.last_name)
        self.assertEqual(self.profile.get_full_name(), full_name)
        self.assertEqual(
            self.profile.get_full_name(verbose=True),
            '{} ({}) {} {}'.format(
                preferred_name, self.first_name, middle_name, self.last_name))
        self.assertEqual(self.profile.get_full_name(include_middle_name=False),
                         '{} {}'.format(self.first_name, self.last_name))
        self.assertEqual(self.profile.get_common_name(), common_name)

    def test_get_verbose_first_name(self):
        # With no preferred_name specified, should return the user first name:
        self.assertEqual(self.profile.get_verbose_first_name(), self.first_name)

        preferred_name = 'Bob'
        self.profile.preferred_name = preferred_name
        self.profile.save()

        self.assertEqual(self.profile.get_verbose_first_name(),
                         '{} ({})'.format(preferred_name, self.first_name))

    def test_is_candidate(self):
        """Ensure that basic is_candidate usage works as expected.

        See tests for StudentOrgUserProfilesTest for more extensive testing.
        """
        # No Candidate objects created yet:
        self.assertFalse(self.profile.is_candidate())

        # Create Candidate for user in the current term:
        Candidate(user=self.user, term=self.term).save()

        # Should now be considered a candidate:
        self.assertTrue(self.profile.is_candidate())

    def test_is_member(self):
        """Ensure that basic is_officer usage works as expected.

        See tests for StudentOrgUserProfilesTest for more extensive testing.
        """
        student_org_profile, _ = StudentOrgUserProfile.objects.get_or_create(
            user=self.user)

        # User is not a member yet, since not recorded as initiated and not an
        # officer:
        self.assertFalse(self.profile.is_member())

        # Mark in their StudentOrgUserProfile that they've initiated, which
        # should qualify them as a member
        student_org_profile.initiation_term = self.term_old
        student_org_profile.save()
        self.assertTrue(self.profile.is_member())

    def test_is_officer(self):
        """Ensure that basic is_officer usage works as expected.

        See tests for StudentOrgUserProfilesTest for more extensive testing.
        """
        # No Officer objects created yet:
        self.assertFalse(self.profile.is_officer())

        # Create Officer for user in the current term:
        Officer(user=self.user, position=self.committee, term=self.term).save()

        # Should now be considered an officer:
        self.assertTrue(self.profile.is_officer())


class StudentOrgUserProfilesTest(UserInfoTestCase):
    def setUp(self):
        super(StudentOrgUserProfilesTest, self).setUp()
        self.model = StudentOrgUserProfile
        self.profile = self.model(user=self.user)
        self.profile.save()

        self.house_leader = OfficerPosition(
            short_name='house-leader',
            long_name='House Leader (test)',
            rank=3,
            mailing_list='IT')
        self.house_leader.save()

        self.advisor_pos = OfficerPosition(
            short_name='advisor',
            long_name='Advisor (test)',
            rank=4,
            mailing_list='IT',
            auxiliary=True)
        self.advisor_pos.save()

    def test_is_candidate(self):
        # No Candidate objects created yet:
        self.assertFalse(self.profile.is_candidate())

        # Create Candidate for user in a past term:
        candidate = Candidate(user=self.user, term=self.term_old)
        candidate.save()
        # Should now be considered a candidate only if current=False:
        self.assertTrue(self.profile.is_candidate(current=False))
        self.assertFalse(self.profile.is_candidate(current=True))

        # Mark that candidate as initiated:
        candidate.initiated = True
        candidate.save()
        # Re-fetch profile since candidate save affects StudentOrgUserProfile
        # initiation_term field:
        self.profile = get_object_or_none(self.model, user=self.user)
        self.assertFalse(self.profile.is_candidate(current=False))
        self.assertFalse(self.profile.is_candidate(current=True))

        # Mark initiated as False, and create new Candidate for the current
        # Term, as is the case for a candidate who doesn't initiate one term
        # and returns as a candidate a later term:
        candidate.initiated = False
        candidate.save()
        candidate = Candidate(user=self.user, term=self.term)
        candidate.save()
        self.profile = get_object_or_none(self.model, user=self.user)
        # Should be now considered a candidate (initiated not True):
        self.assertTrue(self.profile.is_candidate(current=False))
        self.assertTrue(self.profile.is_candidate(current=True))

        # Mark that candidate as initiated:
        candidate.initiated = True
        candidate.save()
        self.profile = get_object_or_none(self.model, user=self.user)
        self.assertFalse(self.profile.is_candidate(current=False))
        self.assertFalse(self.profile.is_candidate(current=True))

        # Change the 'current' semester to an old semester:
        self.term_old.current = True
        self.term_old.save()
        # Now the candidate should be considered a candidate since they have
        # not _yet_ initiated based on what the current semester is, but
        # they are in the database as a candidate for the current semester:
        self.assertTrue(self.profile.is_candidate(current=False))
        self.assertTrue(self.profile.is_candidate(current=True))

        # Ensure that they are also marked as a candidate if initiated = False
        candidate.initiated = False
        candidate.save()
        self.profile = get_object_or_none(self.model, user=self.user)
        self.assertTrue(self.profile.is_candidate(current=False))
        self.assertTrue(self.profile.is_candidate(current=True))

    def test_is_member(self):
        # User is not a member yet, since not recorded as initiated and not an
        # officer:
        self.assertFalse(self.profile.is_member())

        # Mark in their StudentOrgUserProfile that they've initiated, which
        # should qualify them as a member
        self.profile.initiation_term = self.term_old
        self.profile.save()
        self.assertTrue(self.profile.is_member())

        # Remove the initiation term, and check that just being an officer
        # also qualifies the user as a member
        self.profile.initiation_term = None
        self.profile.save()
        self.assertFalse(self.profile.is_member())
        Officer(user=self.user, position=self.committee, term=self.term).save()
        self.assertTrue(self.profile.is_member())

    def test_is_officer(self):
        # Note that is_officer also tests the get_officer_positions() method
        self.assertFalse(self.profile.is_officer())

        # Officer in the current term:
        officer = Officer(user=self.user, position=self.committee,
                          term=self.term, is_chair=True)
        officer.save()
        self.assertTrue(self.profile.is_officer())
        self.assertTrue(self.profile.is_officer(current=True))

        # Officer in an old term:
        officer.term = self.term_old
        officer.save()
        self.assertTrue(self.profile.is_officer())
        self.assertFalse(self.profile.is_officer(current=True))

        # Advisor officer in the current term:
        officer.position = self.advisor_pos
        officer.term = self.term
        officer.save()
        self.assertTrue(self.profile.is_officer())
        self.assertTrue(self.profile.is_officer(current=True))

        # Exclude auxiliary positions, such as advisors:
        self.assertFalse(self.profile.is_officer(exclude_aux=True))
        self.assertFalse(self.profile.is_officer(current=True,
                                                 exclude_aux=True))

    def test_get_officer_positions(self):
        # Note that when given no 'term' kwarg, the method returns positions
        # from all terms. The order of the list returned is based on term, then
        # officer position rank
        # No officer positions for this user yet:
        self.assertEqual(list(self.profile.get_officer_positions()), [])

        # One Officer position in the current term:
        Officer(user=self.user, position=self.committee, term=self.term,
                is_chair=True).save()
        self.assertEqual(
            list(self.profile.get_officer_positions()),
            [self.committee])
        self.assertEqual(
            list(self.profile.get_officer_positions(term=self.term)),
            [self.committee])
        self.assertEqual(
            list(self.profile.get_officer_positions(term=self.term_old)),
            [])

        # Advisor officer position in an old term:
        Officer(user=self.user, position=self.advisor_pos,
                term=self.term_old).save()
        self.assertEqual(
            list(self.profile.get_officer_positions()),
            [self.advisor_pos, self.committee])
        self.assertEqual(
            list(self.profile.get_officer_positions(term=self.term)),
            [self.committee])
        self.assertEqual(
            list(self.profile.get_officer_positions(term=self.term_old)),
            [self.advisor_pos])

        # Another advisor officer position in the current term
        Officer(user=self.user, position=self.advisor_pos,
                term=self.term).save()
        self.assertEqual(
            list(self.profile.get_officer_positions()),
            [self.advisor_pos, self.committee, self.advisor_pos])
        self.assertEqual(
            list(self.profile.get_officer_positions(term=self.term)),
            [self.committee, self.advisor_pos])
        self.assertEqual(
            list(self.profile.get_officer_positions(term=self.term_old)),
            [self.advisor_pos])

        # Add a house leader officer position in the current term:
        # Ensure ordering is correct:
        Officer(user=self.user, position=self.house_leader,
                term=self.term).save()
        self.assertEqual(
            list(self.profile.get_officer_positions()),
            [self.advisor_pos, self.committee, self.house_leader,
             self.advisor_pos])
        older_term = Term(term=Term.SPRING, year=2008)
        older_term.save()
        # Add a house leader officer position in an even older term:
        Officer(user=self.user, position=self.house_leader,
                term=older_term).save()
        self.assertEqual(
            list(self.profile.get_officer_positions()),
            [self.house_leader, self.advisor_pos, self.committee,
             self.house_leader, self.advisor_pos])

    def test_get_officer_positions_user_specific(self):
        """Test that get_officer_positions does not return positions held by
        other users.
        """
        # No officer positions for either user yet:
        new_user = self.user_model(username='new_officer_test',
                                   password='password',
                                   email='shyguy@tbp.berkeley.edu')
        new_user.save()
        new_user_profile = self.model(user=new_user)
        self.assertEqual(
            list(self.profile.get_officer_positions()), [])
        self.assertEqual(
            list(new_user_profile.get_officer_positions()), [])

        # Make both users different officer positions:
        Officer(user=self.user, position=self.committee,
                term=self.term).save()
        Officer(user=new_user, position=self.advisor_pos,
                term=self.term_old).save()

        # Check the officer positions for self.user:
        self.assertEqual(
            list(self.profile.get_officer_positions()),
            [self.committee])
        self.assertEqual(
            list(self.profile.get_officer_positions(term=self.term)),
            [self.committee])
        self.assertEqual(
            list(self.profile.get_officer_positions(term=self.term_old)),
            [])

        # Check the officer positions for new_user:
        self.assertEqual(
            list(new_user_profile.get_officer_positions()),
            [self.advisor_pos])
        self.assertEqual(
            list(new_user_profile.get_officer_positions(term=self.term)),
            [])
        self.assertEqual(
            list(new_user_profile.get_officer_positions(term=self.term_old)),
            [self.advisor_pos])

    def test_is_officer_position(self):
        # Note that current=False is the default, which checks whether the
        # person has ever held the officer position

        # Not ever an officer:
        self.assertFalse(
            self.profile.is_officer_position(self.committee.short_name))
        self.assertFalse(
            self.profile.is_officer_position(self.advisor_pos.short_name))
        self.assertFalse(
            self.profile.is_officer_position(
                self.committee.short_name, current=True))

        # Add an officer position in the current term:
        Officer(user=self.user, position=self.committee, term=self.term,
                is_chair=True).save()
        self.assertTrue(
            self.profile.is_officer_position(self.committee.short_name))
        self.assertTrue(
            self.profile.is_officer_position(
                self.committee.short_name, current=True))
        self.assertFalse(
            self.profile.is_officer_position(self.advisor_pos.short_name))

        # Add an advisor officer position in an old term:
        Officer(user=self.user, position=self.advisor_pos,
                term=self.term_old).save()
        self.assertTrue(self.profile.is_officer_position(
            self.committee.short_name))
        self.assertTrue(self.profile.is_officer_position(
            self.advisor_pos.short_name))
        self.assertFalse(self.profile.is_officer_position(
            self.advisor_pos.short_name, current=True))

    def test_get_first_term_as_candidate(self):
        # No Candidate objects created yet:
        self.assertFalse(self.profile.is_candidate())
        self.assertIsNone(self.profile.get_first_term_as_candidate())

        # Create Candidate for user in a past term:
        candidate = Candidate(user=self.user, term=self.term_old)
        candidate.save()
        self.assertEqual(self.profile.get_first_term_as_candidate(),
                         self.term_old)

        # Create Candidate for user in current term, and past term should
        # still be marked as first term as candidate:
        candidate = Candidate(user=self.user, term=self.term)
        candidate.save()
        self.assertEqual(self.profile.get_first_term_as_candidate(),
                         self.term_old)

        # Create user who only has initiation term data and no Candidate
        # objects:
        temp_user = get_user_model().objects.create_user(
            'tester', 'test@tbp.berkeley.edu', 'testpw')
        temp_user.first_name = 'Bentley'
        temp_user.last_name = 'Bent'
        temp_user.save()

        profile = self.model(user=temp_user)
        profile.save()
        self.assertIsNone(profile.get_first_term_as_candidate())

        profile.initiation_term = self.term
        profile.save()
        self.assertEqual(profile.get_first_term_as_candidate(),
                         self.term)

    def test_student_org_user_profile_post_save(self):
        """Tests whether creating and saving a StudentOrgUserProfile properly
        ensures that a CollegeStudentInfo object exists for the user in the
        post_save callback.
        """
        self.assertIsNotNone(get_object_or_none(CollegeStudentInfo,
                                                user=self.user))


class FieldsTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

        self.user1 = self.user_model.objects.create_user(
            username='testuser1',
            email='test1@tbp.berkeley.edu',
            password='testpassword')
        self.user1.first_name = 'Wilford'
        self.user1.last_name = 'Bentley'
        self.user1.save()

        self.user2 = self.user_model.objects.create_user(
            username='testuser2',
            email='test2@tbp.berkeley.edu',
            password='testpassword')
        self.user2.first_name = 'Mike'
        self.user2.last_name = 'McTest'
        self.user2.save()

        # Re-fetch the users from the DB to avoid issues with the current
        # objects having stale references to their corresponding userprofiles
        self.user1 = self.user_model.objects.get(pk=self.user1.pk)
        self.user2 = self.user_model.objects.get(pk=self.user2.pk)

    def test_common_name_choice_fields(self):
        # Form a queryset of all users created above, in order by last name:
        user_queryset = self.user_model.objects.all()

        name_field = UserCommonNameChoiceField(
            queryset=user_queryset)
        name_mult_field = UserCommonNameMultipleChoiceField(
            queryset=user_queryset)

        # Note that field.choices gives an iterable of choices, where each
        # element is a tuple for the HTML select field as (id, label).
        # Thus the second tuple element is the label that the user of the
        # site will see as his HTML selection option.
        # Also note that for UserCommonNameChoiceField, the first tuple in the
        # list is for the Empty label (before the user has selected anything),
        # so the first user choice is at index 1 instead of 0.
        name_choices = [name for _, name in list(name_field.choices)]
        name_mult_choices = [name for _, name in list(name_mult_field.choices)]

        user1_common_name = self.user1.userprofile.get_common_name()
        user2_common_name = self.user2.userprofile.get_common_name()

        # Names will be in reverse order because it is sorted by first name.
        self.assertEqual(name_choices[2], user1_common_name)
        self.assertEqual(name_mult_choices[1], user1_common_name)
        self.assertEqual(name_choices[1], user2_common_name)
        self.assertEqual(name_mult_choices[0], user2_common_name)
