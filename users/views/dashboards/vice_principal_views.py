from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# =====================================================
# 🧑‍💼 VICE PRINCIPAL DASHBOARD VIEW
#     - Accessible only to authenticated users
#     - Meant for users with teacher role + Vice Principal subrole
# =====================================================
@login_required
def vice_principal_dashboard(request):
    # Add VP-specific context here (e.g., discipline reports, staff attendance)
    return render(request, 'dashboards/vice_principal/vice_principal_dashboard.html')
