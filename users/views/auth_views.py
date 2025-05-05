from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.urls import reverse

from users.forms import EmailAuthenticationForm

# =====================================================
# 🔐 1. CUSTOM LOGIN VIEW (Handles form login logic)
# =====================================================
def custom_login(request):
    # If the user is already authenticated, redirect them to their role-based dashboard
    if request.user.is_authenticated:
        return redirect('users:role_dashboard')

    # Process the login form
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Session expiry control based on "Remember Me" checkbox
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Session ends when browser closes
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days

            return redirect('users:role_dashboard')

        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = EmailAuthenticationForm()

    return render(request, 'users/accounts/login.html', {'form': form})


# =====================================================
# 🚪 2. CUSTOM LOGOUT VIEW (Secure logout via POST)
# =====================================================
@require_POST
@login_required
def custom_logout(request):
    # Logs the user out and clears their session
    logout(request)

    # Flash a friendly goodbye message
    messages.success(request, "You have been logged out successfully.")

    # Redirect to login page
    return redirect('users:login')
