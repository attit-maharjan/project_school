# =====================================================
#  users/forms.py
# =====================================================
#  Purpose:
#  - Handle custom authentication using Email
#  - Handle user profile update (edit profile form)
# =====================================================

# ============================
#  IMPORTS
# ============================
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from PIL import Image  # For image validation
# Import the imghdr module to identify image file types (e.g., jpeg, png, gif) based on file headers
import imghdr


# ============================
#  USER MODEL
# ============================
User = get_user_model()

# =====================================================
#  Email-Based Authentication Form 📧
# =====================================================
class EmailAuthenticationForm(AuthenticationForm):
    """Custom authentication using email and password."""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email",
            "autofocus": True
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your password"
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(),
        label="Remember Me"
    )

    def confirm_login_allowed(self, user):
        """Ensure only active users can log in."""
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.", code='inactive')

# =====================================================
#  User Profile Update Form 🛠
# =====================================================
class UserUpdateForm(forms.ModelForm):
    """Form for users to update their profile information."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'initials', 'dob', 'gender',
            'phone_number', 'profile_image',
            'street_address', 'city', 'state_province', 'postal_code', 'country'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),  # Use HTML5 date picker
        }

    def clean_profile_image(self):
        """Validate the profile image size and dimensions."""
        image = self.cleaned_data.get('profile_image')

        if image:
            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024  # 5 MB
            if image.size > max_size:
                raise ValidationError("The image file size exceeds the maximum limit of 5 MB.")
            
            # Check file type (only JPEG, PNG, and WebP)
            img_type = imghdr.what(image)
            if img_type not in ['jpeg', 'png', 'webp']:
                raise ValidationError("Only JPG, PNG, and WebP images are allowed.")
            
            # Check image dimensions (min 100x100px and max 1500x1500px)
            img = Image.open(image)
            width, height = img.size

            if width < 100 or height < 100:
                raise ValidationError("The image must be at least 100x100 pixels.")
            if width > 1500 or height > 1500:
                raise ValidationError("The image cannot be larger than 1500x1500 pixels.")

        return image
