from django.conf import settings
from django.urls import include
from django.urls import path, re_path
from django.contrib.flatpages import views
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView


admin.autodiscover()


urlpatterns = [
    path('', include(('base.urls', 'base'), namespace='base')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('achievements/', include(('achievements.urls', 'achievements'), namespace='achievements')),
    path('admin/', admin.site.urls),
    path('alumni/', include(('alumni.urls', 'alumni'), namespace='alumni')),
    path('candidates/', include(('candidates.urls', 'candidates'), namespace='candidates')),
    path('courses/', include(('courses.urls', 'courses'), namespace='courses')),
    path('email/', include(('emailer.urls', 'emailer'), namespace='emailer')),
    path('events/', include(('events.urls', 'events'), namespace='events')),
    path('exams/', include(('exams.urls', 'exams'), namespace='exams')),
    path('houses/', include(('houses.urls', 'houses'), namespace='houses')),
    path('syllabi/', include(('syllabi.urls', 'syllabi'), namespace='syllabi')),
    path('industry/', include(('companies.urls', 'companies'), namespace='companies')),
    path('minutes/', include(('minutes.urls', 'minutes'), namespace='minutes')),
    path('newsreel/', include(('newsreel.urls', 'newsreel'), namespace='newsreel')),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),
    path('past-presidents/', include(('past_presidents.urls', 'past-presidents'), namespace='past-presidents')),
    path('profile/', include(('user_profiles.urls', 'user-profiles'), namespace='user-profiles')),
    path('project-reports/', include(('project_reports.urls', 'project-reports'), namespace='project-reports')),
    path('quote-board/', include(('quote_board.urls', 'quote-board'), namespace='quote-board')),
    path('resumes/', include(('resumes.urls', 'resumes'), namespace='resumes')),
    path('videos/', include(('videos.urls', 'videos'), namespace='videos')),
    path('vote/', include(('vote.urls', 'vote'), namespace='vote')),
]

# Add flatpages URLs
urlpatterns += [
    path('about/', views.flatpage, {'url': '/about/'}, name='about'),
    path('about/contact/', views.flatpage, {'url': '/about/contact/'},
        name='contact'),
    path('about/eligibility/', views.flatpage, {'url': '/about/eligibility/'},
        name='eligibility'),
    path('people/committees/', views.flatpage, {'url': '/people/committees/'},
        name='committees'),
    path('student-resources/', views.flatpage, {'url': '/student-resources/'},
        name='student-resources'),
    path('resume-critique/', views.flatpage, {'url': '/resume-critique/'},
        name='resume-critique'),
    path('mock-interviews/', views.flatpage, {'url': '/mock-interviews/'},
        name='mock-interviews'),
    path('partnership_program/', views.flatpage, {'url': '/partnership_program/'},
        name='partnership_program'),
	path('gallery/', views.flatpage, {'url': '/gallery/'}, name='gallery')
]

# Handle page redirects
urlpatterns += [
    path('indrel/', RedirectView.as_view(pattern_name='industry')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if settings.SHOW_DEBUG_TOOLBAR:

        import debug_toolbar

        urlpatterns += [
            path('__debug__', include(debug_toolbar.urls)),
        ]
