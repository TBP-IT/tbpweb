from functools import wraps
import magic

from django.shortcuts import _get_queryset


def get_object_or_none(klass, *args, **kwargs):
    """
    This shortcut is modified from django.shortcuts.get_object_or_404
    Uses get() to return an object, or returns None if the object does not
    exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more
    than one object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def get_file_mimetype(file_object):
    """Return the file mimetype (using python-magic) for the given file.

    This method is useful for verifying the file type of uploaded files so that
    someone cannot upload a disallowed file type by simply changing the file
    extension.
    """
    # If the uploaded file is greater than 2.5MB (if multiple_chunks() returns
    # True), then it will be stored temporarily on disk; otherwise, it will be
    # stored in memory.
    if file_object.multiple_chunks():
        output = magic.from_file(file_object.temporary_file_path(), mime=True)
    else:
        output = magic.from_buffer(file_object.read(), mime=True)
    return output


def disable_for_loaddata(signal_handler):
    """Decorator that turns off signal handlers when loading fixture data.

    Taken from the Django documentation:
    https://docs.djangoproject.com/en/dev/ref/django-admin/
    #loaddata-fixture-fixture
    """
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs['raw']:
            return
        signal_handler(*args, **kwargs)
    return wrapper


def create_leaderboard(leaders, max_width):
    """Function that generates a leader_list for use in leaderboard views.

    This method takes in a queryset of leaders which have some annotated score,
    for example a count of attended events or points from achievements, and
    the maximum width a bar on the leaderboard can be. It returns a leader_list
    where each entry is a dictionary that includes the user, their rank on the
    leaderboard (1st, 2nd, etc.), and their leaderboard width factor, which is
    the width that user's bar takes given their score.
    """
    if len(leaders) > 0:
        max_score = leaders[0].score or 0
    else:
        max_score = 0

    leader_list = []
    if max_score > 0:  # Ensure there is no dividing by zero
        prev_value = -1
        prev_rank = 1

        for i, leader in enumerate(leaders, start=prev_rank):
            # factor is used for CSS width property (percentage).  2.5 is added
            # to every factor to make sure that there is enough room for text
            # to be displayed.
            factor = 2.5 + leader.score * (max_width - 2.5) / max_score

            if leader.score == prev_value:
                rank = prev_rank
            else:
                rank = i
            prev_rank = rank
            prev_value = leader.score

            # Add the leader entry to the list
            leader_list.append({'user': leader,
                                'factor': factor,
                                'rank': rank})

        return leader_list
