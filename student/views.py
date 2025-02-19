from django.shortcuts import render
from .models import Student

def student_list(request):
    students = Student.objects.all()
    return render(request, 'student.html', {'students': students})

def home(request):
    return render(request, 'home.html')