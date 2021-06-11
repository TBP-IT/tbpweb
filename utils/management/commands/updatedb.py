from django.core.management.base import BaseCommand

from tbpweb.utils import update_db


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        update_db()
