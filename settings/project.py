"""
Settings introduced by tbpweb
Note: The values given here are intended for development. A production
environment would overwrite these. The base and site-specific settings files
must not overwrite these.
"""
# pylint: disable=F0401
import settings.tbpweb_keys as tbpweb_keys

# Custom setting used to include a short tag for the site in relevant content
# (like automatic email subject lines):
SITE_TAG = 'TBP'

HOSTNAME = 'tbp-dev.apphost.ocf.berkeley.edu'

DEFAULT_FROM_EMAIL = 'webmaster@' + HOSTNAME
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# An email address for receiving test emails
TEST_ADDRESS = 'test@' + HOSTNAME

# ResumeQ is used to automatically assign officers for critiquing resumes.
# The short_name of the position of officers that are assigned resume_critiques:
RESUMEQ_OFFICER_POSITION = 'prodev'

# Emailer stuff
ENABLE_HELPDESKQ = False

RESUMEQ_ADDRESS = TEST_ADDRESS

# Email addresses
HELPDESK_ADDRESS = TEST_ADDRESS
INDREL_ADDRESS = TEST_ADDRESS
IT_ADDRESS = TEST_ADDRESS
STARS_ADDRESS = TEST_ADDRESS

# Should we cc people who ask us questions?
HELPDESK_CC_ASKER = False

# Do we send spam notices?
HELPDESK_SEND_SPAM_NOTICE = True
INDREL_SEND_SPAM_NOTICE = True
# where?
HELPDESK_NOTICE_TO = TEST_ADDRESS
INDREL_NOTICE_TO = TEST_ADDRESS

# Do we send messages known to be spam?
HELPDESK_SEND_SPAM = False
INDREL_SEND_SPAM = False
# where?
HELPDESK_SPAM_TO = TEST_ADDRESS
INDREL_SPAM_TO = TEST_ADDRESS

# YouTube Secret Stuff
YT_USERNAME = 'BerkeleyTBP'
YT_PRODUCT = 'noiro'
YT_DEVELOPER_KEY = tbpweb_keys.YT_DEVELOPER_KEY
YT_PASSWORD = tbpweb_keys.YT_PASSWORD

# http://www.djangosnippets.org/snippets/1653/
RECAPTCHA_PRIVATE_KEY = tbpweb_keys.RECAPTCHA_PRIVATE_KEY
RECAPTCHA_PUBLIC_KEY = tbpweb_keys.RECAPTCHA_PUBLIC_KEY

# Valid username regex
# Please use raw string notation (i.e. r'text') to keep regex sane.
VALID_USERNAME = r'^[a-z][a-z0-9]{2,29}$'
USERNAME_HELPTEXT = ('Username must be 3-30 characters, start with a letter, '
                     'and use only lowercase letters and numbers.')

# Valid types are 'semester' and 'quarter'.
TERM_TYPE = 'semester'