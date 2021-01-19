import os

from django.db import models

from quark.base.models import Term


class VideoType(models.Model):
    name = models.CharField(max_length=60, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return self.name


class Video(models.Model):
    # TODO: Increase max file upload size so historians can upload
    # videos onto the TBP server
    def rename_file(self, filename):
        """
        Renames the video file into the format VideoType_SemesterYear
        and puts it in the directory MEDIA_ROOT/videos/SemesterYear
        ex: /media/videos/sp2013/cm_sp2013.mp4
        """
        video_type_abbreviation = self.video_type.abbreviation
        video_term = self.term.get_url_name()
        file_ext = os.path.splitext(filename)[1]
        filename = '{}_{}{}'.format(
            video_type_abbreviation, video_term, file_ext)
        file_path = os.path.join('videos', video_term, filename)
        return file_path

    term = models.ForeignKey(Term)
    video_type = models.ForeignKey(VideoType)
    video_file = models.FileField(upload_to=rename_file)
    video_link = models.URLField(
        help_text='If the video cannot be hosted on another website such '
                  'as Youtube, please contact IT to upload the video onto '
                  'the TBP server.')

    class Meta(object):
        unique_together = (('term', 'video_type'),)
