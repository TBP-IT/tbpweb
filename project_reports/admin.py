from django.contrib import admin

from project_reports.models import ProjectReport
from project_reports.models import ProjectReportFromEmail


class ProjectReportFromEmailAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_prefix')


admin.site.register(ProjectReport)
admin.site.register(ProjectReportFromEmail, ProjectReportFromEmailAdmin)
