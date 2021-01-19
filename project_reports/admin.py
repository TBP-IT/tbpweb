from django.contrib import admin

from quark.project_reports.models import ProjectReport
from quark.project_reports.models import ProjectReportFromEmail


class ProjectReportFromEmailAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_prefix')


admin.site.register(ProjectReport)
admin.site.register(ProjectReportFromEmail, ProjectReportFromEmailAdmin)
