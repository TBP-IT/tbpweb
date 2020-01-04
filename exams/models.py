import datetime
from django.db import models
from tbpweb.settings.models import MAX_STRLEN

def this_year():
    return datetime.date.today().year

class Subject(models.Model):
    name = models.CharField(max_length=MAX_STRLEN)

class Course(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    number = models.CharField(max_length=MAX_STRLEN)
    name = models.CharField(max_length=MAX_STRLEN, blank=True)

    def __str__(self):
        return "{0} {1}: {2}".format(self.subject, self.number, self.name)

    def shorthand(self):
        return "{0} {1}".format(self.subject, self.number)

class Instructor(models.Model):
    first_name = models.CharField(max_length=MAX_STRLEN)
    last_name = models.CharField(max_length=MAX_STRLEN)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return "{0}, {1}".format(self.last_name, self.first_name)

class Semester(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sem = models.CharField(max_length=MAX_STRLEN, choices=[('Fa', 'Fall'), ('Sp', 'Spring'), ('Su', 'Summer')])
    year = models.IntegerField(
        validators=[MinValueValidator(1970), MaxValueValidator(this_year())],
        default=this_year(),
    )
    instructors = models.ManyToManyField(Instructor)
    syllabus = models.FileField(blank=True)
    midterm1 = models.FileField(blank=True)
    midterm1_sol = models.FileField(blank=True)
    midterm2 = models.FileField(blank=True)
    midterm2_sol = models.FileField(blank=True)
    midterm3 = models.FileField(blank=True)
    midterm3_sol = models.FileField(blank=True)
    final = models.FileField(blank=True)
    final_sol = models.FileField(blank=True)
