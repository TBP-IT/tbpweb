from django.urls import re_path
from courses.views import CourseDetailView, CourseListView, CourseDepartmentListView, \
                          CourseCreateView, CourseEditView, CourseDeleteView, \
                          InstructorCreateView, InstructorDepartmentListView, \
                          InstructorDeleteView, InstructorDetailView, InstructorEditView, \
                          InstructorListView, listCourses


urlpatterns = [
    re_path(r'^list', listCourses, name='search'),
    re_path(r'^$', CourseDepartmentListView.as_view(),
        name='course-department-list'),
    re_path(r'^(?P<dept_slug>(?!instructors)[A-Za-z-]+)/$',
        CourseListView.as_view(), name='course-list'),
    re_path(r'^(?P<dept_slug>(?!instructors)[A-Za-z-]+)/'
        '(?P<course_num>[A-Za-z0-9w-]+)/$',
        CourseDetailView.as_view(), name='course-detail'),
    re_path(r'^add$', CourseCreateView.as_view(),
        name='add-course'),
    re_path(r'^(?P<cous_pk>[0-9]+)/edit/$', CourseEditView.as_view(),
        name='edit-course'),
    re_path(r'^(?P<cous_pk>[0-9]+)/delete/$',
        CourseDeleteView.as_view(), name='delete-course'),
    re_path(r'^instructors/$', InstructorDepartmentListView.as_view(),
        name='instructor-department-list'),
    re_path(r'^instructors/add/$', InstructorCreateView.as_view(),
        name='add-instructor'),
    re_path(r'^instructors/(?P<dept_slug>[A-Za-z-]+)/$',
        InstructorListView.as_view(), name='instructor-list'),
    re_path(r'^instructors/(?P<inst_pk>[0-9]+)/$',
        InstructorDetailView.as_view(), name='instructor-detail'),
    re_path(r'^instructors/(?P<inst_pk>[0-9]+)/edit/$',
        InstructorEditView.as_view(), name='edit-instructor'),
    re_path(r'^instructors/(?P<inst_pk>[0-9]+)/delete/$',
        InstructorDeleteView.as_view(), name='delete-instructor'),
]
