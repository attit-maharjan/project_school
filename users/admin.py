# users app > admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Parent, Student, Teacher

# ========== INLINE ADMIN ==========

class ParentInline(admin.StackedInline):
    model = Parent
    extra = 0
    can_delete = False


class StudentInline(admin.StackedInline):
    model = Student
    extra = 0
    can_delete = False
    readonly_fields = ('student_id',)


class TeacherInline(admin.StackedInline):
    model = Teacher
    extra = 0
    can_delete = False
    readonly_fields = ('employee_id', 'hire_date')


# ========== USER ADMIN ==========

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [ParentInline, StudentInline, TeacherInline]
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'gender', 'is_active', 'country')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    readonly_fields = ('date_joined',)

    fieldsets = (
        ("Login Credentials", {"fields": ("email", "password")}),
        ("Personal Info", {
            "fields": (
                "first_name", "initials", "last_name", "dob", "gender", "role", "profile_image"
            )
        }),
        ("Contact Info", {"fields": ("phone_number",)}),
        ("Address", {
            "fields": ("street_address", "city", "state_province", "postal_code", "country")
        }),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("date_joined",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )


# ========== STUDENT ADMIN ==========

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'enrollment_date', 'is_active_student')
    list_filter = ('enrollment_date', 'is_active_student')
    search_fields = ('user__first_name', 'user__last_name', 'student_id')
    readonly_fields = ('student_id',)

    fieldsets = (
        (None, {
            "fields": (
                "user", "enrollment_date", "student_id", "is_active_student"
            )
        }),
        ("Parent/Guardian Info", {
            "fields": ("father", "mother", "guardian")
        }),
    )


# ========== TEACHER ADMIN ==========

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'teacher_role', 'salary')
    list_filter = ('teacher_role',)
    search_fields = ('user__first_name', 'user__last_name', 'employee_id')
    readonly_fields = ('employee_id', 'hire_date')

    fieldsets = (
        (None, {
            "fields": (
                "user", "hire_date", "employee_id", "salary", "teacher_role", "custom_teacher_role"
            )
        }),
    )


# ========== PARENT ADMIN ==========

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'alternative_emergency_phone_number')
    search_fields = ('user__first_name', 'user__last_name', 'alternative_emergency_phone_number')
