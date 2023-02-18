import os

###############################################################################
# Import the proper instance environment settings (dev/production/staging)
# Errors will be raised if the appropriate settings file is not found
###############################################################################
LOCAL_ENV = os.getenv('TBPWEB_MODE', 'dev')
# pylint: disable=W0401,W0614
if LOCAL_ENV == 'dev':
    from .dev import *
elif LOCAL_ENV == 'production':
    from .production import *
else:
    print('WARNING: Invalid value for TBPWEB_MODE: %s' % LOCAL_ENV)
