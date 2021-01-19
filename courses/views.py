from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from json import dumps

from quark.courses.forms import InstructorEditForm
from quark.courses.forms import InstructorForm
from quark.courses.forms import CourseForm
from quark.courses.forms import CourseEditForm
from quark.courses.models import Course
from quark.courses.models import Department
from quark.courses.models import Instructor
from quark.exams.models import Exam
from quark.syllabi.models import Syllabus


def listCourses(request):
    course_data = [[str(x.department.long_name), str(x.department.short_name),
                    str(x.number)]
                   for x in sorted(Course.objects.all(),
                                   key=lambda x: str(x.department.short_name) +
                                   str(x.number))]
    return HttpResponse(dumps(course_data))


def group_exams(unpaired):
    """ Takes in unpaired but sorted exams.
    Returns a list of grouped exams and solutions as tuples.

    If both exam and sol are available, (ex, sol, ex) will be returned.
    If only exam is available, (ex, None, ex) will be returned.
    If only sol is available, (None, sol, sol) will be returned.

    The third tuple item is a hack to fulfill html templating requirements.
    Essentially, a guaranteed non-None item.
    """
    # Give each exam a unique (inst, term, exam#) mapping
    # which will pair exams & sols.
    pairings = dict()
    for exam in unpaired:
        # Use rpartition to remove the exam type from the link.
        mapping, _split, _unused = exam.get_download_file_name().rpartition("-")
        current_pair = [None, None, None]
        if mapping in pairings:
            # Update current mapping.
            current_pair = pairings[mapping]
        if exam.exam_type == Exam.EXAM:
            current_pair[0] = exam
        else:
            current_pair[1] = exam
        # Update the third (non-None) tuple item.
        current_pair[2] = exam
        pairings[mapping] = current_pair
    return pairings.values()


class CourseDepartmentListView(ListView):
    context_object_name = 'departments'
    template_name = 'courses/course_department_list.html'

    def get_queryset(self):
        courses_with_surveys = Course.objects.filter(survey__published=True)
        course_pks = Exam.objects.get_approved().values_list(
            'course_instance__course__pk', flat=True)
        courses_with_exams = Course.objects.filter(pk__in=course_pks)
        course_pks = Syllabus.objects.get_approved().values_list(
            'course_instance__course__pk', flat=True)
        courses_with_syllabi = Course.objects.filter(pk__in=course_pks)

        return Department.objects.filter(
            Q(course__in=courses_with_surveys) |
            Q(course__in=courses_with_exams) |
            Q(course__in=courses_with_syllabi)).distinct()


class CourseListView(ListView):
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'
    dept = None

    def dispatch(self, *args, **kwargs):
        self.dept = get_object_or_404(Department,
                                      slug=self.kwargs['dept_slug'].lower())
        return super(CourseListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        courses_with_exams_pks = Exam.objects.get_approved().values_list(
            'course_instance__course__pk', flat=True)
        courses_with_syllabi_pks = Syllabus.objects.get_approved().values_list(
            'course_instance__course__pk', flat=True)
        courses_query = Course.objects.select_related('department').filter(
            Q(survey__published=True) |
            Q(pk__in=courses_with_exams_pks) |
            Q(pk__in=courses_with_syllabi_pks),
            department=self.dept).distinct()
        if not courses_query.exists():
            raise Http404
        return sorted(courses_query)

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        context['department'] = self.dept
        return context


class CourseDetailView(DetailView):
    context_object_name = 'course'
    template_name = 'courses/course_detail.html'
    course = None

    def get_object(self, queryset=None):
        self.course = get_object_or_404(
            Course,
            department__slug=self.kwargs['dept_slug'].lower(),
            number=self.kwargs['course_num'])
        return self.course

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)

        # Get all exams for the course
        context['exams'] = Exam.objects.get_approved().filter(
            course_instance__course=self.course).select_related(
            'course_instance__term',
            'course_instance__course__department').prefetch_related(
            'course_instance__instructors').order_by('course_instance__term',
                                                     'exam_number', 'exam_type')

        unpaired = context['exams']
        context['paired_exams'] = group_exams(unpaired)

        # Get all syllabi for the course
        context['syllabi'] = Syllabus.objects.get_approved().filter(
            course_instance__course=self.course).select_related(
            'course_instance__term',
            'course_instance__course__department').prefetch_related(
            'course_instance__instructors')

        return context


