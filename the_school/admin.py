# the_school app > admin.py
# =====================================================
#                   IMPORT STATEMENTS
# =====================================================
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import SchoolSettings, Accreditor, Department, AcademicYear, GradeLevel, ClassGroup, Subject

# -----------------------------
# 🏛 Accreditor Admin
# -----------------------------
@admin.register(Accreditor)
class AccreditorAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_number", "accreditation_date", "status", "website_link")
    search_fields = ("name", "registration_number")
    list_filter = ("status",)
    ordering = ("-accreditation_date",)

    def website_link(self, obj):
        if obj.website:
            return format_html('<a href="{}" target="_blank">🌐 Visit</a>', obj.website)
        return "-"
    website_link.short_description = "Website"


# -----------------------------
# 🏫 School Settings Admin
# -----------------------------
@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    """Enforce Singleton, organize content nicely in admin UI."""

    def has_add_permission(self, request):
        # Prevent new entries if one already exists
        if SchoolSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    # Optional but helpful: keep list display minimal
    list_display = ("school_name", "contact_number", "email_address", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    save_on_top = True

    fieldsets = (
        ("🎓 School Core Info", {
            "fields": (
                "singleton",
                "school_name",
                "school_logo",
                "school_motto",
                "established_year"
            )
        }),
        ("📍 Contact Information", {
            "fields": (
                "address",
                "contact_number",
                "email_address",
                "website_url",
            )
        }),
        ("🌐 Social Media & Accreditation", {
            "fields": (
                "social_media_links",
                "accreditation_details",
            )
        }),
        ("🏠 Homepage Content", {
            "fields": ("homepage_intro",),
            "description": "This will show on the main homepage of the public site."
        }),
        ("📄 About Us Page Content", {
            "fields": (
                "about_us_title",
                "about_us_subheading1",
                "about_us_paragraph1",
                "about_us_paragraph2",
                "about_us_subheading2",
                "about_us_paragraph3",
            )
        }),
        ("📄 Contact Us Page Content", {
            "fields": (
                "contact_us_title",
                "contact_us_paragraph1",
                "contact_us_paragraph2",
            )
        }),
        ("📜 Legal Pages", {
            "fields": ("privacy_policy", "terms_of_service"),
        }),
        ("🕒 Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )



# =============================================
# 🛡️ Department Admin — Enterprise Ready
# =============================================




@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Department model.
    Designed for scalability, UX, and team clarity.
    """

    # 📋 List View Configurations
    list_display = (
        "code",
        "name",
        "head_display",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "head_of_department")
    search_fields = ("code", "name", "head_of_department__user__full_name")  # Customize this as per your User model
    ordering = ("code",)
    date_hierarchy = "created_at"

    # 🧠 Optimizations
    autocomplete_fields = ("head_of_department",)
    readonly_fields = ("created_at", "updated_at")

    # 🧱 Form Layout (Fieldsets)
    fieldsets = (
        ("🧾 Basic Info", {
            "fields": ("code", "name", "description", "is_active"),
        }),
        ("👤 Leadership", {
            "fields": ("head_of_department",),
            "description": "Assign a department head (optional).",
        }),
        ("📅 Record History", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    # 🔍 Custom Display Methods
    @admin.display(description="Department Head")
    def head_display(self, obj):
        if obj.head_of_department:
            return f"{obj.head_of_department.user.get_full_name()}"
        return "—"

    # 🔐 Permissions (optional, safety net)
    def has_delete_permission(self, request, obj=None):
        if obj and not obj.is_active:
            return True
        return super().has_delete_permission(request, obj)

    # 🧼 Clean-up and Pre-save Hook (optional)
    def save_model(self, request, obj, form, change):
        obj.name = obj.name.title().strip()
        obj.code = obj.code.upper().strip()
        super().save_model(request, obj, form, change)



# ===============================================
# ⚙️ Academic Year Admin Configuration
# ===============================================


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Academic Years with clean layout,
    validation enforcement, and readonly timestamps.
    """

    # ---------------------------
    # 📋 List View
    # ---------------------------
    list_display = (
        'name_display',
        'start_date',
        'end_date',
        'is_active',
        'is_current',
        'is_closed',
        'created_at',
    )
    list_filter = ('is_active', 'is_current', 'is_closed')
    search_fields = ('name',)
    ordering = ('-start_date',)

    # ---------------------------
    # 📝 Field Grouping
    # ---------------------------
    fieldsets = (
        (_("Basic Information"), {
            'fields': (
                'name',
                ('start_date', 'end_date'),
            )
        }),
        (_("Status Flags"), {
            'fields': (
                'is_active',
                'is_closed',
                'is_current',
            )
        }),
        (_("Timestamps"), {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    # ---------------------------
    # 🔒 Read-only Fields
    # ---------------------------
    readonly_fields = ('created_at', 'updated_at')

    # ---------------------------
    # 🧠 Custom Display Logic
    # ---------------------------
    @admin.display(description="Academic Year")
    def name_display(self, obj):
        return format_html(
            "<strong>{}</strong>", obj.name
        )

    def save_model(self, request, obj, form, change):
        """
        Extra safety: Validate before saving from admin UI.
        """
        obj.full_clean()  # Enforce model-level clean()
        super().save_model(request, obj, form, change)


# ===============================================
# 🎓 Grade Level Admin
# ===============================================

@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    """
    Admin configuration for GradeLevel model.
    Provides clean list views, search, and validation tools.
    """

    # 🎯 What to show in the list view
    list_display = ("display_name", "reference_code", "grade_number", "year_level")
    list_editable = ("reference_code", "year_level")
    list_filter = ("grade_number",)
    search_fields = ("display_name", "reference_code")
    ordering = ("grade_number",)

    # 🛠️ Fields layout when adding or editing a grade level
    fieldsets = (
        ("Basic Grade Info", {
            "fields": ("grade_number", "year_level", "reference_code", "display_name")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("created_at", "updated_at")

    # 🧹 Optional: Prevent duplicate grade numbers (already enforced at model level)
    def save_model(self, request, obj, form, change):
        obj.full_clean()  # Trigger model-level validation
        super().save_model(request, obj, form, change)


# ===============================================
# 🛠️ Admin Configuration: ClassGroup
# ===============================================

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    """
    Admin UI for managing class groups, grouped by academic year and grade level.
    """

    # 🔍 Useful fields in the list view
    list_display = ("name", "academic_year", "grade_level")
    list_filter = ("academic_year", "grade_level")
    search_fields = ("name", "academic_year__name", "grade_level__reference_code")
    
    # ⚡ Foreign key selector improvements
    autocomplete_fields = ("academic_year", "grade_level")

    # 📝 Group fields for better UI
    fieldsets = (
        (None, {
            "fields": ("academic_year", "grade_level", "name")
        }),
    )

    # 🚫 Prevent editing of auto-generated name
    readonly_fields = ("name",)

    # 🧠 Optional: Order by year descending + grade
    ordering = ("-academic_year__start_date", "grade_level__grade_number")



# ===============================================
# 🛠️ Admin Configuration: Subject
# ===============================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """
    Admin interface for managing academic subjects per grade and department.
    """

    # 🧾 Display overview
    list_display = ("name", "code", "grade_level", "department")
    list_filter = ("grade_level", "department")
    search_fields = ("name", "code", "grade_level__reference_code", "department__code")

    # 🧠 Autocomplete where possible
    autocomplete_fields = ("grade_level", "department")

    # 🚫 Prevent editing of auto-generated subject code
    readonly_fields = ("code",)

    # 🗂️ Field arrangement
    fieldsets = (
        (None, {
            "fields": ("name", "department", "grade_level", "code")
        }),
    )

    # 🔽 Default ordering
    ordering = ("grade_level__grade_number", "department__code")
