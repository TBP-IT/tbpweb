"""
WSGI config for tbpweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

try:
    MODE = os.environ['MODE'].lower()
    if (MODE == 'prod'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tbpweb.prod')
    else: os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tbpweb.dev')
except KeyError:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tbpweb.dev')

application = get_wsgi_application()
