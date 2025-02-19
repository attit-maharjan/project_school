from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page URL
    path('students/', views.student_list, name='student_list'),  # Student list URL
]