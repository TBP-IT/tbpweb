from django.contrib import admin

from quark.syllabi.models import Syllabus
from quark.syllabi.models import SyllabusFlag
from quark.syllabi.models import InstructorSyllabusPermission


class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('course_instance', 'instructor_names', 'verified',
                    'flags', 'blacklisted')
    list_filter = ('verified', 'flags', 'blacklisted')
    search_fields = ('course_instance__course__number',
                     'course_instance__course__department__short_name',
                     'course_instance__course__title',
                     'course_instance__instructors__first_name',
                     'course_instance__instructors__last_name')

    def instructor_names(self, obj):
        return ', '.join(
            ['{} {}'.format(instructor.first_name, instructor.last_name)
             for instructor in obj.instructors])
    instructor_names.short_description = 'Instructor(s)'


class SyllabusFlagAdmin(admin.ModelAdmin):
    list_display = ('syllabus', 'created', 'resolved')
    list_filter = ('resolved',)
    search_fields = ('syllabus__course_instance__course__number',
                     'syllabus__course_instance__department__short_name')


class InstructorSyllabusPermissionAdmin(admin.ModelAdmin):
    list_display = ('instructor', 'permission_allowed')
    list_filter = ('permission_allowed', 'instructor__department')
    search_fields = ('instructor__first_name', 'instructor__last_name')


admin.site.register(Syllabus, SyllabusAdmin)
admin.site.register(SyllabusFlag, SyllabusFlagAdmin)
admin.site.register(InstructorSyllabusPermission,
                    InstructorSyllabusPermissionAdmin)
