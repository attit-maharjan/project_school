from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# =====================================================
# 📚 SUBJECT TEACHER DASHBOARD VIEW
#     - Targeted for subject-specific teaching staff
#     - Could handle mark entry, lesson plans, and performance analytics
# =====================================================
@login_required
def subject_teacher_dashboard(request):
    # Add subject-teacher-specific context here (e.g., classes taught, markbook, subject schedule)
    return render(request, 'dashboards/subject_teacher/subject_teacher_dashboard.html')
