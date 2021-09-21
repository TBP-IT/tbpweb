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
    path('', include('base.urls')),
    path('accounts/', include('accounts.urls')),
    path('achievements/', include('achievements.urls')),
    path('admin/', admin.site.urls),
    path('alumni/', include('alumni.urls')),
    path('candidates/', include('candidates.urls')),
    path('courses/', include('courses.urls')),
    path('email/', include('emailer.urls')),
    path('events/', include('events.urls')),
    path('exams/', include('exams.urls')),
    path('houses/', include('houses.urls')),
    path('syllabi/', include('syllabi.urls')),
    path('industry/', include('companies.urls')),
    path('mailing-lists/', include('mailing_lists.urls')),
    path('minutes/', include('minutes.urls')),
    path('newsreel/', include('newsreel.urls')),
    path('notifications/', include('notifications.urls')),
    path('past-presidents/', include('past_presidents.urls')),
    path('profile/', include('user_profiles.urls')),
    path('project-reports/', include('project_reports.urls')),
    path('quote-board/', include('quote_board.urls')),
    path('resumes/', include('resumes.urls')),
    path('syllabi/', include('syllabi.urls')),
    path('videos/', include('videos.urls')),
    path('vote/', include('vote.urls')),
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
]

# Handle page redirects
urlpatterns += [
    path('indrel/', RedirectView.as_view(pattern_name='industry')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns += [
        path('__debug__', include(debug_toolbar.urls)),
    ]
