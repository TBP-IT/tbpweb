# pylint: disable=F0401
import tbpweb_keys
from tbpweb.settings.project import HOSTNAME
from tbpweb.settings.project import RESUMEQ_OFFICER_POSITION


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('TBP IT', 'it-notice@' + HOSTNAME),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tbpweb_prod',
        'USER': 'tbpweb',
        'PASSWORD': tbpweb_keys.PROD_DB_PASSWORD,
    }
}

# Only use LDAP in production/staging
USE_LDAP = True

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

# ALLOWED_HOSTS = [
#     'localhost', 'tbp.apphost.ocf.berkeley.edu'
# ]

# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/2.1/howto/static-files/
# STATIC_URL = 'https://www.ocf.berkeley.edu/~tbp/static/'
# STATIC_ROOT = '/home/t/tb/tbp/public_html/tbpweb/static'

# # Media files (user-uploaded files)
# # https://docs.djangoproject.com/en/2.1/topics/files/
# MEDIA_URL = 'https://www.ocf.berkeley.edu/~tbp/media/'
# MEDIA_ROOT = '/home/t/tb/tbp/public_html/tbpweb/media'
