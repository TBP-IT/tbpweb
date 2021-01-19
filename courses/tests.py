from django.contrib.auth import get_user_model
from django.test import TestCase

from quark.base.models import Term
from quark.courses.models import Course
from quark.courses.models import CourseInstance
from quark.courses.models import Department
from quark.courses.models import Instructor
from quark.exams.models import Exam
from quark.syllabi.models import Syllabus


def make_test_department():
    test_department = Department(
        long_name='Test Department 1',
        short_name='Tst Dep 1',
        abbreviation='TEST DEPT 1')
    test_department.save()
    return test_department


class CoursesTestCase(TestCase):
    def setUp(self):
        self.dept_cs = Department(
            long_name='Computer Science',
            short_name='CS',
            abbreviation='COMPSCI')
        self.dept_cs.save()
        self.dept_ee = Department(
            long_name='Electrical Engineering',
            short_name='EE',
            abbreviation='EL ENG')
        self.dept_ee.save()
        self.course_cs_1 = Course(department=self.dept_cs, number='1')
        self.course_cs_1.save()
        self.course_ee_1 = Course(department=self.dept_ee, number='1')
        self.course_ee_1.save()
        self.instructor_cs = Instructor(first_name='Tau', last_name='Bate',
                                        department=self.dept_cs)
        self.instructor_cs.save()
        self.instructor_ee = Instructor(first_name='Pi', last_name='Bent',
                                        department=self.dept_ee)
        self.instructor_ee.save()
        self.instructor_ee_2 = Instructor(first_name='Bau', last_name='Tate',
                                          department=self.dept_ee)
        self.instructor_ee_2.save()
        self.term = Term(term='sp', year=2013, current=True)
        self.term.save()
        self.term2 = Term(term='sp', year=2014, current=False)
        self.term2.save()
        self.course_instance_cs_1 = CourseInstance(
            term=self.term,
            course=self.course_cs_1)
        self.course_instance_cs_1.save()
        self.course_instance_cs_1.instructors.add(self.instructor_cs)
        self.course_instance_cs_1.save()
        self.course_instance_ee_1 = CourseInstance(
            term=self.term,
            course=self.course_ee_1)
        self.course_instance_ee_1.save()
        self.course_instance_ee_1.instructors.add(self.instructor_ee)
        self.course_instance_ee_1.save()
        self.course_instance_ee_2 = CourseInstance(
            term=self.term2,
            course=self.course_ee_1)
        self.course_instance_ee_2.save()
        self.course_instance_ee_2.instructors.add(self.instructor_ee)
        self.course_instance_ee_2.save()
        self.course_instance_ee_3 = CourseInstance(
            term=self.term2,
            course=self.course_ee_1)
        self.course_instance_ee_3.save()
        self.course_instance_ee_3.instructors.add(self.instructor_ee_2)
        self.course_instance_ee_3.save()
        self.user = get_user_model().objects.create_user(
            username='tbpUser',
            email='tbp.berkeley.edu',
            password='testpassword',
            first_name='tbp',
            last_name='user')
        self.user.save()
        self.syllabus_cs_1 = Syllabus(
            course_instance=self.course_instance_cs_1,
            submitter=self.user,
            file_ext='.pdf',
            verified=True)
        self.syllabus_cs_1.save()
        # Create exams:
        # ee_1: Course ee1, instr 1 final exam
        # ee_2: Course ee1, instr 1 final solution
        # ee_3: Course ee1, instr 1 final exam
        # ee_4: Course ee1, instr 2 final exam
        self.exam_ee_1 = Exam(
            course_instance=self.course_instance_ee_1,
            submitter=self.user,
            exam_number=Exam.FINAL,
            exam_type=Exam.EXAM,
            file_ext='.pdf',
            verified=True)
        self.exam_ee_1.save()
        self.exam_ee_2 = Exam(
            course_instance=self.course_instance_ee_1,
            submitter=self.user,
            exam_number=Exam.FINAL,
            exam_type=Exam.SOLN,
            file_ext='.pdf',
            verified=True)
        self.exam_ee_2.save()
        self.exam_ee_3 = Exam(
            course_instance=self.course_instance_ee_2,
            submitter=self.user,
            exam_number=Exam.FINAL,
            exam_type=Exam.EXAM,
            file_ext='.pdf',
            verified=True)
        self.exam_ee_3.save()
        self.exam_ee_4 = Exam(
            course_instance=self.course_instance_ee_3,
            submitter=self.user,
            exam_number=Exam.FINAL,
            exam_type=Exam.EXAM,
            file_ext='.pdf',
            verified=True)
        self.exam_ee_4.save()


