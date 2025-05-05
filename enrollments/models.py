# ==========================================================
# 📁 enrollments/models.py
# ==========================================================
# This file contains models related to teacher subject
# assignments and other enrollment-related data.
# ==========================================================


#============================
# 📦 Import Statements
#============================

from django.db import models  # Base class for defining Django models
from django.core.exceptions import ValidationError  # To raise validation errors
from django.utils import timezone  # For managing date and time fields



# -------------------------------
# 📘 Student Enrollment Type
# -------------------------------
class StudentEnrollmentType(models.Model):
    """
    Defines the method or reason a student is enrolled in a class group.
    Examples: Fresh Enrollment, Transfer, Promoted, Repeat, Re-enrolled.
    """

    # -----------------------------
    # 🧩 Core Fields
    # -----------------------------
    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text="Short code like FRESH, TRANSFER, PROMOTED, etc."
    )
    name = models.CharField(
        max_length=50,
        help_text="Descriptive name of the enrollment type."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional longer explanation for internal use."
    )

    # -----------------------------
    # 🔒 Meta Configuration
    # -----------------------------
    class Meta:
        verbose_name = "Student Enrollment Type"
        verbose_name_plural = "Student Enrollment Types"
        ordering = ['code']

    # -----------------------------
    # 🔁 String Representation
    # -----------------------------
    def __str__(self):
        return f"{self.code} - {self.name}"







# -------------------------------
# 📘 Class Group Student Enrollment
# -------------------------------
class ClassGroupStudentEnrollment(models.Model):
    """
    Links a student to a specific class group for a given academic year
    and records how they enrolled (e.g., Fresh, Transfer, Repeat).
    """

    # -------------------------------------------
    # 🔗 Relationships
    # -------------------------------------------
    student = models.ForeignKey(
        "users.Student",
        on_delete=models.CASCADE,
        related_name="class_group_enrollments",
        help_text="The student being enrolled."
    )
    class_group = models.ForeignKey(
        "the_school.ClassGroup",
        on_delete=models.CASCADE,
        related_name="student_enrollments",
        help_text="The class group the student is assigned to."
    )
    enrollment_type = models.ForeignKey(
        "enrollments.StudentEnrollmentType",
        on_delete=models.PROTECT,
        help_text="The reason or method of enrollment (e.g., Transfer, Fresh)."
    )

    # -------------------------------------------
    # 📆 Enrollment Info
    # -------------------------------------------
    enrollment_date = models.DateField(
        help_text="Date when the student was enrolled in this class group."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if this enrollment is currently active."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes for this enrollment (manual remarks, exceptions, etc.)."
    )

    # -------------------------------------------
    # 🕓 Timestamps
    # -------------------------------------------
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated."
    )

    # -------------------------------------------
    # 🔒 Meta Configuration
    # -------------------------------------------
    class Meta:
        verbose_name = "Class Group Student Enrollment"
        verbose_name_plural = "Class Group Student Enrollments"
        ordering = ["-enrollment_date", "student"]
        unique_together = ("student", "class_group")  # Enforce one enrollment per class group

    # -------------------------------------------
    # 🔁 String Representation
    # -------------------------------------------
    def __str__(self):
        return f"{self.student} → {self.class_group} [{self.enrollment_type.code}]"




# ==========================================================
# 🧑‍🏫 Teacher Department Enrollment Model
# ==========================================================
# This model captures the assignment of a teacher to a specific
# department, optionally within a particular academic year.
# Great for tracking staff roles, departmental rotations, and
# ensuring uniqueness per year per department per teacher.
# ==========================================================

