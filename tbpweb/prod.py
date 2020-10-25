from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'localhost', 'tbp.apphost.ocf.berkeley.edu'
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = 'https://www.ocf.berkeley.edu/~tbp/static/'
STATIC_ROOT = '/home/t/tb/tbp/public_html/tbpweb/static'

# Media files (user-uploaded files)
# https://docs.djangoproject.com/en/2.1/topics/files/
MEDIA_URL = 'https://www.ocf.berkeley.edu/~tbp/media/'
MEDIA_ROOT = '/home/t/tb/tbp/public_html/tbpweb/media'