class DepartmentTest(TestCase):
    def test_save(self):
        test_department = Department(
            long_name='Test Department 2',
            short_name='Tst Dep 2',
            abbreviation='test dept 2')
        self.assertFalse(test_department.slug)
        test_department.save()
        self.assertEquals(test_department.abbreviation, 'TEST DEPT 2')
        self.assertEquals(test_department.slug, 'tst-dep-2')
        test_department.short_name = 'Tst Dep 2 New'
        self.assertEquals(test_department.slug, 'tst-dep-2')
        test_department.save()
        self.assertEquals(test_department.slug, 'tst-dep-2-new')
        test_department.full_clean()


class CourseTest(TestCase):
    def setUp(self):
        self.test_department = make_test_department()
        self.test_department_2 = Department(
            long_name='Test Department 2',
            short_name='Tst Dep 2',
            abbreviation='TEST DEPT 2')
        self.test_department_2.save()
        self.test_course_1 = Course(
            department=self.test_department,
            number='61a',
            title='TestDept1 61a')
        self.test_course_1.save()
        self.test_course_2 = Course(
            department=self.test_department,
            number='h61a',
            title='Honors TestDept1 61a')
        self.test_course_2.save()
        self.test_course_3 = Course(
            department=self.test_department,
            number='61b',
            title='TestDept1 61b')
        self.test_course_3.save()
        self.test_course_4 = Course(
            department=self.test_department,
            number='70',
            title='TestDept1 70')
        self.test_course_4.save()
        self.test_course_5 = Course(
            department=self.test_department_2,
            number='C30',
            title='TestDept2 C30')
        self.test_course_5.save()
        self.test_course_6 = Course(
            department=self.test_department_2,
            number='70',
            title='TestDept2 70')
        self.test_course_6.save()
        self.test_course_7 = Course(
            department=self.test_department_2,
            number='130AC',
            title='TestDept2 130AC')
        self.test_course_7.save()
        self.test_course_8 = Course(
            department=self.test_department_2,
            number='C130AC',
            title='TestDept2 C130AC')
        self.test_course_8.save()
        self.test_course_9 = Course(
            department=self.test_department_2,
            number='H130AC',
            title='TestDept2 Honors 130AC')
        self.test_course_9.save()
        self.dept1_70_hyphen_24 = Course(
            department=self.test_department,
            number='70-24')
        self.dept1_70_hyphen_25 = Course(
            department=self.test_department,
            number='70-25')
        self.dept2_70_hyphen_25 = Course(
            department=self.test_department_2,
            number='70-25')
        self.dept1_71 = Course(
            department=self.test_department,
            number='71')

    def tearDown(self):
        self.test_department.full_clean()

    def test_save(self):
        self.assertEquals(self.test_course_2.number, 'H61A')

    def test_abbreviation(self):
        self.assertEquals(self.test_course_2.abbreviation(), 'Tst Dep 1 H61A')

    def test_get_display_name(self):
        self.assertEquals(self.test_course_2.get_display_name(),
                          'Test Department 1 H61A')

    def test_lessthan(self):
        self.assertFalse(self.test_course_1 < self.test_course_1)
        self.assertTrue(self.test_course_1 < self.test_course_2)
        self.assertTrue(self.test_course_1 < self.test_course_3)
        self.assertTrue(self.test_course_1 < self.test_course_4)
        self.assertTrue(self.test_course_1 < self.test_course_5)
        self.assertTrue(self.test_course_1 < self.test_course_6)
        self.assertTrue(self.test_course_2 < self.test_course_3)
        self.assertTrue(self.test_course_2 < self.test_course_4)
        self.assertTrue(self.test_course_4 < self.test_course_5)
        self.assertTrue(self.test_course_4 < self.test_course_6)
        self.assertTrue(self.test_course_4 < self.test_course_7)
        self.assertTrue(self.test_course_4 < self.test_course_8)
        self.assertTrue(self.test_course_7 < self.test_course_8)
        self.assertTrue(self.test_course_7 < self.test_course_9)
        self.assertTrue(self.test_course_8 < self.test_course_9)
        self.assertFalse(self.test_course_1 < self.test_department)
        # Hypenated course tests
        self.assertTrue(self.dept1_70_hyphen_24 < self.dept1_70_hyphen_25)
        self.assertFalse(self.dept1_70_hyphen_24 < self.dept1_70_hyphen_24)
        self.assertFalse(self.dept1_70_hyphen_25 < self.dept1_70_hyphen_24)
        self.assertTrue(self.dept1_70_hyphen_24 < self.dept1_71)
        self.assertTrue(self.test_course_4 < self.dept1_70_hyphen_24)
        self.assertTrue(self.dept1_70_hyphen_25 < self.dept2_70_hyphen_25)

    def test_equals(self):
        self.assertTrue(self.test_course_1 == self.test_course_1)
        self.assertFalse(self.test_course_4 == self.test_course_6)
        self.assertFalse(self.test_course_7 == self.test_course_8)
        self.assertFalse(self.test_course_8 == self.test_course_9)
        self.assertFalse(self.test_course_1 == self.test_department)

    def test_other_comparison_methods(self):
        self.assertTrue(self.test_course_2 <= self.test_course_2)
        self.assertTrue(self.test_course_2 <= self.test_course_3)
        self.assertTrue(self.test_course_2 != self.test_course_3)
        self.assertTrue(self.test_course_4 > self.test_course_1)
        self.assertTrue(self.test_course_4 >= self.test_course_4)
        self.assertTrue(self.test_course_4 >= self.test_course_3)
        self.assertFalse(self.test_course_1 <= self.test_department)
        self.assertFalse(self.test_course_1 > self.test_department)
        self.assertFalse(self.test_course_1 >= self.test_department)
        self.assertTrue(self.test_course_1 != self.test_department)

    def test_sort(self):
        sorted_list = [self.test_course_1, self.test_course_2,
                       self.test_course_3, self.test_course_4,
                       self.test_course_5, self.test_course_6,
                       self.test_course_7, self.test_course_8,
                       self.test_course_9]
        test_list = [self.test_course_1, self.test_course_3,
                     self.test_course_5, self.test_course_7,
                     self.test_course_9, self.test_course_4,
                     self.test_course_6, self.test_course_8,
                     self.test_course_2]
        self.assertNotEqual(test_list, sorted_list)
        test_list.sort()
        # Correct ordering:
        # TD1 61A, TD1 H61A, TD1 61B, TD1 70, TD2 C30,
        # TD2 70, TD2 130AC, TD2 C130AC, TD2 H130AC
        self.assertEquals(test_list, sorted_list)


