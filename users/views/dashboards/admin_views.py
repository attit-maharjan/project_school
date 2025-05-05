from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# =====================================================
# 🛠️ ADMIN DASHBOARD VIEW
#     - Displays the admin panel for school system managers
#     - Accessible only to logged-in users with the 'admin' role
# =====================================================
@login_required
def admin_dashboard(request):
    # You can pass in admin-specific context here in the future
    return render(request, 'dashboards/admin/admin_dashboard.html')
