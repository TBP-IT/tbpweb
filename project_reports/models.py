import re
from datetime import date

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from quark.base.models import OfficerPosition
from quark.base.models import Term
from quark.notifications.models import Notification
from quark.shortcuts import get_object_or_none

from picklefield.fields import PickledObjectField
import tblib.pickling_support

tblib.pickling_support.install()


class ProjectReport(models.Model):
    PROJECT_AREA_CHOICES = (
        ('cl', 'Community/Liberal Culture'),
        ('uc', 'University/College'),
        ('pe', 'Profession/Engineering'),
        ('cs', 'Chapter/Social'),
        ('ep', 'Education/Prof. Dev.'),
        ('km', 'K-12/MindSET'))

    term = models.ForeignKey(Term)
    date = models.DateField()
    title = models.CharField(max_length=80)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    committee = models.ForeignKey(OfficerPosition)
    area = models.CharField(
        max_length=2, choices=PROJECT_AREA_CHOICES, blank=True)
    organize_hours = models.PositiveSmallIntegerField(
        default=0, help_text='Number of hours spent organizing the event.')
    participate_hours = models.PositiveSmallIntegerField(
        default=0, help_text=('Number of hours spent by a single person '
                              'participating in the event.'))
    is_new = models.BooleanField(
        default=False, help_text=('Was this the first time an event like this '
                                  'had been held?'))
    other_group = models.CharField(
        max_length=60, blank=True,
        help_text=('Name(s) of any other organization that also participated '
                   'and/or helped organize the event.'))

    description = models.TextField(
        help_text=('General description of event, vendors, '
                   'sponsors, etc. Use markdown formatting.'))
    purpose = models.TextField()
    organization = models.TextField(
        help_text=('Setup, number of people involved, clean-up, etc.'))
    cost = models.TextField()
    problems = models.TextField()
    results = models.TextField()

    officer_list = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='officer_list+', blank=True)
    member_list = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='member_list+', blank=True)
    candidate_list = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='candidate_list+', blank=True)
    non_tbp = models.PositiveSmallIntegerField(
        default=0, help_text='Number of non-TBP participants')
    complete = models.BooleanField(
        default=False, help_text='Is this project report finished?')
    first_completed_at = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='pr', blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s (%s)' % (self.title, self.date)

    def save(self, *args, **kwargs):
        if self.first_completed_at is None and self.complete:
            self.first_completed_at = timezone.now()
        elif not self.complete:
            self.first_completed_at = None
        super(ProjectReport, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project-reports:detail', args=(self.pk,))

    def word_count(self):
        text = [self.description, self.purpose, self.organization, self.cost,
                self.problems, self.results]
        return len([x for x in re.split(r'\W+', ' '.join(text)) if len(x) > 0])

    def is_past_due(self):
        return date.today() > self.date and not self.complete

    class Meta(object):
        ordering = ('date',)
        permissions = (
            ('view_project_reports', 'Can view all project reports'),
        )


class ProjectReportFromEmail(models.Model):
    """An email address from which project report reminders are sent.
    """
    name = models.CharField(max_length=100)

    # Email address without the domain name (the "local part")
    email_prefix = models.CharField(max_length=100, unique=True)

    class Meta(object):
        ordering = ('name',)
        verbose_name = 'Project report reminder email address'


class ProjectReportBook(models.Model):
    """A project report book. Generating a project report book is very slow,
    so the result needs to be cached in the database.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    terms = models.ManyToManyField(Term)
    presidents_letter = models.TextField()
    pdf = models.FileField(upload_to='project_report_books/', blank=True)
    exception = PickledObjectField(null=True)


def project_report_notification(sender, instance, created, **kwargs):
    """Clear the notification if it exists for the project report when it is
    completed.
    """
    if instance.complete:
        notification = get_object_or_none(
            Notification,
            user=instance.author,
            content_type=ContentType.objects.get_for_model(ProjectReport),
            object_pk=instance.pk)
        if notification:
            notification.cleared = True
            notification.save()


def project_report_notification_delete(sender, instance, **kwargs):
    """Delete the notification if it exists for the project report when it is
    deleted.
    """
    notification = get_object_or_none(
        Notification,
        user=instance.author,
        content_type=ContentType.objects.get_for_model(ProjectReport),
        object_pk=instance.pk)
    if notification:
        notification.delete()


def project_report_book_notification(sender, instance, created, **kwargs):
    if not created:
        notification = get_object_or_none(
            Notification,
            user=instance.user,
            content_type=ContentType.objects.get_for_model(ProjectReportBook),
            object_pk=instance.pk)
        if notification:
            return
        Notification.objects.create(
            user=instance.user,
            status=Notification.POSITIVE,
            content_type=ContentType.objects.get_for_model(ProjectReportBook),
            object_pk=instance.pk,
            title='Project Report Book Generated',
            subtitle='click to download',
            description='',
            url=reverse('project-reports:download-book', args=(instance.pk,)))


models.signals.post_save.connect(
    project_report_notification, sender=ProjectReport)
models.signals.post_delete.connect(
    project_report_notification_delete, sender=ProjectReport)
models.signals.post_save.connect(
    project_report_book_notification, sender=ProjectReportBook)
