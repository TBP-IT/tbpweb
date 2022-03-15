import datetime
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as DefaultUser
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch

from accounts.forms import AuthenticationForm
from companies.models import Company
from companies.models import CompanyRep


class UserModelTest(TestCase):
    @override_settings(AUTH_USER_MODEL='auth.User')
    def get_correct_user_model(self):
        self.assertEqual(get_user_model(), DefaultUser)

    @override_settings(AUTH_USER_MODEL='nonexistent.User')
    def get_wrong_user_model(self):
        self.assertRaises(NameError, get_user_model)

class AuthenticationFormTest(TestCase):
    fixtures = ['groups.yaml']

    def setUp(self):
        self.username = 'testuser'
        self.password = 'password'
        self.user = get_user_model().objects.create_user(
            username=self.username,
            email='test@tbp.berkeley.edu',
            password=self.password,
            first_name='John',
            last_name='Doe')
        self.form_data = {
            'username': self.username,
            'password': self.password
        }

    def test_regular_user_auth_succeeds(self):
        """Test whether a non-company user can log in as expected."""
        form = AuthenticationForm(None, self.form_data)
        self.assertTrue(form.is_valid())

    def test_company_user_auth_succeeds_for_valid_account(self):
        """Verify that a company rep user can log in if their company's
        subscription is not expired.
        """
        # Create a company rep for the user, with a company that is active
        # (is_expired returns False)
        company = Company(name='Test Company',
                          expiration_date=datetime.date.today())
        company.save()
        with patch.object(Company, 'is_expired',
                          return_value=False) as mock_is_expired:
            rep = CompanyRep(user=self.user, company=company)
            rep.save()

            # Ensure that the user can be authenticated
            form = AuthenticationForm(None, self.form_data)
            self.assertTrue(form.is_valid())
        self.assertEquals(mock_is_expired.call_count, 1)

    def test_company_user_auth_fails_for_expired_account(self):
        """Verify that a company rep user cannot log in if their company's
        subscription is expired.
        """
        # Create a company rep for the user, with a company that has an expired
        # subscription (is_expired returns True)
        company = Company(name='Test Company',
                          expiration_date=datetime.date.today())
        company.save()
        with patch.object(Company, 'is_expired',
                          return_value=True) as mock_is_expired:
            rep = CompanyRep(user=self.user, company=company)
            rep.save()

            # Ensure that the user cannot be authenticated
            form = AuthenticationForm(None, self.form_data)
            self.assertFalse(form.is_valid())
            expected_error_msg = (
                '{}\'s subscription to this website has expired'.format(
                    company.name))
            self.assertIn(expected_error_msg, form.non_field_errors()[0])
        self.assertEquals(mock_is_expired.call_count, 1)
