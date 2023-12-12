from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Q
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from companies.models import CompanyRep

class UserFormMixin(object):
    """Change the username regex and require user fields."""
    def __init__(self, *args, **kwargs):
        super(UserFormMixin, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username'] = forms.RegexField(
            regex=settings.VALID_USERNAME,
            help_text=settings.USERNAME_HELPTEXT)


class UserCreationForm(UserFormMixin, auth_forms.UserCreationForm):
    def save(self, commit=True):
        # Call the ModelForm save method directly, since we are overriding the
        # Django UserCreationForm save() functionality here
        user = forms.ModelForm.save(self, commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(UserFormMixin, auth_forms.UserChangeForm):
    pass


class AuthenticationForm(auth_forms.AuthenticationForm):
    """An AuthenticationForm that takes into account Company users."""
    def confirm_login_allowed(self, user: AbstractBaseUser):
        """Ensures that Company users and their Company's account expiration
        are taken into consideration to allow login.
        Cleaning and Authentication should already have happened (which notably
        checks the password correctness and whether the given User is "active").
        If the user corresponds to a company representative account,
        this method performs the additional confirmation that the company account
        has not expired, raising a ValidationError if so.
        """
        company_rep = None

        try:
            # Try to get a company account for the given user
            company_rep = user.companyrep
        except CompanyRep.DoesNotExist:
            # If the user is not a company, don't set company rep
            #  Company Rep validation skipped (via None),
            #  and direct to allow login
            pass

        if (company_rep is not None) and (company_rep.company.is_expired()):
            raise forms.ValidationError(
                ('{}\'s subscription to this website has expired. '
                 'Please contact {} to arrange account renewal.'.format(
                     company_rep.company.name, settings.INDREL_ADDRESS)),
                code='expired'
            )

        return super().confirm_login_allowed(user)

class PasswordResetForm(forms.Form):
    """A form for users to enter their username or email address and have a
    password reset email sent to them.
    Unlike the standard password reset form, note that this form accepts both
    username and email address, rather than just email address.
    The save method is primarily copied from django.contrib.auth.forms
    PasswordResetForm, though this reset-form allows for sending reset emails to
    users that have unusable passwords. Also, while the Django form will send emails
    to multiple users if they all have the same email address on file, if
    multiple users are found here (due to having users with colliding email
    addresses), a validation error is raised.
    """
    username_or_email = forms.CharField(label='Username or email address')
    user_cache = None  # A cached user object, found during validation process

    def clean_username_or_email(self):
        entry = self.cleaned_data['username_or_email']

        # The username is case-sensitive, but the email address is not:
        lookup = Q(username__exact=entry) | Q(email__iexact=entry)

        user_model = get_user_model()
        try:
            self.user_cache = user_model._default_manager.get(
                lookup, is_active=True)
        except user_model.DoesNotExist:
            raise forms.ValidationError('Sorry, this user doesn\'t exist.')
        except user_model.MultipleObjectsReturned:
            raise forms.ValidationError('Unable to find distinct user.')
        return entry

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='accounts/password_reset_email.html',
             html_email_template_name='accounts/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             extra_email_context=None,
             from_email=None, request=None):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        Use as defaults the built-in Django password_reset_subject template and
        the custom password_reset_email template.
        """
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override

        # Get the user selected in the clean method:
        user = self.user_cache

        context = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        email = loader.render_to_string(html_email_template_name, context)
        send_mail(subject, email, from_email, [user.email])
