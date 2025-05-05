from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# =====================================================
# 🎓 PRINCIPAL DASHBOARD VIEW
#     - Renders the principal's main dashboard
#     - Protected: only accessible to authenticated users
# =====================================================
@login_required
def principal_dashboard(request):
    # Add principal-specific context here (e.g., school-wide metrics, reports)
    return render(request, 'dashboards/principal/principal_dashboard.html')