class InstructorTest(TestCase):
    def setUp(self):
        self.test_department = make_test_department()
        self.test_instructor = Instructor(
            first_name='Tau',
            last_name='Betapi',
            department=self.test_department)
        self.test_instructor.save()

    def tearDown(self):
        self.test_department.full_clean()

    def test_full_name(self):
        self.assertEquals(self.test_instructor.full_name(), 'Tau Betapi')


class DepartmentListViewTest(CoursesTestCase):
    def test_response(self):
        resp = self.client.get('/courses/')
        # A successful HTTP GET request has status code 200
        self.assertEqual(resp.status_code, 200)

    def test_dept_filter(self):
        resp = self.client.get('/courses/')
        self.assertEqual(resp.context['departments'].count(), 2)
        self.exam_ee_1.verified = False
        self.exam_ee_1.save()
        self.exam_ee_2.verified = False
        self.exam_ee_2.save()
        self.exam_ee_3.verified = False
        self.exam_ee_3.save()
        self.exam_ee_4.verified = False
        self.exam_ee_4.save()
        self.syllabus_cs_1.verified = False
        self.syllabus_cs_1.save()
        resp = self.client.get('/courses/')
        # Filters out departments that don't have exams/syllabi
        self.assertEqual(resp.context['departments'].count(), 0)


