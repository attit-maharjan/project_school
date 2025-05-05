from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# =====================================================
# 👨‍👩‍👧 PARENT DASHBOARD VIEW
#     - Accessible to authenticated users with the 'parent' role
#     - Provides insights into their child's academic performance and activity
# =====================================================
@login_required
def parent_dashboard(request):
    # Add parent-specific context here (e.g., child's grades, attendance, teacher feedback)
    return render(request, 'dashboards/parent/parent_dashboard.html')
