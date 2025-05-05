# *************************************************************
# shared app > views.py
# *************************************************************

# Import the render shortcut to easily return HTML responses
from django.shortcuts import render

# =============================================================
#                    PUBLIC-FACING VIEWS
# =============================================================

# -------------------------------------------------------------
# Homepage view — Displays intro using SchoolSettings context
# -------------------------------------------------------------
def index(request):
    return render(request, "shared/index.html")

# -------------------------------------------------------------
# About Us view — Uses structured content from SchoolSettings
# -------------------------------------------------------------
def about(request):
    return render(request, "shared/about.html")

# -------------------------------------------------------------
# Privacy Policy view — Plain text from SchoolSettings
# -------------------------------------------------------------
def privacy_policy(request):
    return render(request, "shared/privacy_policy.html")

# -------------------------------------------------------------
# Terms of Service view — Plain text from SchoolSettings
# -------------------------------------------------------------
def terms_of_service(request):
    return render(request, "shared/terms_of_service.html")

# -------------------------------------------------------------
# Accreditations view — Will list active Accreditor objects
# -------------------------------------------------------------
def accreditations(request):
    return render(request, "shared/accreditations.html")

# -------------------------------------------------------------
# Contact view — Displays contact fields and optional form
# -------------------------------------------------------------
def contact(request):
    return render(request, "shared/contact.html")
