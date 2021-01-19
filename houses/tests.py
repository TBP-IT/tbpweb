from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from quark.base.models import Officer
from quark.base.models import OfficerPosition
from quark.base.models import Term
from quark.houses.models import House
from quark.houses.models import HouseMember


class HouseMemberAssignmentTest(TestCase):
    fixtures = ['house.yaml',
                'officer_position.yaml',
                'test/term.yaml']

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test', password='test', email='test@tbp.berkeley.edu',
            first_name='Test', last_name='Test')

        self.bodi = House.objects.get(name='Bodi')
        self.delphini = House.objects.get(name='Delphini')
        self.kastoras = House.objects.get(name='Kastoras')
        self.skylos = House.objects.get(name='Skylos')

        self.current_term = Term.objects.get_current_term()
        self.sp2010 = Term.objects.get(term=Term.SPRING, year='2010')

        self.house_leader = OfficerPosition.objects.get(
            short_name='house-leaders')

        # Make the user a superuser so that they can add and remove housemembers
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username=self.user.username, password='test')

    def test_assign_user_to_house(self):
        assign_url = reverse('houses:assign')
        assign_data = {'userPK': self.user.id,
                       'houseName': self.bodi.mailing_list,
                       'term': self.current_term.get_url_name()}

        self.assertEqual(0, HouseMember.objects.filter(house=self.bodi).count())

        # Assign the user to house
        response = self.client.post(assign_url, assign_data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, HouseMember.objects.filter(house=self.bodi).count())

    def test_assign_user_to_second_house(self):
        assign_url = reverse('houses:assign')
        assign_data1 = {'userPK': self.user.id,
                        'houseName': self.kastoras.mailing_list,
                        'term': self.current_term.get_url_name()}

        self.assertEqual(0, HouseMember.objects.filter(
            house=self.kastoras).count())

        # Assign the user to first house
        response1 = self.client.post(assign_url, assign_data1)
        self.assertEqual(200, response1.status_code)
        self.assertEqual(1, HouseMember.objects.filter(
            house=self.kastoras).count())

        # Assign the user to second house and verify they are removed from first
        assign_data2 = {'userPK': self.user.id,
                        'houseName': self.delphini.mailing_list,
                        'term': self.current_term.get_url_name()}

        self.assertEqual(0, HouseMember.objects.filter(
            house=self.delphini).count())

        response2 = self.client.post(assign_url, assign_data2)
        self.assertEqual(200, response2.status_code)
        self.assertEqual(1, HouseMember.objects.filter(
            house=self.delphini).count())
        self.assertEqual(0, HouseMember.objects.filter(
            house=self.kastoras).count())

    def test_assign_user_to_second_house_different_terms(self):
        assign_url = reverse('houses:assign')
        assign_data1 = {'userPK': self.user.id,
                        'houseName': self.kastoras.mailing_list,
                        'term': self.current_term.get_url_name()}

        self.assertEqual(0, HouseMember.objects.filter(
            house=self.kastoras).count())

        # Assign the user to first house
        response1 = self.client.post(assign_url, assign_data1)
        self.assertEqual(200, response1.status_code)
        self.assertEqual(1, HouseMember.objects.filter(
            house=self.kastoras).count())

        # Assign the user to 2nd house and verify they're not removed from 1st
        assign_data2 = {'userPK': self.user.id,
                        'houseName': self.delphini.mailing_list,
                        'term': self.sp2010.get_url_name()}

        self.assertEqual(0, HouseMember.objects.filter(
            house=self.delphini).count())

        response2 = self.client.post(assign_url, assign_data2)
        self.assertEqual(200, response2.status_code)
        self.assertEqual(1, HouseMember.objects.filter(
            house=self.delphini).count())
        self.assertEqual(1, HouseMember.objects.filter(
            house=self.kastoras).count())
        self.assertEqual(1, HouseMember.objects.filter(
            term=self.sp2010).count())
        self.assertEqual(1, HouseMember.objects.filter(
            term=self.current_term).count())

    def test_unassign_user(self):
        assign_url = reverse('houses:assign')
        assign_data = {'userPK': self.user.id,
                       'houseName': self.skylos.mailing_list,
                       'term': self.current_term.get_url_name()}

        unassign_url = reverse('houses:unassign')
        unassign_data = {'userPK': self.user.id,
                         'term': self.current_term.get_url_name()}

        self.assertEqual(0, HouseMember.objects.filter(
            house=self.skylos).count())

        response1 = self.client.post(assign_url, assign_data)
        self.assertEqual(200, response1.status_code)
        self.assertEqual(1, HouseMember.objects.filter(
            house=self.skylos).count())

        response2 = self.client.post(unassign_url, unassign_data)
        self.assertEqual(200, response2.status_code)
        self.assertEqual(0, HouseMember.objects.filter(
            house=self.skylos).count())

    def test_house_leader(self):
        Officer.objects.create(
            user=self.user, position=self.house_leader, term=self.current_term)

        assign_url = reverse('houses:assign')
        assign_data = {'userPK': self.user.id,
                       'houseName': self.delphini.mailing_list,
                       'term': self.current_term.get_url_name()}

        self.assertEqual(0, HouseMember.objects.filter(is_leader=True).count())

        response = self.client.post(assign_url, assign_data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, HouseMember.objects.filter(is_leader=True).count())

    def test_second_house_leader(self):
        Officer.objects.create(
            user=self.user, position=self.house_leader, term=self.current_term)

        assign_url = reverse('houses:assign')
        assign_data1 = {'userPK': self.user.id,
                        'houseName': self.kastoras.mailing_list,
                        'term': self.current_term.get_url_name()}

        self.assertEqual(0, HouseMember.objects.filter(is_leader=True).count())

        response1 = self.client.post(assign_url, assign_data1)
        self.assertEqual(200, response1.status_code)
        self.assertEqual(1, HouseMember.objects.filter(is_leader=True).count())

        # Create a second user, make them house leader, and assign to same house
        user2 = get_user_model().objects.create_user(
            username='test2', password='test', email='test2@tbp.berkeley.edu',
            first_name='Test', last_name='Test')

        Officer.objects.create(
            user=user2, position=self.house_leader, term=self.current_term)

        assign_data2 = {'userPK': user2.id,
                        'houseName': self.kastoras.mailing_list,
                        'term': self.current_term.get_url_name()}

        response2 = self.client.post(assign_url, assign_data2)

        # Verify that the post request fails and no HouseMember is created

        self.assertEqual(400, response2.status_code)
        self.assertEqual(1, HouseMember.objects.filter(is_leader=True).count())
        self.assertEqual(1, HouseMember.objects.all().count())

    def test_multiple_non_leaders(self):
        assign_url = reverse('houses:assign')
        assign_data1 = {'userPK': self.user.id,
                        'houseName': self.skylos.mailing_list,
                        'term': self.current_term.get_url_name()}

        self.assertEqual(0, HouseMember.objects.all().count())

        response1 = self.client.post(assign_url, assign_data1)
        self.assertEqual(200, response1.status_code)
        self.assertEqual(1, HouseMember.objects.all().count())

        # Create a second non-house-leader user and assign to same house
        user2 = get_user_model().objects.create_user(
            username='test2', password='test', email='test2@tbp.berkeley.edu',
            first_name='Test', last_name='Test')

        assign_data2 = {'userPK': user2.id,
                        'houseName': self.skylos.mailing_list,
                        'term': self.current_term.get_url_name()}

        response2 = self.client.post(assign_url, assign_data2)

        # Verify that they are added correctly

        self.assertEqual(200, response2.status_code)
        self.assertEqual(2, HouseMember.objects.all().count())
