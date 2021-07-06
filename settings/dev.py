import getpass
import subprocess

from tbpweb.settings.base import WORKSPACE_ROOT
# pylint: disable=F0401
import tbpweb_keys


###############################################################################
# Private Variables for this dev instance
###############################################################################
_user = getpass.getuser()
_git_cmd = ['git', '--git-dir=%s/.git' % WORKSPACE_ROOT,
            '--work-tree=%s' % WORKSPACE_ROOT]
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
DEBUG = True
TEMPLATE_DEBUG = DEBUG

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Set the debug mode for easy-thumbnails
THUMBNAIL_DEBUG = DEBUG

# Set dev user's info for admins/manager
ADMINS = ((_name, _email),)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # We need this for per-user development databases.
        'NAME': 'tbpweb_dev_%s' % _user,
        'USER': 'tbpweb_dev',
        'PASSWORD': tbpweb_keys.DEV_DB_PASSWORD,
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
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'tbpweb.settings.third_party.show_toolbar'
}

# NOTE: It is highly recommended that you copy tbpweb/settings/local.py.template
# to a new file tbpweb/settings/local.py. After making necessary changes to the
# local.py file, you will be able to use HTTPS for your dev server. See
# tbpweb/settings/local.py.template for further clarification and instruction.

# Import any local settings
try:
    # pylint: disable=E0611,F0401,W0401,W0614
    from tbpweb.settings.local import *
except ImportError:
    # Ignore if there's no local settings file
    pass
