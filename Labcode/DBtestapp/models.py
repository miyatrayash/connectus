from django.db import models
class Student(models.Model):
    student_name = models.CharField(max_length=100)
    student_dob = models.DateTimeField('date published')