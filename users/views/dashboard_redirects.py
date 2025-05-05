from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


# =====================================================
# 🧭 HELPER FUNCTION: Determine the correct dashboard
#     - Based on the authenticated user's role
#     - Used immediately after login to redirect appropriately
# =====================================================
def get_dashboard_redirect(user):
    if user.role == 'admin':
        return reverse('users:admin_dashboard')

    elif user.role == 'teacher':
        if hasattr(user, 'teacher'):
            role_map = {
                'Principal': 'users:principal_dashboard',
                'Vice Principal': 'users:vice_principal_dashboard',
                'HOD': 'users:hod_dashboard',
                'Classroom Teacher': 'users:classroom_teacher_dashboard',
                'Subject Teacher': 'users:subject_teacher_dashboard',
            }
            return reverse(role_map.get(user.teacher.teacher_role, 'users:fallback_dashboard'))

        # Teacher has no associated Teacher profile or role
        return reverse('users:fallback_dashboard')

    elif user.role == 'student':
        return reverse('users:student_dashboard')

    elif user.role == 'parent':
        return reverse('users:parent_dashboard')

    # Role not recognized or user is misconfigured
    return reverse('users:fallback_dashboard')


# =====================================================
# 🚦 DASHBOARD REDIRECT VIEW
#     - Called after login
#     - Uses helper to redirect user to their dashboard
# =====================================================
@login_required
def role_dashboard_redirect_view(request):
    user = request.user
    redirect_url = get_dashboard_redirect(user)

    if redirect_url:
        return redirect(redirect_url)

    # If no valid dashboard is found (e.g., unconfigured teacher)
    messages.warning(
        request,
        "Your account is not fully configured. Please contact the school admin."
    )
    return redirect('users:fallback_dashboard')
