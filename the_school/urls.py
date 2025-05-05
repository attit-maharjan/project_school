# *************************************************************
# the_school app > urls.py
# *************************************************************

# Import the path function to define URL patterns
from django.urls import path

# Import views from the current app
from . import views

# Namespace for the app to avoid name clashes in project-wide URL naming
app_name = "the_school"

# =============================================================
#                    URL Patterns for Public Pages
# =============================================================
urlpatterns = [
    # ---------------------------------------------------------
    # Homepage
    # Responds to base URL (e.g., /) with homepage content
    # ---------------------------------------------------------
    path("", views.index, name="index"),

    # ---------------------------------------------------------
    # About Us Page
    # Introduces the school and its mission (from SchoolSettings)
    # ---------------------------------------------------------
    path("about/", views.about, name="about"),

    # ---------------------------------------------------------
    # Privacy Policy Page
    # Displays school privacy rules (from SchoolSettings)
    # ---------------------------------------------------------
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),

    # ---------------------------------------------------------
    # Terms of Service Page
    # Legal usage terms (from SchoolSettings)
    # ---------------------------------------------------------
    path("terms-of-service/", views.terms_of_service, name="terms_of_service"),

    # ---------------------------------------------------------
    # Accreditations Page
    # Displays a list of accrediting institutions
    # ---------------------------------------------------------
    path("accreditations/", views.accreditations, name="accreditations"),

    # ---------------------------------------------------------
    # Contact Page
    # Displays contact info and optional form
    # ---------------------------------------------------------
    path("contact/", views.contact, name="contact"),
]
