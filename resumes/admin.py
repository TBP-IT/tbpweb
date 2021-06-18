from django.contrib import admin

from resumes.models import Resume


class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'updated', 'verified', 'critique',
                    'release')
    list_filter = ('verified', 'critique', 'release')


admin.site.register(Resume, ResumeAdmin)
