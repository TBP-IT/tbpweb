from django.conf.urls import patterns
from django.conf.urls import url

from tbpweb.achievements.views import AchievementDetailView
from tbpweb.achievements.views import LeaderboardListView
from tbpweb.achievements.views import UserAchievementAssignView
from tbpweb.achievements.views import UserAchievementListView


urlpatterns = patterns(
    '',
    url(r'^leaderboard/$', LeaderboardListView.as_view(), name='leaderboard'),
    url(r'^assign/$', UserAchievementAssignView.as_view(), name='assign'),
    url(r'^(?P<achievement_short_name>\w+)/$',
        AchievementDetailView.as_view(), name='detail'),
    url(r'^user/(?P<user_id>\d+)/$',
        UserAchievementListView.as_view(), name='user'),
)
