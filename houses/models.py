from django.conf import settings
from django.db import models

from quark.base.models import Term


class House(models.Model):
    """A house that contains a subsection of an organization's members.

    HouseMember objects reference Houses to link members to the houses they
    have been a part of.
    """
    name = models.CharField(max_length=16, unique=True)
    mailing_list = models.CharField(
        max_length=16, blank=True,
        help_text='The mailing list name, not including the @domain.')

    def __unicode__(self):
        return self.name


class HouseMember(models.Model):
    """A member of a house."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='housemember')
    term = models.ForeignKey(Term)
    house = models.ForeignKey(House)

    is_leader = models.NullBooleanField(
        default=None,
        help_text='Is this person the house leader?')

    class Meta(object):
        unique_together = (('user', 'term'), ('term', 'house', 'is_leader'))
        permissions = (
            ('view_housemember', 'Can view all houses and members'),
        )

    def __unicode__(self):
        return '%s - %s (%s %d)' % (
            self.user.userprofile.get_common_name(), self.house.name,
            self.term.get_term_display(), self.term.year)
