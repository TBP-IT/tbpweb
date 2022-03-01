# pylint: disable=F0401
import os

from .tbpweb_keys import *
from .base import *
from .project import HOSTNAME
from .project import RESUMEQ_OFFICER_POSITION


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('TBP IT', 'it-notice@' + HOSTNAME),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tbp',
        'HOST': 'mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'read_default_file': "~/.my.cnf",
        },
    },
}

# HTTPS support in production
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Email addresses
RESUMEQ_ADDRESS = RESUMEQ_OFFICER_POSITION + '@' + HOSTNAME
HELPDESK_ADDRESS = 'helpdesk@' + HOSTNAME
INDREL_ADDRESS = 'indrel@' + HOSTNAME
IT_ADDRESS = 'it@' + HOSTNAME
STARS_ADDRESS = 'stars@' + HOSTNAME

HELPDESK_NOTICE_TO = 'notice@' + HOSTNAME
INDREL_NOTICE_TO = 'notice@' + HOSTNAME
HELPDESK_SPAM_TO = 'spam@' + HOSTNAME
INDREL_SPAM_TO = 'spam@' + HOSTNAME

ALLOWED_HOSTS = [
    'localhost', 'tbp-dev.apphost.ocf.berkeley.edu'
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = 'https://www.ocf.berkeley.edu/~tbp/tbpweb/static/'
STATIC_ROOT = os.path.join(WORKSPACE_DJANGO_ROOT, 'static/')

# Media files (user-uploaded files)
# https://docs.djangoproject.com/en/2.1/topics/files/
MEDIA_URL = 'https://www.ocf.berkeley.edu/~tbp/tbpweb/media/'
MEDIA_ROOT = os.path.join(WORKSPACE_DJANGO_ROOT, 'media/')
