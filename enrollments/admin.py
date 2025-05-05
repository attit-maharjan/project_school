# ===============================================
# ⚙️ # enrollments/admin.py
# ===============================================
from django.contrib import admin
from .models import (
    StudentEnrollmentType, ClassGroupStudentEnrollment, TeacherDepartmentEnrollment, 
    TeacherSubjectAssignment, ClassGroupTeacherAssignment, 
    ClassGroupSubjectAssignment
)


# -------------------------------
# 🛠️ StudentEnrollmentType Admin
# -------------------------------
@admin.register(StudentEnrollmentType)
class StudentEnrollmentTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the StudentEnrollmentType model.
    Provides search, filtering, and display features for easy management.
    """

    # 🔍 Searchable fields
    search_fields = ['code', 'name', 'description']

    # 🧾 Fields to display in list view
    list_display = ['code', 'name', 'description']

    # 🪄 Field layout in form view
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description'),
            'description': 'Define how and why a student was enrolled in a given academic year.'
        }),
    )




# -------------------------------
# ⚙️ Admin: ClassGroupStudentEnrollment
# -------------------------------
@admin.register(ClassGroupStudentEnrollment)
class ClassGroupStudentEnrollmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for class group student enrollments.
    Allows filtering, searching, and clean presentation for staff.
    """

    # -------------------------------------------
    # 🧩 Fields to Display in List View
    # -------------------------------------------
    list_display = (
        "student",
        "class_group",
        "enrollment_type",
        "enrollment_date",
        "is_active",
        "created_at",
    )
    list_filter = (
        "class_group",
        "enrollment_type",
        "is_active",
        "enrollment_date",
        "created_at",
    )
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__student_id",
        "class_group__name",
        "enrollment_type__name",
    )
    autocomplete_fields = ("student", "class_group", "enrollment_type")

    # -------------------------------------------
    # 📝 Field Groupings in Form
    # -------------------------------------------
    fieldsets = (
        ("📚 Enrollment Details", {
            "fields": (
                "student",
                "class_group",
                "enrollment_type",
                "enrollment_date",
                "is_active",
            )
        }),
        ("🗒 Optional Notes", {
            "fields": ("notes",),
            "classes": ("collapse",),
        }),
        ("🕓 Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # -------------------------------------------
    # 🔒 Read-Only Fields
    # -------------------------------------------
    readonly_fields = ("created_at", "updated_at")

# ==========================================================
# 🧑‍🏫 Admin: Teacher Department Enrollment
# ==========================================================
# Customizes the Django admin interface for managing which 
# teachers are assigned to which departments, optionally per 
# academic year. Improves usability with filters, searches, 
# and custom display formatting.
# ==========================================================


# -----------------------------------------
# 🛠️ Admin Config: TeacherDepartmentEnrollment
# -----------------------------------------
@admin.register(TeacherDepartmentEnrollment)
class TeacherDepartmentEnrollmentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing teacher-department assignments.
    """

    # 📊 Columns to display in list view
    list_display = (
        'teacher_display', 
        'department', 
        'academic_year', 
        'is_active', 
        'date_assigned'
    )

    # 🔍 Sidebar filters
    list_filter = (
        'department', 
        'academic_year', 
        'is_active'
    )

    # 🔎 Fields searchable from admin
    search_fields = (
        'teacher__user__first_name',
        'teacher__user__last_name',
        'department__name',
    )

    # 📝 Fields to show in the admin form
    fields = (
        'teacher', 
        'department', 
        'academic_year', 
        'date_assigned', 
        'is_active'
    )

    # -----------------------------------------
    # 🧠 Display Full Teacher Name
    # -----------------------------------------
    @admin.display(description="Teacher")
    def teacher_display(self, obj):
        return f"{obj.teacher.user.first_name} {obj.teacher.user.last_name}"

    # -----------------------------------------
    # 🔐 Limit Delete Permissions (optional)
    # -----------------------------------------
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete entries
        return request.user.is_superuser




#============================
# 🛠️ Admin: TeacherSubjectAssignmentAdmin
#============================
# Custom admin interface for TeacherSubjectAssignment.
# Includes autocomplete, custom display fields, search, 
# filtering, and permission restrictions.
#============================

@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    """
    Admin with autocomplete fields for assigning teachers to subjects.
    """

    #============================
    # List Display Configuration
    #============================
    # Fields shown in the object list view
    list_display = (
        "teacher_display",     # Custom display for teacher name
        "subject",             # Subject assigned
        "academic_year",       # Year of assignment
        "is_active",           # Active flag
        "date_assigned",       # Date when assigned
    )

    #============================
    # Filters for Sidebar
    #============================
    list_filter = ("academic_year", "is_active", "subject")

    #============================
    # Searchable Fields
    #============================
    search_fields = (
        "teacher__user__first_name",
        "teacher__user__last_name",
        "subject__name",
    )

    #============================
    # Field Layout in Form
    #============================
    fields = (
        "teacher",
        "subject",
        "academic_year",
        "date_assigned",
        "is_active",
    )

    #============================
    # Autocomplete Configuration
    #============================
    autocomplete_fields = ("teacher", "subject", "academic_year")

    #============================
    # Custom Display Methods
    #============================

    @admin.display(description="Teacher")
    def teacher_display(self, obj):
        """
        Returns the full name of the teacher for display in list view.
        """
        return f"{obj.teacher.user.first_name} {obj.teacher.user.last_name}"

    #============================
    # Model Save Hook
    #============================

    def save_model(self, request, obj, form, change):
        """
        Clean the object before saving to enforce model validations.
        """
        obj.full_clean()
        super().save_model(request, obj, form, change)

    #============================
    # Delete Permissions
    #============================

    def has_delete_permission(self, request, obj=None):
        """
        Only superusers are allowed to delete assignments.
        """
        return request.user.is_superuser




# Admin: ClassGroupTeacherAssignmentAdmin
# ----------------------------------------------------------
# Admin interface for assigning Classroom Teachers to 
# ClassGroups. Supports filters, search, autocomplete, 
# and model validation.
# ==========================================================


#============================
# 🛠 Admin Registration
#============================

@admin.register(ClassGroupTeacherAssignment)
class ClassGroupTeacherAssignmentAdmin(admin.ModelAdmin):
    """
    Admin interface for assigning Classroom Teachers to ClassGroups,
    with autocomplete, search, filters, and validation hooks.
    """

    #============================
    # 📋 List Display Configuration
    #============================
    # Defines columns visible in the admin list view.
    list_display = (
        "teacher_display",    # Custom display for teacher
        "class_group",        # Class group name
        "academic_year",      # Year of assignment
        "is_active",          # Active status
        "date_assigned"       # Date of assignment
    )

    #============================
    # 🔍 Filters (Sidebar)
    #============================
    # Allows filtering records in the admin sidebar.
    list_filter = (
        "academic_year",
        "is_active",
        "class_group"
    )

    #============================
    # 🔎 Search Fields
    #============================
    # Enables keyword searching in the admin search bar.
    search_fields = (
        "teacher__user__first_name",
        "teacher__user__last_name",
        "teacher__user__email",
        "class_group__name"
    )

    #============================
    # 🧩 Field Layout (Form View)
    #============================
    # Controls the order and visibility of fields in the admin form.
    fields = (
        "teacher",
        "class_group",
        "academic_year",
        "date_assigned",
        "is_active"
    )

    #============================
    # ⚡ Autocomplete Fields
    #============================
    # Enables autocomplete UI for related models.
    autocomplete_fields = (
        "teacher",
        "class_group",
        "academic_year"
    )

    #============================
    # 🧠 Custom Field Display
    #============================
    # Combines first and last name for better display in list view.
    @admin.display(description="Classroom Teacher")
    def teacher_display(self, obj):
        return f"{obj.teacher.user.first_name} {obj.teacher.user.last_name}"

    #============================
    # ✅ Model Validation Hook
    #============================
    # Ensures clean() logic is respected when saving through admin.
    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

    #============================
    # 🛡 Deletion Restriction
    #============================
    # Only superusers can delete assignments.
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ========================================================
# 🛠 Admin: ClassGroupSubjectAssignment
# ========================================================
# Purpose:
# - Manages subject-to-class-group assignments via the Django admin.
# - Includes filtering, searching, autocomplete, and custom layout.
# - Prevents duplicate subject assignments and enforces clean UX.
# ========================================================



@admin.register(ClassGroupSubjectAssignment)
class ClassGroupSubjectAssignmentAdmin(admin.ModelAdmin):
    # 📋 Fields shown in list display
    list_display = (
        "class_group",       # Target class group
        "subject",           # Assigned subject
        "academic_year",     # Year of assignment
        "is_active",         # Status flag
        "date_assigned"      # Timestamp
    )

    # 🔍 Filters available in the sidebar
    list_filter = (
        "academic_year",                         # Filter by year
        "is_active",                             # Filter by status
        "subject__grade_level",                  # Filter by subject grade level
        "class_group__grade_level"               # Filter by class group grade
    )

    # 🔎 Search fields for top bar
    search_fields = (
        "class_group__name",     # e.g., "Grade 10 A"
        "subject__name",         # e.g., "Mathematics"
        "academic_year__name"    # e.g., "2024"
    )

    # 🪄 Enable autocomplete for foreign key inputs
    autocomplete_fields = (
        "class_group",
        "subject",
        "academic_year"
    )

    # 📐 Default sorting order in admin list view
    ordering = ("-date_assigned",)  # Show most recent first

    # 🧱 Custom layout for the admin form
    fieldsets = (
        (None, {
            "fields": ("class_group", "subject", "academic_year", "is_active"),
            "description": "Assign subjects to class groups by academic year. Each pair must match grade levels."
        }),
        ("Metadata", {
            "fields": ("date_assigned",),
            "classes": ("collapse",)  # Hide section unless expanded
        })
    )

    # 🚀 Optimize queries to reduce DB hits
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "class_group", "subject", "academic_year"
        )
