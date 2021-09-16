from django.urls import patterns
from django.urls import url

from courses.views import CourseDetailView
from courses.views import CourseListView
from courses.views import CourseDepartmentListView
from courses.views import CourseCreateView
from courses.views import CourseEditView
from courses.views import CourseDeleteView
from courses.views import InstructorCreateView
from courses.views import InstructorDepartmentListView
from courses.views import InstructorDeleteView
from courses.views import InstructorDetailView
from courses.views import InstructorEditView
from courses.views import InstructorListView
from courses.views import listCourses


urlpatterns = patterns(
    '',
    url(r'^list', listCourses, name='search'),
    url(r'^$', CourseDepartmentListView.as_view(),
        name='course-department-list'),
    url(r'^(?P<dept_slug>(?!instructors)[A-Za-z-]+)/$',
        CourseListView.as_view(), name='course-list'),
    url(r'^(?P<dept_slug>(?!instructors)[A-Za-z-]+)/'
        '(?P<course_num>[A-Za-z0-9w-]+)/$',
        CourseDetailView.as_view(), name='course-detail'),
    url(r'^add$', CourseCreateView.as_view(),
        name='add-course'),
    url(r'^(?P<cous_pk>[0-9]+)/edit/$', CourseEditView.as_view(),
        name='edit-course'),
    url(r'^(?P<cous_pk>[0-9]+)/delete/$',
        CourseDeleteView.as_view(), name='delete-course'),
    url(r'^instructors/$', InstructorDepartmentListView.as_view(),
        name='instructor-department-list'),
    url(r'^instructors/add/$', InstructorCreateView.as_view(),
        name='add-instructor'),
    url(r'^instructors/(?P<dept_slug>[A-Za-z-]+)/$',
        InstructorListView.as_view(), name='instructor-list'),
    url(r'^instructors/(?P<inst_pk>[0-9]+)/$',
        InstructorDetailView.as_view(), name='instructor-detail'),
    url(r'^instructors/(?P<inst_pk>[0-9]+)/edit/$',
        InstructorEditView.as_view(), name='edit-instructor'),
    url(r'^instructors/(?P<inst_pk>[0-9]+)/delete/$',
        InstructorDeleteView.as_view(), name='delete-instructor'),
)
