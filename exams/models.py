# ==========================================================
# 🧾 Exams App — Core Data Models
# ==========================================================
# This module defines the essential data models for the Exams app.
# These models manage exam configurations, grading scales, and
# the recording of student performance.
#
# ┌────────────┬─────────────────────────────────────────────┐
# │   Model    │ Purpose                                     │
# ├────────────┼─────────────────────────────────────────────┤
# │ GradeScale │ Defines a full grading system               │
# │            │ (e.g., “CAPS 2024”)                         │
# ├────────────┼─────────────────────────────────────────────┤
# │ GradeRange │ Maps a letter grade to a % range            │
# │            │ under a specific GradeScale                 │
# ├────────────┼─────────────────────────────────────────────┤
# │ ExamType   │ Singleton model for defining exam categories│
# │            │ and their weightings                        │
# ├────────────┼─────────────────────────────────────────────┤
# │ Exam       │ Represents an assessment event              │
# │            │ with details like subject, type, and scale  │
# ├────────────┼─────────────────────────────────────────────┤
# │ StudentMark│ Stores an individual student’s score + grade│
# │            │ for a specific exam                         │
# └────────────┴─────────────────────────────────────────────┘
# ==========================================================

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import validate_email
from django.apps import apps
from django.utils.translation import gettext_lazy as _




# ==========================================================
# 📊 Model: GradeScale
# ==========================================================
# A grading system that groups multiple GradeRanges to map
# percentage scores to letter grades (e.g., “CAPS 2024”).
# ==========================================================


class GradeScale(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="A unique identifier for this grading scale, e.g., 'CAPS 2024'."
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description providing details or context for this grading scale."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp indicating when this grading scale was created."
    )

    class Meta:
        verbose_name = "Exam Grade Scale"
        verbose_name_plural = "Exam Grade Scales"  # 👈 Display name in Django admin

    def __str__(self):
        return self.name

    # 🔍 Internal Validation
    def validate_ranges(self):
        """
        Validates that GradeRanges in this scale do not overlap.
        Useful for ensuring data consistency. Can be triggered manually
        or during admin form processing.
        """
        ranges = self.grade_ranges.order_by('min_percentage')
        last_max = -1
        for r in ranges:
            if r.min_percentage <= last_max:
                raise ValidationError(f"Overlapping range at grade {r.letter}")
            last_max = r.max_percentage


# =====================================
# 🧮 Model: GradeRange
# =====================================
# Defines a single letter grade and its percentage boundaries
# within a specific GradeScale. Can include optional GPA points.
# =====================================

class GradeRange(models.Model):
    scale = models.ForeignKey(
        GradeScale,
        on_delete=models.CASCADE,
        related_name='grade_ranges',
        help_text="The grading scale to which this grade range belongs."
    )
    letter = models.CharField(max_length=3)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    # 👇 Add this
    points = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        help_text="Optional points equivalent for GPA/weighting.",
        default=0.00
    )

    class Meta:
        ordering = ['-min_percentage']
        unique_together = ('scale', 'letter')

    def __str__(self):
        return f"{self.letter}: {self.min_percentage}% - {self.max_percentage}%"


# ======================================
# 🏷️ Model: ExamType
# ======================================
# Singleton model that defines exam categories and their
# weightings (e.g., Final Exam = 40%). Only one instance
# is permitted for this project.
# ======================================

