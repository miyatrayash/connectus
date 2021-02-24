from django.db import models
# Create your models here.
# class StudentListView(generic.ListView):
#     model = Student

class Student(models.Model):
    student_name = models.CharField(max_length=100)
    student_dob = models.DateTimeField('date published')