import getpass
import subprocess
import os

from .base import *
# pylint: disable=F0401
from .project import HOSTNAME

###############################################################################
# Private Variables for this dev instance
###############################################################################
_user = getpass.getuser()
_git_cmd = ['git', '--git-dir=%s/.git' % WORKSPACE_DJANGO_ROOT,
            '--work-tree=%s' % WORKSPACE_DJANGO_ROOT]
try:
    # Get dev user contact info from git
    _name = subprocess.check_output(
        _git_cmd + ['config', 'user.name']).strip()
    _email = subprocess.check_output(
        _git_cmd + ['config', 'user.email']).strip()
except subprocess.CalledProcessError:
    _name = 'Test'
    _email = 'test@tbp.berkeley.edu'


###############################################################################
# Override settings for all dev instances
###############################################################################
DEBUG = False
TEMPLATE_DEBUG = True
SHOW_DEBUG_TOOLBAR = False  # Custom flag to show the Django Debug Toolbar

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Set the debug mode for easy-thumbnails
#THUMBNAIL_DEBUG = DEBUG
THUMBNAIL_DEBUG = True

# Set dev user's info for admins/manager
ADMINS = ((_name, _email),)
MANAGERS = ADMINS

ALLOWED_HOSTS = ['localhost','127.0.0.1', HOSTNAME]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR , 'db.sqlite3'),
    }
}

# Check X-Forwarded-Protocol for http protocol so that request.is_secure()
# returns the correct value when dev server is behind a proxy.
# Make sure proxy config sets this header correctly:
#  nginx:
#    proxy_set_header X-Forwarded-Protocol $scheme;
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# Custom dev cookie session ID
SESSION_COOKIE_NAME = 'tbpweb_dev_%s_sid' % _user

# Always show the Django Debug Toolbar on dev. By default, the Debug Toolbar
# would only be shown when DEBUG=True and the request is from an IP listed in
# the INTERNAL_IPS setting.
if SHOW_DEBUG_TOOLBAR:
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 'settings.third_party.show_toolbar'
    }

# NOTE: It is highly recommended that you copy tbpweb/settings/local.py.template
# to a new file tbpweb/settings/local.py. After making necessary changes to the
# local.py file, you will be able to use HTTPS for your dev server. See
# tbpweb/settings/local.py.template for further clarification and instruction.

# Import any local settings
try:
    # pylint: disable=E0611,F0401,W0401,W0614
    from .local import *
except ImportError:
    # Ignore if there's no local settings file
    pass