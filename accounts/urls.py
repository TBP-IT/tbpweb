from re import template
from django.urls import reverse_lazy
from django.urls import re_path
from django.contrib.auth.views import LoginView, LogoutView, \
                                      PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
                                      PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView

from accounts.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth import forms as auth_forms


app_name = 'accounts'

urlpatterns = [
    re_path(r'^login/$',
        LoginView.as_view(template_name='accounts/login.html',
                          authentication_form=AuthenticationForm),
        name='login'),
    re_path(r'^logout/$',
        # next_page is used to redirect to the root URL after logout if the
        # requested URL doesn't contain a redirect GET field
        LogoutView.as_view(next_page=reverse_lazy('base:home'), template_name='accounts/logout.html'),
        name='logout'),

    # Changing password (change, then done):
    re_path(r'password/change/$',
        PasswordChangeView.as_view(template_name='accounts/password_change.html',
                                   success_url=reverse_lazy('accounts:password-change-done'),
                                   form_class=auth_forms.PasswordChangeForm),
        name='password-change'),
    re_path(r'password/change/done/$',
        PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
        name='password-change-done'),

    # Resetting password (reset, then sent, then confirm, then done):
    re_path(r'password/reset/$', PasswordResetView.as_view(template_name='accounts/password_reset.html',
         email_template_name='accounts/password_reset_email.html',
         form_class=PasswordResetForm,
         success_url=reverse_lazy('accounts:password-reset-sent')),
        name='password-reset'),
    re_path(r'password/reset/sent/$', PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.html'),
        name='password-reset-sent'),
    # URL regex for uid and token copied from Django source
    re_path((r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
         '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'),
        PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html',
                                         form_class=auth_forms.SetPasswordForm,
                                         success_url=reverse_lazy(
                                            'accounts:password-reset-complete')),
        name='password-reset-confirm'),
    re_path(r'^password/reset/complete/',
        PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='password-reset-complete'),
]
