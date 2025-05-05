# =====================================================
# 🌐 PROJECT-WIDE URL CONFIGURATION (BIVGS)
# =====================================================
# This file defines how URLs are routed to different apps
# across the Django project: admin panel, user auth system,
# public site, and media files in development.
# =====================================================

from django.contrib import admin                         # Django's admin interface
from django.urls import path, include                    # Routing functions
from django.conf import settings                         # Project settings
from django.conf.urls.static import static               # Serve media files during development

urlpatterns = [
    # -------------------------
    # 🛠 Django Admin Interface
    # -------------------------
    path("admin/", admin.site.urls),

    # -------------------------
    # 🔐 User Authentication & Dashboards
    # -------------------------
    # Includes login, logout, and role-based dashboards
    path("users/", include("users.urls")),

    # -------------------------
    # 🏫 Public Website (Landing Pages)
    # -------------------------
    # Includes pages accessible to all users (home, about, contact, etc.)
    path("", include("the_school.urls", namespace="the_school")),
]

# -------------------------
# 🎨 Media Files (Only in Development)
# -------------------------
# Allows uploaded media (e.g., profile photos) to be served in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
