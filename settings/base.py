"""
Django settings for "tbpweb" student organization website project.
This file lists Django settings constant for development and production
environments. Never import this or any other settings file directly unless you
are sure you do not need the settings in the site- or env-specific settings
files.
"""

import os
import sys
import warnings

KEY_PATH = '/home/tbp/private'
if KEY_PATH not in sys.path:
    sys.path.append(KEY_PATH)
try:
    # pylint: disable=F0401
    import settings.tbpweb_keys as tbpweb_keys
except ImportError:
    print('Could not import tbpweb_keys. Please make sure tbpweb_keys.py exists '
          'on the path, and that there are no errors in the module.')
    sys.exit(1)

# Determine the path of your local workspace.
WORKSPACE_DJANGO_ROOT = os.path.abspath(
    os.path.dirname(os.path.dirname(globals()['__file__'])))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
SHOW_DEBUG_TOOLBAR = False  # Custom flag to show the Django Debug Toolbar

# Email stuff
CONST_CURR_TBP_IT = "tbpwebsite@tbp.berkeley.edu"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Host for sending e-mail.
EMAIL_HOST = "smtp.ocf.berkeley.edu" #"smtp.gmail.com"

# Port for sending e-mail.
EMAIL_PORT = 587

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = CONST_CURR_TBP_IT #"tbpwebsite@tbp.berkeley.edu"
EMAIL_USE_TLS = True

NO_REPLY_EMAIL = "no-reply@tbp.berkeley.edu"

# Email password as EMAIL_HOST_PASSWORD on Production Keys

# Set admins and managers
ADMINS = [('TBP', CONST_CURR_TBP_IT)] #"website-errors@tbp.berkeley.edu")]
MANAGERS = ADMINS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_DIRS = [
    os.path.join(WORKSPACE_DJANGO_ROOT, 'templates'),
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # You shouldn't be using this database
        'NAME': 'improper_tbpweb.db',
    }
}

# Use a default local memory cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Use 'app_label.model_name'
# Currently use django.contrib.auth.User.
AUTH_USER_MODEL = 'auth.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'accounts:login'
LOGOUT_URL = 'accounts:logout'
REDIRECT_FIELD_NAME = 'next'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
]

# Set the SITE_ID to 1, since we only need one site
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

if USE_TZ:
    # Raise an error when dealing with timezone-unaware objects.
    warnings.filterwarnings(
        'error', r'DateTimeField received a naive datetime',
        RuntimeWarning, r'django\.db\.models\.fields')

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(WORKSPACE_DJANGO_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(WORKSPACE_DJANGO_ROOT, 'static/')

# URL prefix for static files.
STATIC_URL = '/static/'

# Additional locations of static files
# STATICFILES_DIRS = (
#     # Put strings here, like "/home/html/static" or "C:/www/django/static".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
#     os.path.join(WORKSPACE_DJANGO_ROOT, 'static/'),
# )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # django-compressor file finder:
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = tbpweb_keys.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')] + TEMPLATE_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'base.context_processors.local_env',
                'notifications.context_processors.notifications'
            ],
        },
    },
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'settings.wsgi.application'

DJANGO_CONTRIB_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',  # Necessary for flatpages
    'django.contrib.staticfiles',
]

# All projects that we write (and thus, need to be tested) should go here.
PROJECT_APPS = [
    'accounts',
    'achievements',
    'alumni',
    'base',
    'candidates',
    'companies',
    'courses',
    'course_files',
    'course_surveys',
    'emailer',
    'events',
    'exams',
    'houses',
    'minutes',
    'newsreel',
    'notifications',
    'past_presidents',
    'project_reports',
    'quote_board',
    'resumes',
    'syllabi',
    'user_profiles',
    'utils',
    'videos',
    'vote',
]

# Third-party apps belong here, since we won't use them for testing.
THIRD_PARTY_APPS = [
    'chosen',
    'compressor',
    'debug_toolbar',
    'easy_thumbnails',
    'localflavor',
]

# This is the actual variable that django looks at.
INSTALLED_APPS = DJANGO_CONTRIB_APPS + PROJECT_APPS + THIRD_PARTY_APPS


###############################################################################
# Import any extra settings to override default settings.
###############################################################################
try:
    # pylint: disable=W0401,W0614
    from .project import *
    from .third_party import *
except ImportError as err:
    # If the file doesn't exist, print a warning message but do not fail.
    print('WARNING: %s' % str(err))