# -----------------------------------------
# 🧩 Model: TeacherDepartmentEnrollment
# -----------------------------------------
class TeacherDepartmentEnrollment(models.Model):
    """
    Links a teacher to a department, optionally for a specific academic year.
    Useful for managing staff assignments, rotations, or role-based scheduling.
    """

    # 🧑‍🏫 Teacher being assigned
    teacher = models.ForeignKey(
        "users.Teacher",
        on_delete=models.CASCADE,
        related_name="department_enrollments",
        help_text="The teacher being assigned."
    )

    # 🏢 Department assigned to
    department = models.ForeignKey(
        "the_school.Department",
        on_delete=models.CASCADE,
        related_name="teacher_enrollments",
        help_text="The department the teacher is assigned to."
    )

    # 📅 Optional Academic Year (if time-bound)
    academic_year = models.ForeignKey(
        "the_school.AcademicYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: Academic year for this enrollment (e.g., 2025)."
    )

    # 🗓️ Date of assignment
    date_assigned = models.DateField(default=timezone.now)

    # ✅ Whether this enrollment is currently active
    is_active = models.BooleanField(default=True)

    # -----------------------------------------
    # ⚙️ Meta Options
    # -----------------------------------------
    class Meta:
        verbose_name = "Teacher Department Enrollment"
        verbose_name_plural = "Teacher Department Enrollments"
        ordering = ['-date_assigned']
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'department', 'academic_year'],
                name='unique_teacher_department_enrollment'
            )
        ]

    # -----------------------------------------
    # 🔁 String Representation
    # -----------------------------------------
    def __str__(self):
        return f"{self.teacher} → {self.department} ({self.academic_year or 'Permanent'})"

    # -----------------------------------------
    # ✅ Clean: Enforce Unique Constraint
    # -----------------------------------------
    def clean(self):
        # Prevent duplicate enrollments for same teacher-department-year combo
        if self.__class__.objects.exclude(pk=self.pk).filter(
            teacher=self.teacher,
            department=self.department,
            academic_year=self.academic_year
        ).exists():
            raise ValidationError(
                "This teacher is already assigned to this department for the selected academic year."
            )





#============================
# 🎯 Model: TeacherSubjectAssignment
#============================
# Assigns a teacher to a single subject, optionally scoped
# to a specific academic year. Ensures that no teacher is
# assigned to more than one subject per academic year.
#============================

class TeacherSubjectAssignment(models.Model):
    """
    Assigns a teacher to a subject (one subject per teacher).
    Optionally scoped to an academic year.
    """

    #============================
    # Fields
    #============================

    teacher = models.OneToOneField(
        "users.Teacher",  # Link to the Teacher model from the users app
        on_delete=models.CASCADE,  # Delete assignment if teacher is deleted
        related_name="subject_assignment",  # Enables reverse lookup from Teacher
        help_text="The teacher being assigned to a subject."
    )

    subject = models.ForeignKey(
        "the_school.Subject",  # Link to the Subject model
        on_delete=models.CASCADE,  # Delete assignment if subject is deleted
        related_name="assigned_teachers",  # Enables reverse lookup from Subject
        help_text="The subject this teacher is responsible for."
    )

    academic_year = models.ForeignKey(
        "the_school.AcademicYear",  # Optional academic year scope
        on_delete=models.SET_NULL,  # Set to NULL if academic year is deleted
        null=True,
        blank=True,
        help_text="Optional: The academic year of the assignment."
    )

    date_assigned = models.DateField(
        default=timezone.now  # Automatically set to the current date
    )

    is_active = models.BooleanField(
        default=True  # Indicates if the assignment is currently active
    )

    #============================
    # Meta Configuration
    #============================

    class Meta:
        verbose_name = "Teacher Subject Assignment"
        verbose_name_plural = "Teacher Subject Assignments"
        unique_together = ("teacher", "academic_year")  # Prevent duplicate assignments per academic year
        ordering = ['-date_assigned']  # Newest assignments first

    #============================
    # String Representation
    #============================

    def __str__(self):
        return f"{self.teacher} → {self.subject} ({self.academic_year or 'Permanent'})"

    #============================
    # Custom Validation
    #============================

    def clean(self):
        """
        Enforce that a teacher can only be assigned to one subject at a time
        per academic year (or permanently if no year is set).
        """
        if TeacherSubjectAssignment.objects.exclude(pk=self.pk).filter(
            teacher=self.teacher,
            academic_year=self.academic_year
        ).exists():
            raise ValidationError("This teacher already has a subject assigned for the selected academic year.")




#============================
# 🧑‍🏫 Model: ClassGroupTeacherAssignment
#============================
# ----------------------------------------------------------
# Assigns a teacher to a ClassGroup, limited to teachers 
# whose role is "Classroom Teacher". Can be optionally scoped 
# by academic year, and includes uniqueness validation.
# ==========================================================


