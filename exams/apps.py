# ==========================================================
# ⚙️ Exams App Configuration
# ==========================================================
# This module defines the app configuration for the Exams app.
# It ensures Django recognizes this app and initializes it
# with any required startup logic.
# ==========================================================

from django.apps import AppConfig

# 🧩 AppConfig: Exams
class ExamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exams'

    # 🚦 Startup Hook
    def ready(self):
        # Register signal handlers when the app is ready
        import exams.signals
