# ====================================================================================
# 🌐 USERS APP URL CONFIGURATION
# ====================================================================================
# This module defines all URL routes related to the `users` app:
# - Authentication (login/logout)
# - Role-based dashboard redirects
# - Individual dashboards per role (admin, student, teacher sub-roles, etc.)
#
# NOTE:
#   - These views are imported from modularized view files inside `users/views/`
#   - This file uses a flat, centralized structure for clarity and simplicity
# ====================================================================================

from django.urls import path

# --------------------------------------------------------
# Import grouped views for clean modular access
# --------------------------------------------------------
from users.views import (
    auth_views, 
    dashboard_redirects,
    profile_views
)
from users.views.dashboards import (
    admin_views,
    principal_views,
    vice_principal_views,
    hod_views,
    classroom_teacher_views,
    subject_teacher_views,
    student_views,
    parent_views,
    fallback_views,
)



# Namespace for reversing URLs like 'users:login'
app_name = 'users'

# --------------------------------------------------------
# Define URL patterns
# --------------------------------------------------------
urlpatterns = [

    # ===============================
    # 🔐 Authentication
    # ===============================
    path('login/', auth_views.custom_login, name='login'),           # Custom email-based login
    path('logout/', auth_views.custom_logout, name='logout'),        # POST-only logout view

    # ===============================
    # 🚦 Dashboard Redirection Logic
    # ===============================
    path('dashboard/', dashboard_redirects.role_dashboard_redirect_view, name='role_dashboard'),     # Detects role and redirects
    path('fallback-dashboard/', fallback_views.fallback_dashboard, name='fallback_dashboard'),       # For unconfigured roles

    # ===============================
    # 🧑‍💼 Admin Dashboard
    # ===============================
    path('dashboard/admin/', admin_views.admin_dashboard, name='admin_dashboard'),

    # ===============================
    # 🎓 Student Dashboard
    # ===============================
    path('dashboard/student/', student_views.student_dashboard, name='student_dashboard'),
    path('dashboard/student/subjects/', student_views.student_subjects_view, name='student_subjects'),
    path('dashboard/student/exams/', student_views.student_exam_schedule_view, name='student_exam_schedule'), 
    path("results/summary/", student_views.exam_summary_view, name="student_exam_summary"),         # 📄 Table: Subject, Score, Grade
    path("results/performance/", student_views.exam_performance_view, name="student_exam_performance"),  # 📊 Charts: Score vs Avg, Trend Line
    path("results/insights/", student_views.exam_insights_view, name="student_exam_insights"),           # 📈 Grade Insight Bars
    path("results/report-card/", student_views.exam_report_card_view, name="student_exam_report_card"),  # 🧾 Printable Report Card
    path("results/comments/", student_views.exam_comments_view, name="student_exam_comments"),           # 💬 Smart Subject Comments
    path("student/report-card/pdf/", student_views.exam_report_card_pdf_view, name="exam_report_card_pdf"),




    # ===============================
    # 👨‍👩‍👧 Parent Dashboard
    # ===============================
    path('dashboard/parent/', parent_views.parent_dashboard, name='parent_dashboard'),

    # ===============================
    # 🧑‍🏫 Teacher Dashboards (Sub-Roles)
    # ===============================
    path('dashboard/principal/', principal_views.principal_dashboard, name='principal_dashboard'),
    path('dashboard/vice-principal/', vice_principal_views.vice_principal_dashboard, name='vice_principal_dashboard'),
    path('dashboard/hod/', hod_views.hod_dashboard, name='hod_dashboard'),
    path('dashboard/classroom-teacher/', classroom_teacher_views.classroom_teacher_dashboard, name='classroom_teacher_dashboard'),
    path('dashboard/subject-teacher/', subject_teacher_views.subject_teacher_dashboard, name='subject_teacher_dashboard'),
    
    
    # ===============================
    # 👤 Profile Views
    # ===============================
    path('profile/', profile_views.view_profile, name='view_profile'),  # View profile page
    path('profile/edit/', profile_views.edit_profile, name='edit_profile'),  # Edit profile page
    # URL pattern for changing the user's password
    path('password/change/', profile_views.CustomPasswordChangeView.as_view(), name='change_password'),

]