class CourseCreateView(CreateView):
    form_class = CourseForm
    template_name = 'courses/add_course.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('courses.add_course', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CourseCreateView, self).dispatch(
            *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Course added!')
        return super(CourseCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(CourseCreateView, self).form_invalid(form)


class CourseEditView(UpdateView):
    context_object_name = 'course'
    form_class = CourseEditForm
    model = Course
    pk_url_kwarg = 'cous_pk'
    template_name = 'courses/edit_course.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('courses.change_course', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(CourseEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Changes saved!')
        return super(CourseEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(CourseEditView, self).form_invalid(form)


class CourseDeleteView(DeleteView):
    context_object_name = 'course'
    model = Course
    pk_url_kwarg = 'cous_pk'
    template_name = 'courses/delete_course.html'
    dept_slug = None

    @method_decorator(login_required)
    @method_decorator(
        permission_required('courses.delete_course', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        self.dept_slug = self.get_object().department.slug
        return super(CourseDeleteView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Course deleted!')
        return super(CourseDeleteView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'courses:course-list', kwargs={'dept_slug': self.dept_slug})


class InstructorCreateView(CreateView):
    form_class = InstructorForm
    template_name = 'courses/add_instructor.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('courses.add_instructor', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(InstructorCreateView, self).dispatch(
            *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Instructor added!')
        return super(InstructorCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(InstructorCreateView, self).form_invalid(form)


class InstructorDepartmentListView(ListView):
    context_object_name = 'departments'
    template_name = 'courses/instructor_department_list.html'

    def get_queryset(self):
        instructors = Instructor.objects.all()
        return Department.objects.filter(instructor__in=instructors).distinct()


class InstructorListView(ListView):
    context_object_name = 'instructors'
    template_name = 'courses/instructor_list.html'
    dept = None

    def dispatch(self, *args, **kwargs):
        self.dept = get_object_or_404(
            Department, slug=self.kwargs['dept_slug'].lower())
        return super(InstructorListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Instructor.objects.filter(department=self.dept)

    def get_context_data(self, **kwargs):
        context = super(InstructorListView, self).get_context_data(**kwargs)
        context['department'] = self.dept
        return context


class InstructorDetailView(DetailView):
    context_object_name = 'instructor'
    template_name = 'courses/instructor_detail.html'
    instructor = None

    def get_object(self, queryset=None):
        self.instructor = get_object_or_404(Instructor,
                                            pk=self.kwargs['inst_pk'])
        return self.instructor

    def get_context_data(self, **kwargs):
        context = super(InstructorDetailView, self).get_context_data(**kwargs)

        # Get all exams for the instructor
        context['exams'] = Exam.objects.get_approved().filter(
            course_instance__instructors=self.instructor).select_related(
            'course_instance__term',
            'course_instance__course__department').prefetch_related(
            'course_instance__instructors').order_by('course_instance__term',
                                                     'exam_number', 'exam_type')
        unpaired = context['exams']
        context['paired_exams'] = group_exams(unpaired)

        # Get all syllabi for the instructor
        context['syllabi'] = Syllabus.objects.get_approved().filter(
            course_instance__instructors=self.instructor).select_related(
            'course_instance__term',
            'course_instance__course__department').prefetch_related(
            'course_instance__instructors')

        return context


class InstructorEditView(UpdateView):
    context_object_name = 'instructor'
    form_class = InstructorEditForm
    model = Instructor
    pk_url_kwarg = 'inst_pk'
    template_name = 'courses/edit_instructor.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('courses.change_instructor', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(InstructorEditView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Changes saved!')
        return super(InstructorEditView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct your input fields.')
        return super(InstructorEditView, self).form_invalid(form)


class InstructorDeleteView(DeleteView):
    context_object_name = 'instructor'
    model = Instructor
    pk_url_kwarg = 'inst_pk'
    template_name = 'courses/delete_instructor.html'
    dept_slug = None

    @method_decorator(login_required)
    @method_decorator(
        permission_required('courses.delete_instructor', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        self.dept_slug = self.get_object().department.slug
        return super(InstructorDeleteView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Instructor deleted!')
        return super(InstructorDeleteView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'courses:instructor-list', kwargs={'dept_slug': self.dept_slug})
