from django.conf import settings
from django.db import models

from base.models import Term
from courses.models import Course
from courses.models import Instructor


class Survey(models.Model):
    RATING_CHOICES = (
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7')
    )
    RATING_CHOICES_NULL = RATING_CHOICES + ((None, 'N/A'),)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    prof_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        help_text='1 being terrible, 7 being excellent')
    course_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        help_text='1 being terrible, 7 being excellent')
    time_commitment = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        help_text='Higher number means more time commitment.')
    exam_difficulty = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES_NULL, blank=True, null=True,
        help_text='Higher number means more difficult.')
    hw_difficulty = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES_NULL, blank=True, null=True,
        help_text='Higher number means more difficult.')
    comments = models.TextField(
        blank=True,
        help_text=('Did you like the course and professor? What would you '
                   'tell a future student?'))
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s (%s)' % (self.course, self.submitter)

    class Meta(object):
        ordering = ('course', 'instructor', '-term')
