from django.conf import settings
from django.urls import include
from django.urls import re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView


admin.autodiscover()


urlpatterns = [
    re_path(r'^', include('base.urls')),
    re_path(r'^accounts/', include('accounts.urls')),
    re_path(r'^achievements/', include('achievements.urls')),
    re_path(r'^admin/', include(admin.site.urls)),
    re_path(r'^alumni/', include('alumni.urls')),
    re_path(r'^candidates/', include('candidates.urls')),
    re_path(r'^courses/', include('courses.urls')),
    re_path(r'^email/', include('emailer.urls')),
    re_path(r'^events/', include('events.urls')),
    re_path(r'^exams/', include('exams.urls')),
    re_path(r'^houses/', include('houses.urls')),
    re_path(r'^syllabi/', include('syllabi.urls')),
    re_path(r'^industry/', include('companies.urls')),
    re_path(r'^mailing-lists/', include('mailing_lists.urls')),
    re_path(r'^minutes/', include('minutes.urls')),
    re_path(r'^newsreel/', include('newsreel.urls')),
    re_path(r'^notifications/', include('notifications.urls')),
    re_path(r'^past-presidents/', include('past_presidents.urls')),
    re_path(r'^profile/', include('user_profiles.urls')),
    re_path(r'^project-reports/', include('project_reports.urls')),
    re_path(r'^quote-board/', include('quote_board.urls')),
    re_path(r'^resumes/', include('resumes.urls')),
    re_path(r'^syllabi/', include('syllabi.urls')),
    re_path(r'^videos/', include('videos.urls')),
    re_path(r'^vote/', include('vote.urls')),
]

# Add flatpages URLs
urlpatterns += [
    'django.contrib.flatpages.views',
    re_path(r'^about/$', 'flatpage', {'url': '/about/'}, name='about'),
    re_path(r'^about/contact/$', 'flatpage', {'url': '/about/contact/'},
        name='contact'),
    re_path(r'^about/eligibility/$', 'flatpage', {'url': '/about/eligibility/'},
        name='eligibility'),
    re_path(r'^people/committees/$', 'flatpage', {'url': '/people/committees/'},
        name='committees'),
    re_path(r'^student-resources/$', 'flatpage', {'url': '/student-resources/'},
        name='student-resources'),
    re_path(r'^resume-critique/$', 'flatpage', {'url': '/resume-critique/'},
        name='resume-critique'),
    re_path(r'^mock-interviews/$', 'flatpage', {'url': '/mock-interviews/'},
        name='mock-interviews'),
    re_path(r'^partnership_program/$', 'flatpage', {'url': '/partnership_program/'},
        name='partnership_program'),
]

# Handle page redirects
urlpatterns += [
    re_path(r'^indrel/$', RedirectView.as_view(pattern_name='industry')),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
