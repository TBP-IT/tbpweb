from django.contrib import admin

from alumni.models import Alumnus, DiscussionTopic, TimeInvestment


class AlumnusAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'occupation')
    search_fields = ('^user__first_name', '^user__last_name', '^user__username')


admin.site.register(Alumnus, AlumnusAdmin)
admin.site.register(DiscussionTopic)
admin.site.register(TimeInvestment)
