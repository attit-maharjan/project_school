from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# =====================================================
# 🚧 FALLBACK DASHBOARD VIEW
#     - Shown when no valid dashboard is available for the user
#     - Typically means their role or sub-role isn’t properly configured
# =====================================================
@login_required
def fallback_dashboard(request):
    # Optional: add context like contact info for support
    return render(request, 'dashboards/fallback_dashboard.html')
