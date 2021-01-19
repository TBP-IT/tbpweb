from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models


class Alumnus(models.Model):
    """An alumnus class for participants in Fogeys First.

    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    description = models.TextField(default='', blank=True)
    dream = models.TextField(default='', blank=True)
    hobbies = models.TextField(default='', blank=True)
    location = models.CharField(max_length=100, default='', blank=True)
    occupation = models.CharField(max_length=100, default='', blank=True)
    time_investment = models.ManyToManyField('TimeInvestment',
                                             related_name='+', blank=True)
    college_activities = models.TextField(default='', blank=True)
    discussion_topics = models.ManyToManyField('DiscussionTopic',
                                               related_name='+', blank=True)

    class Meta(object):
        permissions = (
            ('view_alumnus', 'Can view all alumni'),
        )
        verbose_name_plural = 'Alumni'

    def __unicode__(self):
        return '{user}'.format(user=self.user)

    def get_absolute_url(self):
        return reverse('alumni:edit-alumnus', args=(self.pk,))


class DiscussionTopic(models.Model):
    """Discussion topics represent areas of possible discussion for alumni."""
    name = models.CharField(
        max_length=64, help_text='The name of the topic to be displayed '
                                 'on the page.')
    icon = models.CharField(
        max_length=64, help_text='The name of the Font Awesome icon '
                                 'corresponding to this topic (\'fa fa-\' '
                                 'is implicitly included at the beginning).')

    def __unicode__(self):
        return self.name


class TimeInvestment(models.Model):
    """Time investment entries are alumni's preferred means of communication
       with current TBP members."""
    name = models.CharField(
        max_length=64, help_text='The name of the communication method to be '
                                 'displayed on the page.')
    short_name = models.CharField(
        max_length=64, help_text='The name of the communication method to be '
                                 'displayed in checkboxes used for sorting.')
    icon = models.CharField(
        max_length=64, help_text='The name of the Font Awesome icon '
                                 'corresponding to this topic (\'fa fa-\' '
                                 'is implicitly included at the beginning).')

    def __unicode__(self):
        return self.name
