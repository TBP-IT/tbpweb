from django.contrib import admin

from achievements.models import Achievement, AchievementIcon, UserAchievement

#from achievements.event_achievements import *


class AchievementAdmin(admin.ModelAdmin):
    #fields = (
    #    'name', 'description', 'points', 'goal', 'privacy', 'manual', 'rank',
    #    'sequence', 'category', 'short_name')
    search_fields = ('name', 'points')
    list_filter = ('privacy', 'manual', 'repeatable')
    list_display = ('name', 'points', 'goal', 'privacy', 'manual', 'rank')


class AchievementIconAdmin(admin.ModelAdmin):
    search_fields = (
        '^achievement__name', '^creator__first_name', '^creator__last_name',
        '^creator__username')
    list_display = ('achievement', 'creator')


class UserAchievementAdmin(admin.ModelAdmin):
    search_fields = (
        'achievement__name', '^user__first_name', '^user__last_name',
        '^user__username')
    list_display = ('achievement', 'user', 'acquired', 'progress',
                    'assigner', 'term')

admin.site.register(Achievement, AchievementAdmin)
admin.site.register(AchievementIcon, AchievementIconAdmin)
admin.site.register(UserAchievement, UserAchievementAdmin)
