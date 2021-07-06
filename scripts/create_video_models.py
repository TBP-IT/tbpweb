import os

from quark.videos.models import Video
from quark.videos.models import VideoType
from quark.base.models import Term


past_semesters = ['sp1999', 'fa2003', 'fa2004', 'sp2005',
                  'fa2005', 'sp2007', 'fa2007', 'sp2008',
                  'fa2008', 'sp2009', 'fa2009', 'sp2010',
                  'fa2010', 'sp2011', 'fa2011', 'sp2012',
                  'fa2012', 'sp2013', 'fa2013']

video_types = {'cm': 'Candidate Meeting',
               'eoh': 'Engineering Open House',
               'eos': 'End of Semester',
               'gm1': 'General Meeting 1',
               'gm2': 'General Meeting 2',
               'gm3': 'General Meeting 3',
               'e4k': 'Engineering 4 Kids',
               'senior': 'Senior',
               'coe': 'CoE Promotional Video',
               'photoscav': 'Photo Scavenger Hunt',
               'retreat': 'Retreat'}

sorted_video_types_abbreviations = ['retreat', 'coe', 'cm', 'photoscav',
                                    'gm1', 'gm2', 'gm3', 'eoh', 'e4k',
                                    'senior', 'eos']


def create_video_types():
    # Method for creating video type models
    for type_abbreviation in sorted_video_types_abbreviations:
        video_type = VideoType()
        video_type.name = video_types[type_abbreviation]
        video_type.abbreviation = type_abbreviation
        video_type.save()


def import_videos(
    quark_path='/var/www/quark', videos_path='/media/videos'):
    """
    Method for creating Video models for past video files
    Run this after running create_video_types
    Only need to run this once!
    """

    for semester in past_semesters:
        term = Term.objects.get_by_url_name(semester)

        for video_type in VideoType.objects.all():
            abbrev = video_type.abbreviation
            filename = '{}_{}.mp4'.format(abbrev, semester)

            # strip the leading slash from the videos path since
            # we want the path to start at /var instead of /media
            file_path = os.path.join(
                quark_path, videos_path[1:], semester, filename)
            if os.path.isfile(file_path):
                print '{}{}'.format('Found video file: ', file_path)
                video = Video()
                video.term = term
                video.video_type = video_type
                video.video_file.name = os.path.join(
                    videos_path, semester, filename)
                video.save()
