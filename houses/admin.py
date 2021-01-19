from django.contrib import admin

from quark.houses.models import House
from quark.houses.models import HouseMember


class HouseAdmin(admin.ModelAdmin):
    fields = ('name', 'mailing_list')
    list_display = ('name', 'mailing_list')


class HouseMemberAdmin(admin.ModelAdmin):
    search_fields = (
        'house__name', 'user__first_name', 'user__last_name',
        'user__username')
    list_display = ('user', 'house', 'term')

admin.site.register(House, HouseAdmin)
admin.site.register(HouseMember, HouseMemberAdmin)
