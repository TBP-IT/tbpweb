from django.conf import settings
from django import forms
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from recaptcha.client import captcha

from emailer.widgets import ReCaptcha


class ReCaptchaField(forms.CharField):
    """A reCAPTCHA field to use with forms.

    Based on http://www.djangosnippets.org/snippets/1653/
    """
    default_error_messages = {
        'captcha_invalid': _(u'Invalid captcha')
    }

    def __init__(self, *args, **kwargs):
        self.widget = ReCaptcha
        self.required = True
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_text(values[0])
        recaptcha_response_value = smart_text(values[1])
        check_captcha = captcha.submit(recaptcha_challenge_value,
                                       recaptcha_response_value,
                                       settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise forms.util.ValidationError(
                self.error_messages['captcha_invalid'])
        return values[0]
