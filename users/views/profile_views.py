# =====================================================
#  users/views/profile_views.py
# =====================================================
#  Purpose:
#  - Handle user profile editing and viewing
#  - Fetch user information and allow updates after validation
#  - Adhere to Django best practices and ensure security with login_required
# =====================================================

# ============================
#  IMPORTS
# ============================
from django.contrib.auth.decorators import login_required  # Ensures only authenticated users can access these views
from django.shortcuts import render, redirect  # To render templates and redirect users
from users.forms import UserUpdateForm  # Importing the form for user profile updates


from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
# =====================================================
#  Edit Profile View 🛠
# =====================================================
@login_required  # Only logged-in users can access this view
def edit_profile(request):
    """
    Allow logged-in users to edit their profile information.
    This view handles both the form display (GET request) and form submission (POST request).
    """

    # Fetch the currently logged-in user from the request object
    user = request.user

    # Handle POST request (when the form is submitted)
    if request.method == 'POST':
        # Bind the form with the POST data and FILES (for image uploads, if any)
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        
        # Check if the form data is valid
        if form.is_valid():
            form.save()  # Save the updated user data
            return redirect('users:view_profile')  # Redirect to the 'view_profile' page after saving the data
    
    else:
        # Handle GET request (when the page is loaded for the first time or after an error)
        # Pre-fill the form with the current user's data
        form = UserUpdateForm(instance=user)

    # Render the 'edit_profile.html' template, passing the form to the template
    return render(request, 'users/accounts/edit_profile.html', {'form': form})


# =====================================================
#  View Profile View 🧐
# =====================================================
@login_required  # Only logged-in users can access this view
def view_profile(request):
    """
    View the profile of the currently logged-in user.
    Displays user information like username, email, and any other profile data.
    """

    # Fetch the currently logged-in user
    user = request.user  # No need to explicitly use get_user_model(), as request.user is already the user model instance

    # Pass the user object to the template to render user information
    return render(request, 'users/accounts/view_profile.html', {'user': user})


# =====================================================
#  Password Change View 🔒
# =====================================================
class CustomPasswordChangeView(PasswordChangeView):
    """
    Allows users to change their password.
    Inherits from Django's built-in PasswordChangeView.
    """
    template_name = 'users/accounts/change_password.html'  # Custom template
    success_url = reverse_lazy('users:view_profile')  # Redirect to profile after success
