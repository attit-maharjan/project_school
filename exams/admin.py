# ==========================================================
# 📁 Admin Configuration — Exams App
# ==========================================================
# This module customizes the Django admin for managing:
#   - Exam grading systems (GradeScale, GradeRange)
#   - Exam metadata and creation (Exam, ExamType)
#   - Student performance records (StudentMark)
# ----------------------------------------------------------
# Each admin class enhances the user interface with:
#   - Autocompletion for foreign keys
#   - Read-only system fields
#   - Custom fieldsets and validation hooks
# ==========================================================

from django.contrib import admin
from exams.models import Exam, GradeScale, GradeRange, ExamType, StudentMark
from django.utils.html import format_html
from django.utils.timezone import localtime
from the_school.models import Subject, ClassGroup, AcademicYear
from users.models import Teacher


# ==========================================================
# 🧮 Grade Range Inline — Inline editor within GradeScale
# ==========================================================
class GradeRangeInline(admin.TabularInline):
    model = GradeRange
    extra = 1
    min_num = 1
    fields = ("letter", "min_percentage", "max_percentage", "points")
    ordering = ["-min_percentage"]
    verbose_name = "Grade Range"
    verbose_name_plural = "Grade Ranges"


# ==========================================================
# 📊 Grade Scale Admin — Manages grading systems
# ==========================================================
@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "range_count")
    search_fields = ("name", "description")
    readonly_fields = ("created_at",)
    inlines = [GradeRangeInline]
    fieldsets = (
        (None, {"fields": ("name", "description")}),
        ("System Info", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    @admin.display(description="Number of Ranges")
    def range_count(self, obj):
        return obj.grade_ranges.count()

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # Enforce GradeScale validation rules
        super().save_model(request, obj, form, change)


# ==========================================================
# 🧾 Exam Type Admin — Singleton definition of exam types
# ==========================================================
@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "weight")
    readonly_fields = ("name",)
    search_fields = ("name",)
    ordering = ("-weight", "name")
    fieldsets = (
        (None, {
            "fields": ("name", "weight"),
            "description": "Only one exam type is allowed in this system."
        }),
    )

    def has_add_permission(self, request):
        return not ExamType.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ==========================================================
# 📝 Exam Admin — Create and manage exams
# ==========================================================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "exam_code", "title", "subject", "class_group", "academic_year",
        "exam_type", "created_by_display", "date_conducted", "is_active_display"
    )
    list_filter = ("academic_year", "exam_type", "grading_scale")
    search_fields = (
        "exam_code", "title", "subject__name", "class_group__name", "created_by__user__email"
    )
    ordering = ("-date_conducted",)

    autocomplete_fields = (
        "subject", "class_group", "academic_year",
        "exam_type", "created_by", "grading_scale"
    )

    readonly_fields = ("exam_code", "created_at", "updated_at")

    fieldsets = (
        ("🧠 Core Exam Details", {
            "fields": ("title", "subject", "class_group", "academic_year", "exam_type", "grading_scale"),
        }),
        ("📋 Metadata", {
            "fields": ("date_conducted", "max_marks", "created_by"),
        }),
        ("📫 Admin Notifications", {
            "fields": ("admin_emails",),
            "description": "Comma-separated emails for people to be notified about this exam."
        }),
        ("🔒 System Fields", {
            "fields": ("exam_code", "created_at", "updated_at"),
        }),
    )

    def created_by_display(self, obj):
        return obj.created_by.user.get_full_name() if obj.created_by else "—"
    created_by_display.short_description = "Created By"

    def is_active_display(self, obj):
        if obj.academic_year and obj.academic_year.is_active:
            return format_html('<span style="color:green;">🟢 Active</span>')
        return format_html('<span style="color:gray;">⚪ Inactive</span>')
    is_active_display.short_description = "Academic Year Status"

    def save_model(self, request, obj, form, change):
        obj.save()
        self.message_user(request, f"✅ Exam saved successfully: {obj.exam_code}")


# ==========================================================
# 📈 Student Mark Admin — Track student exam scores
# ==========================================================
@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "score", "grade")
    list_filter = ("exam__academic_year", "exam__class_group", "grade")
    search_fields = (
        "student__user__first_name", "student__user__last_name",
        "exam__exam_code", "exam__title"
    )
    autocomplete_fields = ("student", "exam")

    fieldsets = (
        (None, {
            "fields": ("exam", "student")
        }),
        ("Mark Details", {
            "fields": ("score", "grade"),
            "description": "Score is optional. Grade is calculated automatically."
        }),
    )

    readonly_fields = ("grade",)

    def get_readonly_fields(self, request, obj=None):
        # Prevent exam/student changes on edit
        if obj:
            return self.readonly_fields + ("exam", "student")
        return self.readonly_fields