class ExamType(models.Model):
    """
    Represents the type of exam. For this project, only one instance is allowed (e.g., Final Exam).
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        default="Final Exam"
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Weight as percentage (e.g. 40 for 40%)"
    )

    class Meta:
        verbose_name = "Exam Type"
        verbose_name_plural = "Exam Type"

    def __str__(self):
        return f"{self.name} ({self.weight}%)"

    def clean(self):
        # Allow only one instance of ExamType
        if not self.pk and ExamType.objects.exists():
            raise ValidationError("For This Project only One ExamType Instance is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run clean() before saving
        super().save(*args, **kwargs)




# ==========================================================
# 📘 Model: Exam
# ==========================================================
# Represents an academic assessment for a specific subject,
# class group, and academic year. The Exam model includes
# metadata, grading scale links, and validation logic.
#
# 🔗 Relationships:
# - Subject, ClassGroup, AcademicYear, ExamType
# - Created by a Teacher
# - Uses an optional GradeScale
#
# ✅ Key Features:
# - Auto-generates exam code
# - Validates teacher authorization
# - Validates subject-class-year linkage
# - Validates admin notification emails
# ==========================================================


class Exam(models.Model):
    # 🔗 Core foreign keys and metadata
    subject = models.ForeignKey(
        "the_school.Subject",
        on_delete=models.CASCADE,
        related_name="exams"
    )
    class_group = models.ForeignKey(
        "the_school.ClassGroup",
        on_delete=models.CASCADE,
        related_name="exams"
    )
    academic_year = models.ForeignKey(
        "the_school.AcademicYear",
        on_delete=models.CASCADE
    )
    exam_type = models.ForeignKey(
        "exams.ExamType",
        on_delete=models.PROTECT
    )
    created_by = models.ForeignKey(
        "users.Teacher",
        on_delete=models.CASCADE,
        related_name="created_exams"
    )

    # 📋 Exam details
    title = models.CharField(max_length=100)
    date_conducted = models.DateField(default=timezone.now)
    max_marks = models.PositiveIntegerField(default=100)
    grading_scale = models.ForeignKey(
        "exams.GradeScale",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    exam_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        db_index=True
    )

    # 📫 Notifications / Admin use
    admin_emails = models.TextField(
        default='',
        help_text="Comma-separated admin contact emails"
    )

    # 🕓 Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_conducted']
        unique_together = ('subject', 'class_group', 'academic_year', 'exam_type')
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        try:
            return f"{self.exam_code or 'Exam'} - {self.subject or 'No Subject'} ({self.exam_type or 'No Type'})"
        except Exception:
            return "Incomplete Exam"


    # 🔐 Generate a unique exam code
    def generate_exam_code(self):
        return f"{self.subject.code}-{self.academic_year.name}"

    # ✅ Pre-save validation
    def clean(self):
        # 🛡️ Skip validation if required foreign keys aren't filled yet (like in admin preview)
        if not all([self.subject_id, self.class_group_id, self.academic_year_id, self.created_by_id]):
            return  # Let Django admin's own form validation deal with required fields

        # Proceed with real validation


        # 🔁 Lazy imports (to avoid circular dependencies)
        ClassGroupSubjectAssignment = apps.get_model('enrollments', 'ClassGroupSubjectAssignment')
        TeacherSubjectAssignment = apps.get_model('enrollments', 'TeacherSubjectAssignment')
        ClassGroupTeacherAssignment = apps.get_model('enrollments', 'ClassGroupTeacherAssignment')

        # ✅ 1. Is subject assigned to class group for the academic year?
        if not ClassGroupSubjectAssignment.objects.filter(
            class_group=self.class_group,
            subject=self.subject,
            academic_year=self.academic_year,
            is_active=True
        ).exists():
            raise ValidationError({
                'subject': f"'{self.subject}' is not assigned to '{self.class_group}' for {self.academic_year}."
            })

        # ✅ 2. Is creator authorized?
        is_authorized = (
            TeacherSubjectAssignment.objects.filter(
                teacher=self.created_by,
                subject=self.subject,
                academic_year=self.academic_year,
                is_active=True
            ).exists()
            or ClassGroupTeacherAssignment.objects.filter(
                teacher=self.created_by,
                class_group=self.class_group,
                academic_year=self.academic_year,
                is_active=True
            ).exists()
            or self.subject.department.head_of_department == self.created_by
        )

        if not is_authorized:
            raise ValidationError({
                'created_by': f"{self.created_by} is not authorized — must be subject teacher, class teacher, or department HOD."
            })

        # ✅ 3. Validate admin emails
        emails = [e.strip() for e in self.admin_emails.split(',') if e.strip()]
        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError({'admin_emails': f"Invalid email address: {email}"})



    # 🧼 Save method with full validation and exam code generation
    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.exam_code:
            self.exam_code = self.generate_exam_code()
        super().save(*args, **kwargs)




# ==========================================================
# 🎯 Model: StudentMark
# ==========================================================
# Stores a student's score and letter grade for a given Exam.
#
# ✅ Validations:
# - Student is enrolled in the Exam’s class group
# - Score does not exceed max_marks
# - Grade is auto-calculated based on the GradeScale
# ==========================================================

class StudentMark(models.Model):
    exam = models.ForeignKey(
        "exams.Exam",
        on_delete=models.CASCADE,
        related_name="student_marks"
    )
    student = models.ForeignKey(
        "users.Student",
        on_delete=models.CASCADE,
        related_name="exam_marks"
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score awarded to the student."
    )
    grade = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        help_text="Letter grade calculated from the exam’s grading scale."
    )

    class Meta:
        unique_together = ("exam", "student")
        verbose_name = "Student Mark"
        verbose_name_plural = "Student Marks"

    def __str__(self):
        try:
            return f"{self.student} • {self.exam.exam_code} • {self.score or 'No Score'}"
        except Exception:
            return "Unresolved StudentMark"

    def clean(self):
        super().clean()

        # 🛡️ Skip full validation if foreign keys aren't filled (admin preview protection)
        if not self.exam_id or not self.student_id:
            return

        # 🧠 Dynamically load enrollment model
        ClassGroupStudentEnrollment = apps.get_model('enrollments', 'ClassGroupStudentEnrollment')

        # ✅ Validate student is in the exam's class group
        if not ClassGroupStudentEnrollment.objects.filter(
            class_group=self.exam.class_group,
            student=self.student,
            is_active=True
        ).exists():
            raise ValidationError(_("Student is not in the class group assigned to this exam."))

        # ✅ Validate score is within max_marks
        if self.score is not None and self.exam.max_marks is not None:
            if self.score > self.exam.max_marks:
                raise ValidationError(_("Score cannot exceed the exam's maximum marks."))


    def save(self, *args, **kwargs):
        self.full_clean()
        self.calculate_grade()
        super().save(*args, **kwargs)

    def calculate_grade(self):
        if self.score is not None and self.exam.grading_scale:
            percentage = (self.score / self.exam.max_marks) * 100
            grade_ranges = self.exam.grading_scale.grade_ranges.order_by("min_percentage")
            for gr in grade_ranges:
                if gr.min_percentage <= percentage <= gr.max_percentage:
                    self.grade = gr.letter
                    return
            self.grade = "N/A"
