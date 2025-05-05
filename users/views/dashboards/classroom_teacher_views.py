from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# =====================================================
# 👩‍🏫 CLASSROOM TEACHER DASHBOARD VIEW
#     - Designed for homeroom or class teachers
#     - Could include student attendance, class announcements, and behavior logs
# =====================================================
@login_required
def classroom_teacher_dashboard(request):
    # Add classroom-teacher-specific context here (e.g., student lists, attendance, class schedule)
    return render(request, 'dashboards/classroom_teacher/classroom_teacher_dashboard.html')