class ClassGroupTeacherAssignment(models.Model):
    """
    Assigns a teacher to a ClassGroup, only if the teacher is a Classroom Teacher.
    """

    #============================
    # 🔗 Relationships
    #============================

    teacher = models.ForeignKey(
        "users.Teacher",
        on_delete=models.CASCADE,
        related_name="classgroup_assignments",
        help_text="The teacher being assigned to a class group."
    )

    class_group = models.ForeignKey(
        "the_school.ClassGroup",
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
        help_text="The class group the teacher will lead."
    )

    academic_year = models.ForeignKey(
        "the_school.AcademicYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional academic year of the assignment."
    )

    #============================
    # 📅 Additional Fields
    #============================

    date_assigned = models.DateField(
        default=timezone.now,
        help_text="The date the assignment was created."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this assignment is currently active."
    )

    #============================
    # ⚙️ Model Metadata
    #============================

    class Meta:
        verbose_name = "Class Group Teacher Assignment"
        verbose_name_plural = "Class Group Teacher Assignments"
        unique_together = (
            ("teacher", "academic_year"),
            ("class_group", "academic_year")
        )  # Prevent duplicate assignments
        ordering = ["-date_assigned"]

    #============================
    # 📌 String Representation
    #============================

    def __str__(self):
        return f"{self.teacher} → {self.class_group} ({self.academic_year or 'Permanent'})"

    #============================
    # ✅ Model-Level Validation
    #============================

    def clean(self):
        """
        - Enforce that teacher must have role "Classroom Teacher"
        - Ensure no duplicates for teacher/class group per academic year
        """

        # Ensure only classroom teachers can be assigned
        if self.teacher.teacher_role != "Classroom Teacher":
            raise ValidationError("Only teachers with the role 'Classroom Teacher' can be assigned to a class group.")

        # Prevent duplicate teacher assignment for the same year
        if ClassGroupTeacherAssignment.objects.exclude(pk=self.pk).filter(
            teacher=self.teacher,
            academic_year=self.academic_year
        ).exists():
            raise ValidationError("This teacher is already assigned to a class group for the selected academic year.")

        # Prevent duplicate class group assignment for the same year
        if ClassGroupTeacherAssignment.objects.exclude(pk=self.pk).filter(
            class_group=self.class_group,
            academic_year=self.academic_year
        ).exists():
            raise ValidationError("This class group already has a teacher assigned for the selected academic year.")





# ========================================================
# 📘 ClassGroupSubjectAssignment Model
# ========================================================
# Purpose:
# - Defines which subjects are assigned to which class groups
#   in a particular academic year.
# - Supports filtering by date and status (`is_active`).
# - Enforces uniqueness per class group, subject, and year.
# - Commonly used for curriculum planning and timetable validation.
# ========================================================


class ClassGroupSubjectAssignment(models.Model):
    """
    Assigns a subject to a class group for a specific academic year.
    Used to define which subjects are taught in which class groups.
    """

    # 🔗 ForeignKey to the class group receiving the subject
    class_group = models.ForeignKey(
        "the_school.ClassGroup",
        on_delete=models.CASCADE,
        related_name="subject_assignments",
        help_text="Class group to which the subject is being assigned."
    )

    # 🔗 ForeignKey to the subject being taught
    subject = models.ForeignKey(
        "the_school.Subject",
        on_delete=models.CASCADE,
        related_name="class_assignments",
        help_text="The subject being taught to the class group."
    )

    # 📅 Academic year of the assignment
    academic_year = models.ForeignKey(
        "the_school.AcademicYear",
        on_delete=models.CASCADE,
        help_text="The academic year this assignment applies to."
    )

    # 🕒 Date the assignment was made (defaults to today)
    date_assigned = models.DateField(
        default=timezone.now,
        help_text="Date when this subject was assigned to the class group."
    )

    # ✅ Whether the assignment is currently active
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this subject is currently active in the class group."
    )

    # 📐 Meta options for admin and constraints
    class Meta:
        verbose_name = "ClassGroup Subject Assignment"
        verbose_name_plural = "ClassGroup Subject Assignments"
        unique_together = ("class_group", "subject", "academic_year")  # Prevents duplication
        ordering = ["-date_assigned"]  # Newest first

    # 🪪 Human-readable representation
    def __str__(self):
        return f"{self.class_group} → {self.subject} ({self.academic_year})"

    # 🚫 Enforce uniqueness manually (in case of race conditions)
    def clean(self):
        # ✅ Enforce uniqueness
        if ClassGroupSubjectAssignment.objects.exclude(pk=self.pk).filter(
            class_group=self.class_group,
            subject=self.subject,
            academic_year=self.academic_year
        ).exists():
            raise ValidationError(
                "This subject is already assigned to this class group for the given academic year."
            )

        # ✅ Enforce grade level compatibility
        if self.subject.grade_level != self.class_group.grade_level:
            raise ValidationError(
                f"The subject '{self.subject}' is for {self.subject.grade_level}, "
                f"but the class group '{self.class_group}' is for {self.class_group.grade_level}."
            )
