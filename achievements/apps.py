from django.apps import AppConfig

class AchievementConfig(AppConfig):
    name = 'achievements'
    verbose_name = 'Achievements'
    def ready(self):
        import achievements.course_file_achievements
        import achievements.event_achievements
        import achievements.meta_achievements
        import achievements.officership_achievements