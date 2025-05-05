from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# =====================================================
# 🧑‍🏫 HEAD OF DEPARTMENT (HOD) DASHBOARD VIEW
#     - Accessible to authenticated users with teacher role + HOD subrole
#     - Central hub for managing department-specific operations
# =====================================================
@login_required
def hod_dashboard(request):
    # Add HOD-specific context here (e.g., department performance, subject assignments, teacher evaluations)
    return render(request, 'dashboards/hod_teacher/hod_teacher_dashboard.html')
