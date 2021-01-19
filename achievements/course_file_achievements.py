from django.db import models

from quark.achievements.models import Achievement
from quark.exams.models import Exam
from quark.shortcuts import get_object_or_none
from quark.syllabi.models import Syllabus


def course_file_achievements(sender, instance, created, **kwargs):
    if instance.submitter:
        assign_lifetime_course_file_achievements(instance)


def assign_lifetime_course_file_achievements(instance):
    # obtain all approved exams submitted by user
    approved_exams = Exam.objects.get_approved().filter(
        submitter=instance.submitter)

    approved_syllabi = Syllabus.objects.get_approved().filter(
        submitter=instance.submitter)

    approved_file_count = approved_exams.count() + approved_syllabi.count()

    # the number of submitted exams needed to get achievements
    benchmarks = [10, 25, 50]

    for benchmark in benchmarks:
        short_name = 'upload_{:02d}_course_files'.format(benchmark)
        achievement = get_object_or_none(Achievement, short_name=short_name)
        if achievement:
            if approved_file_count < benchmark:
                achievement.assign(
                    instance.submitter, acquired=False,
                    progress=approved_file_count)
            else:
                achievement.assign(instance.submitter)


models.signals.post_save.connect(course_file_achievements, sender=Exam)
models.signals.post_save.connect(course_file_achievements, sender=Syllabus)
