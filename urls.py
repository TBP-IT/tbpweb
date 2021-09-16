from django.conf import settings
from django.urls import include
from django.urls import patterns
from django.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^', include('tbpweb.base.urls',
                      app_name='base')),
    url(r'^accounts/', include('tbpweb.accounts.urls',
                               app_name='accounts',
                               namespace='accounts')),
    url(r'^achievements/', include('tbpweb.achievements.urls',
                                   app_name='achievements',
                                   namespace='achievements')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^alumni/', include('tbpweb.alumni.urls',
                             app_name='alumni',
                             namespace='alumni')),
    url(r'^candidates/', include('tbpweb.candidates.urls',
                                 app_name='candidates',
                                 namespace='candidates')),
    url(r'^courses/', include('tbpweb.courses.urls',
                              app_name='courses',
                              namespace='courses')),
    url(r'^email/', include('tbpweb.emailer.urls',
                            app_name='emailer',
                            namespace='emailer')),
    url(r'^events/', include('tbpweb.events.urls',
                             app_name='events',
                             namespace='events')),
    url(r'^exams/', include('tbpweb.exams.urls',
                            app_name='exams',
                            namespace='exams')),
    url(r'^houses/', include('tbpweb.houses.urls',
                             app_name='houses',
                             namespace='houses')),
    url(r'^syllabi/', include('tbpweb.syllabi.urls',
                              app_name='syllabi',
                              namespace='syllabi')),
    url(r'^industry/', include('tbpweb.companies.urls',
                               app_name='companies',
                               namespace='companies')),
    url(r'^mailing-lists/', include('tbpweb.mailing_lists.urls',
                                    app_name='mailing_lists',
                                    namespace='mailing-lists')),
    url(r'^minutes/', include('tbpweb.minutes.urls',
                              app_name='minutes',
                              namespace='minutes')),
    url(r'^newsreel/', include('tbpweb.newsreel.urls',
                               app_name='newsreel',
                               namespace='newsreel')),
    url(r'^notifications/', include('tbpweb.notifications.urls',
                                    app_name='notifications',
                                    namespace='notifications')),
    url(r'^past-presidents/', include('tbpweb.past_presidents.urls',
                                      app_name='past_presidents',
                                      namespace='past-presidents')),
    url(r'^profile/', include('tbpweb.user_profiles.urls',
                              app_name='user_profiles',
                              namespace='user-profiles')),
    url(r'^project-reports/', include('tbpweb.project_reports.urls',
                                      app_name='project_reports',
                                      namespace='project-reports')),
    url(r'^quote-board/', include('tbpweb.quote_board.urls',
                                  app_name='quote_board',
                                  namespace='quote-board')),
    url(r'^resumes/', include('tbpweb.resumes.urls',
                              app_name='resumes',
                              namespace='resumes')),
    url(r'^syllabi/', include('tbpweb.syllabi.urls',
                              app_name='syllabi',
                              namespace='syllabi')),
    url(r'^videos/', include('tbpweb.videos.urls',
                             app_name='videos',
                             namespace='videos')),
    url(r'^vote/', include('tbpweb.vote.urls',
                           app_name='vote',
                           namespace='vote')),
)

# Add flatpages URLs
urlpatterns += patterns(
    'django.contrib.flatpages.views',
    url(r'^about/$', 'flatpage', {'url': '/about/'}, name='about'),
    url(r'^about/contact/$', 'flatpage', {'url': '/about/contact/'},
        name='contact'),
    url(r'^about/eligibility/$', 'flatpage', {'url': '/about/eligibility/'},
        name='eligibility'),
    url(r'^people/committees/$', 'flatpage', {'url': '/people/committees/'},
        name='committees'),
    url(r'^student-resources/$', 'flatpage', {'url': '/student-resources/'},
        name='student-resources'),
    url(r'^resume-critique/$', 'flatpage', {'url': '/resume-critique/'},
        name='resume-critique'),
    url(r'^mock-interviews/$', 'flatpage', {'url': '/mock-interviews/'},
        name='mock-interviews'),
    url(r'^partnership_program/$', 'flatpage', {'url': '/partnership_program/'},
        name='partnership_program'),
)

# Handle page redirects
urlpatterns += patterns(
    '',
    url(r'^indrel/$', RedirectView.as_view(pattern_name='industry')),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
