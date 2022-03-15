# pylint: disable=F0401
import os
import settings.tbpweb_keys as tbpweb_keys
from .base import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(WORKSPACE_DJANGO_ROOT, 'emails')

ADMINS = (
    ('TBP IT', 'it-notice@tbp.berkeley.edu'),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = [HOSTNAME]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tbpweb_dev_staging',
        'USER': 'tbpweb_dev',
        'PASSWORD': tbpweb_keys.DEV_DB_PASSWORD,
    }
}

# HTTPS support in staging
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Import any local settings custom for staging environment
try:
    # pylint: disable=E0611,F0401,W0401,W0614
    from .local import *
except ImportError:
    # Ignore if there's no local settings file
    pass
