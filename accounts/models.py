from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
import uuid

class APIKey(models.Model):
    """A unique key for each user, which can be used for validating special
    access.
    For instance, an API key can be passed as a URL parameter with the user's
    username to validate what the given user has access to.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name='api_key',
                                on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        verbose_name = 'API key'

    def __str__(self):
        return '{}: {}'.format(self.user, self.key)


def create_api_key(sender, instance, created, **kwargs):
    """A receiver for a signal to automatically create an APIKey for users."""
    if created:
        APIKey.objects.create(user=instance)


models.signals.post_save.connect(create_api_key, sender=get_user_model())
