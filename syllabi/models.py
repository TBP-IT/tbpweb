import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_delete
from django.db.models.signals import post_save

from quark.course_files.models import generate_courseitem_filepath
from quark.course_files.models import GenericCourseFile
from quark.course_files.models import GenericFlag
from quark.course_files.models import GenericInstructorPermission
from quark.shortcuts import disable_for_loaddata


class SyllabusManager(models.Manager):
    def get_approved(self):
        """Return a filtered queryset of approved syllabi.

        A syllabi is 'approved' if it meets all of the following conditions:
          1. Verified by an officer
          2. Is not associated with a blacklisted instructor
          3. Has less than or equal to SyllabusFlag.LIMIT flags
        """
        return self.filter(verified=True, blacklisted=False,
                           flags__lte=SyllabusFlag.LIMIT)


class Syllabus(GenericCourseFile):
    # Constants
    SYLLABUS_FILES_LOCATION = 'syllabus_files'

    syllabus_file = models.FileField(upload_to=generate_courseitem_filepath)

    objects = SyllabusManager()

    class Meta(object):
        permissions = (
            ('view_all_syllabi',
             'Can view blacklisted and flagged syllabi'),
        )
        verbose_name_plural = 'Syllabi'

    def get_folder(self):
        """Return the path of the folder where the syllabus file is."""
        return os.path.join(
            settings.MEDIA_ROOT, Syllabus.SYLLABUS_FILES_LOCATION,
            str(self.unique_id)[0:2])

    def get_relative_pathname(self):
        """Return the relative path of the syllabus file from inside the media
        root.
        """
        return os.path.join(Syllabus.SYLLABUS_FILES_LOCATION,
                            str(self.unique_id)[0:2],
                            str(self.unique_id) + self.file_ext)

    def get_absolute_pathname(self):
        """Return the absolute path of the syllabus file."""
        return os.path.join(settings.MEDIA_ROOT, self.get_relative_pathname())

    def get_absolute_url(self):
        return reverse('syllabi:edit', args=(self.pk,))

    def get_download_file_name(self):
        """Return the file name of the syllabus file when it is downloaded."""
        # Use 'unknown' if the course instance does not have a term
        if self.course_instance.term:
            term = self.course_instance.term.get_url_name()
        else:
            term = 'unknown'

        return 'syllabus-{course}-{term}-{instructors}{ext}'.format(
            course=self.course_instance.course.get_url_name(),
            term=term,
            instructors='_'.join([i.last_name for i in self.instructors]),
            ext=self.file_ext)

    def __unicode__(self):
        """Return a human-readable representation of the syllabus file."""
        # Use 'Unknown' if the course instance does not have a term
        if self.course_instance.term:
            term = self.course_instance.term.verbose_name()
        else:
            term = 'Unknown'

        syllabus_unicode = '{term} for {course}'.format(
            term=term,
            course=self.course_instance.course)
        if self.instructors:
            instructors = ', '.join([i.last_name for i in self.instructors])
            return '{}, taught by {}'.format(syllabus_unicode, instructors)
        else:
            return '{} (Instructors Unknown)'.format(syllabus_unicode)


class SyllabusFlag(GenericFlag):
    """Flag an issue with a particular syllabus on the website."""
    syllabus = models.ForeignKey(Syllabus,
                                 help_text='Syllabus that has an issue.')

    def __unicode__(self):
        return '{} Flag'.format(unicode(self.syllabus))


def delete_file(sender, instance, **kwargs):
    """Delete a syllabus file after the syllabus has been deleted,
    if it exists."""
    if bool(instance.syllabus_file):  # check if syllabus file exists
        try:
            instance.syllabus_file.delete()
        except OSError:
            pass
    # if syllabus file has already been deleted, then do nothing and continue
    # with deleting the syllabus model


class InstructorSyllabusPermission(GenericInstructorPermission):
    """Separate set of instructor permissions for syllabi only."""
    # Nothing here, because there are no additional fields we want to define
    pass


@disable_for_loaddata
def update_syllabus_flags(sender, instance, **kwargs):
    """Update the amount of flags a syllabus has every time
    a flag is updated."""
    syllabus = Syllabus.objects.get(pk=instance.syllabus.pk)
    syllabus.flags = SyllabusFlag.objects.filter(syllabus=syllabus,
                                                 resolved=False).count()
    syllabus.save()


@disable_for_loaddata
def update_syllabus_blacklist(sender, instance, **kwargs):
    """Update whether an syllabus is blacklisted every time an instructor
    permission is updated.
    """
    syllabi = Syllabus.objects.filter(
        course_instance__instructors=instance.instructor)
    if instance.permission_allowed is False:
        syllabi.exclude(blacklisted=True).update(blacklisted=True)
    else:
        for syllabus in syllabi:
            if syllabus.has_permission():
                syllabus.blacklisted = False
                syllabus.save()


pre_delete.connect(delete_file, sender=Syllabus)
post_save.connect(update_syllabus_flags, sender=SyllabusFlag)
post_save.connect(update_syllabus_blacklist,
                  sender=InstructorSyllabusPermission)
