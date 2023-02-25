"""
Settings introduced by tbpweb
Note: The values given here are intended for development. A production
environment would overwrite these. The base and site-specific settings files
must not overwrite these.
"""

# Custom setting used to include a short tag for the site in relevant content
# (like automatic email subject lines):
SITE_TAG = 'TBP'

HOSTNAME = 'tbp.berkeley.edu'

DEFAULT_FROM_EMAIL = 'tbpwebsite@' + HOSTNAME
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# An email address for receiving test emails
TEST_ADDRESS = 'test@' + HOSTNAME

# ResumeQ is used to automatically assign officers for critiquing resumes.
# The short_name of the position of officers that are assigned resume_critiques:
RESUMEQ_OFFICER_POSITION = 'prodev'

RESUMEQ_ADDRESS = TEST_ADDRESS

# Email addresses
INDREL_ADDRESS = TEST_ADDRESS
IT_ADDRESS = TEST_ADDRESS
STARS_ADDRESS = TEST_ADDRESS

# Do we send spam notices?
INDREL_SEND_SPAM_NOTICE = True
# where?
INDREL_NOTICE_TO = TEST_ADDRESS

# Do we send messages known to be spam?
INDREL_SEND_SPAM = False
# where?
INDREL_SPAM_TO = TEST_ADDRESS

# Valid username regex
# Please use raw string notation (i.e. r'text') to keep regex sane.
VALID_USERNAME = r'^[a-z][a-z0-9]{2,29}$'
USERNAME_HELPTEXT = ('Username must be 3-30 characters, start with a letter, '
                     'and use only lowercase letters and numbers.')

# Valid types are 'semester' and 'quarter'.
TERM_TYPE = 'semester'