class CourseListViewTest(CoursesTestCase):
    def test_response(self):
        resp = self.client.get('/courses/Cs/')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/courses/bad-dept/')
        self.assertEqual(resp.status_code, 404)

    def test_course_filter(self):
        resp = self.client.get('/courses/cs/')
        self.assertEqual(len(resp.context['courses']), 1)
        resp = self.client.get('/courses/ee/')
        self.assertEqual(len(resp.context['courses']), 1)
        self.syllabus_cs_1.verified = False
        self.syllabus_cs_1.save()
        self.exam_ee_1.verified = False
        self.exam_ee_1.save()
        self.exam_ee_2.verified = False
        self.exam_ee_2.save()
        self.exam_ee_3.verified = False
        self.exam_ee_3.save()
        self.exam_ee_4.verified = False
        self.exam_ee_4.save()
        # Filters out courses that don't have exams/syllabi
        resp = self.client.get('/courses/cs/')
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get('/courses/ee/')
        self.assertEqual(resp.status_code, 404)


class CourseDetailViewTest(CoursesTestCase):
    def test_response(self):
        resp = self.client.get('/courses/cs/1/')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/courses/bad-dept/1/')
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get('/courses/cs/9999/')
        self.assertEqual(resp.status_code, 404)

    def test_course_details(self):
        resp = self.client.get('/courses/cs/1/')
        self.assertEqual(resp.context['course'].pk,
                         self.course_cs_1.pk)
        self.assertEqual(resp.context['exams'].count(), 0)
        self.assertEqual(resp.context['syllabi'].count(), 1)

    def test_exam_pairing(self):
        resp = self.client.get('/courses/ee/1/')

        # Compare the pairs.
        pairs = [list(p[0:2]) for p in resp.context['paired_exams']]
        self.assertItemsEqual(pairs, [[self.exam_ee_1, self.exam_ee_2],
                                      [self.exam_ee_3, None],
                                      [self.exam_ee_4, None]])
        for exam_pair in resp.context['paired_exams']:
            self.assertIsNotNone(exam_pair[2])
        # pair_0 = resp.context['paired_exams'][0]
        # self.assertEqual(pair_0[0:2], [self.exam_ee_3, None])
        # self.assertIsNotNone(pair_0[2])

        # pair_1 = resp.context['paired_exams'][1]
        # self.assertEqual(pair_1[0:2], [self.exam_ee_1, self.exam_ee_2])
        # self.assertIsNotNone(pair_1[2])

        # pair_2 = resp.context['paired_exams'][2]
        # self.assertEqual(pair_2[0:2], [self.exam_ee_4, None])
        # self.assertIsNotNone(pair_2[2])


class InstructorDetailViewTest(CoursesTestCase):
    def test_response(self):
        resp = self.client.get('/courses/instructors/99999999/')
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(
            '/courses/instructors/%d/' % (self.instructor_cs.pk))
        self.assertEqual(resp.status_code, 200)
