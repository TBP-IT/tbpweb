from django.contrib import admin

from videos.models import Video, VideoType


class VideoAdmin(admin.ModelAdmin):
    list_display = ('video_type', 'term', 'video_file', 'video_link')


class VideoTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation')


admin.site.register(Video, VideoAdmin)
admin.site.register(VideoType, VideoTypeAdmin)
