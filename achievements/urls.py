from django.urls import re_path

from achievements.views import AchievementDetailView
from achievements.views import LeaderboardListView
from achievements.views import UserAchievementAssignView
from achievements.views import UserAchievementListView


urlpatterns = [
    re_path(r'^leaderboard/$', LeaderboardListView.as_view(), name='leaderboard'),
    re_path(r'^assign/$', UserAchievementAssignView.as_view(), name='assign'),
    re_path(r'^(?P<achievement_short_name>\w+)/$',
        AchievementDetailView.as_view(), name='detail'),
    re_path(r'^user/(?P<user_id>\d+)/$',
        UserAchievementListView.as_view(), name='user'),
]
