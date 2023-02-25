# pylint: disable=F0401
import os

from .base import *
from .project import HOSTNAME
from .project import RESUMEQ_OFFICER_POSITION

try:
    # pylint: disable=F0401
    import settings.tbpweb_keys as tbpweb_keys
except ImportError:
    print('Could not import tbpweb_keys. Please make sure tbpweb_keys.py exists '
          'on the path, and that there are no errors in the module.')
    sys.exit(1)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('TBP IT', 'tbpwebsite@' + HOSTNAME),
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

SECRET_KEY = tbpweb_keys.SECRET_KEY

# YouTube Secret Stuff
YT_USERNAME = 'BerkeleyTBP'
YT_PRODUCT = 'noiro'
YT_DEVELOPER_KEY = tbpweb_keys.YT_DEVELOPER_KEY
YT_PASSWORD = tbpweb_keys.YT_PASSWORD

# http://www.djangosnippets.org/snippets/1653/
RECAPTCHA_PRIVATE_KEY = tbpweb_keys.RECAPTCHA_PRIVATE_KEY
RECAPTCHA_PUBLIC_KEY = tbpweb_keys.RECAPTCHA_PUBLIC_KEY

# HTTPS support in production
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Email addresses
RESUMEQ_ADDRESS = RESUMEQ_OFFICER_POSITION + '@' + HOSTNAME
HELPDESK_ADDRESS = 'helpdesk@' + HOSTNAME
INDREL_ADDRESS = 'indrel@' + HOSTNAME
IT_ADDRESS = 'it@' + HOSTNAME
STARS_ADDRESS = 'stars@' + HOSTNAME

INDREL_NOTICE_TO = 'notice@' + HOSTNAME
INDREL_SPAM_TO = 'spam@' + HOSTNAME

DEFAULT_FROM_EMAIL = 'tbpwebsite@' + HOSTNAME
SERVER_EMAIL = DEFAULT_FROM_EMAIL

ALLOWED_HOSTS = [
    'tbp.apphost.ocf.berkeley.edu',
    'tbp-dev.apphost.ocf.berkeley.edu',
    'tbp.berkeley.edu'
]

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(WORKSPACE_DJANGO_ROOT, "static"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = 'https://www.ocf.berkeley.edu/~tbp/tbpweb/static/'
STATIC_ROOT = "/home/t/tb/tbp/public_html/tbpweb/static/"

# Media files (user-uploaded files)
# https://docs.djangoproject.com/en/2.1/topics/files/
MEDIA_URL = 'https://www.ocf.berkeley.edu/~tbp/tbpweb/media/'
MEDIA_ROOT = "/home/t/tb/tbp/public_html/tbpweb/media/"
