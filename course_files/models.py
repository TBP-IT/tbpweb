import os

from abc import abstractmethod
from django.conf import settings
from django.db import models
from uuidfield import UUIDField

from quark.courses.models import CourseInstance
from quark.courses.models import Instructor


def generate_courseitem_filepath(instance, filename):
    """Generate a file name and path for the given file.

    Used for the file upload_to function.

    Files are stored in directories inside the file directory
    corresponding to the first two characters of the unique id. File names
    consist of the whole unique 32-character alphanumeric id, without hyphens.
    """
    instance.file_ext = os.path.splitext(filename)[1]
    return instance.get_relative_pathname()


class GenericCourseFile(models.Model):
    """Abstract class for different course-related files."""

    course_instance = models.ForeignKey(CourseInstance)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                  blank=True)
    file_ext = models.CharField(max_length=5)  # includes the period
    # The file must be verified manually be an officer:
    verified = models.BooleanField(default=False, blank=True)
    flags = models.PositiveSmallIntegerField(default=0)
    blacklisted = models.BooleanField(default=False)
    unique_id = UUIDField(auto=True)

    @property
    def course(self):
        return self.course_instance.course

    @property
    def term(self):
        return self.course_instance.term

    @property
    def instructors(self):
        """Return a QuerySet of all instructors associated with the file."""
        return self.course_instance.instructors.all()

    def is_approved(self):
        """A file is 'approved' if it meets all of the following conditions:
          1. Verified by an officer
          2. Is not associated with a blacklisted instructor
          3. Has less than or equal to GenericFlag.LIMIT flags
        """
        return (self.verified and not self.blacklisted
                and self.flags <= GenericFlag.LIMIT)

    def has_permission(self):
        """Return whether this file has permission from all instructors
        associated with it.
        """
        return not self.course_instance.instructors.filter(
            instructorpermission__permission_allowed=False).exists()

    @abstractmethod
    def get_folder(self):
        """Return the path of the folder where the file is."""
        return ''

    @abstractmethod
    def get_relative_pathname(self):
        """Return the relative path of the file from inside the media
        root."""
        return ''

    @abstractmethod
    def get_absolute_pathname(self):
        """Return the absolute path of the file."""
        return ''

    @abstractmethod
    def get_absolute_url(self):
        return ''

    @abstractmethod
    def get_download_file_name(self):
        """Return the file name of the file when it is downloaded."""
        return ''

    class Meta(object):
        abstract = True


class GenericInstructorPermission(models.Model):
    """Abstract class for defining instructor permissions for course files."""

    instructor = models.OneToOneField(Instructor)
    help_text = 'Has this instructor given permission to post files?'
    permission_allowed = models.BooleanField(help_text=help_text)
    correspondence = models.TextField(
        blank=True,
        help_text='Reason for why permission was or was not given.')

    class Meta(object):
        ordering = ('instructor',)
        abstract = True

    def __unicode__(self):
        return '{} Permission'.format(unicode(self.instructor))


class GenericFlag(models.Model):
    """Abstract class for flagging course files."""
    # Constant for how many times a file can be flagged before being hidden
    LIMIT = 2

    reason = models.TextField(blank=False,
                              help_text='Why is this item being flagged?')
    created = models.DateTimeField(auto_now_add=True)
    # After flagged item is dealt with, an explanation about how it was
    # resolved should be added, and then it should be de-flagged
    resolution = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True
