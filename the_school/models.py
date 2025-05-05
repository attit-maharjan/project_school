# the_school app > models.py

# =====================================================
#                   IMPORT STATEMENTS
# =====================================================
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.validators import (
    MinValueValidator, MaxValueValidator, RegexValidator, URLValidator
)
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


# ===============================================
# 📘 Accreditation and School Settings Model
# ===============================================



# ---------------------------
# 📁 Upload & Validation Utils
# ---------------------------
def school_logo_upload_path(instance, filename):
    """Generate a unique upload path for school logos."""
    return f"school_logos/{instance.school_name.replace(' ', '_').lower()}_{filename}"

def validate_social_links(value):
    """Validate that all values in the JSON field are valid URLs."""
    url_validator = URLValidator()
    if not isinstance(value, dict):
        raise ValidationError("Social media links must be a dictionary.")
    for key, url in value.items():
        try:
            url_validator(url)
        except ValidationError:
            raise ValidationError(f"Invalid URL for {key}: {url}")

# ---------------------------
# 🏛 Accreditor Model
# ---------------------------
class Accreditor(models.Model):
    """Stores details of organizations accrediting schools."""
    name = models.CharField(max_length=255, unique=True)
    registration_number = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True, null=True)
    accreditation_date = models.DateField()

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Expired", "Expired"),
        ("Pending", "Pending"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Active")

    def __str__(self):
        return f"{self.name} ({self.status})"

# ---------------------------
# 🏫 SchoolSettings Singleton
# ---------------------------
class SchoolSettings(models.Model):
    """
    Stores school-specific settings for site-wide display and configuration.
    Enforces singleton to ensure only one active record exists.
    """
    singleton = models.BooleanField(default=True, unique=True)

    # Core Info
    school_name = models.CharField(max_length=255, unique=True)
    school_logo = models.ImageField(upload_to=school_logo_upload_path, 
        blank=True, 
        null=True, 
        default='school_logos/no_logo.png')  # Default logo path
    school_motto = models.CharField(max_length=255, blank=True, null=True)
    established_year = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[
            MinValueValidator(1800),
            MaxValueValidator(datetime.now().year)
        ],
        help_text="Year the school was established (must be reasonable)."
    )

    # Contact
    address = models.TextField()
    contact_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?\d{7,15}$', 'Enter a valid contact number.')],
        help_text="Phone number (e.g., +123456789)."
    )
    email_address = models.EmailField()
    website_url = models.URLField(blank=True, null=True)

    # Accreditation
    accreditation_details = models.ManyToManyField(
        Accreditor, blank=True, related_name="schools"
    )
    

    # Social Media
    social_media_links = models.JSONField(
        default=dict,
        validators=[validate_social_links],
        help_text="JSON format (e.g., {'Facebook': 'https://fb.com/school'})"
    )

    # Public Website Content
    homepage_intro = models.TextField(
        blank=True, null=True,
        help_text="Optional welcome message for homepage (index.html)."
    )

    # --------------------------------------------
    # 📄 About Us Page (Structured Content Fields)
    # --------------------------------------------
    about_us_title = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Optional title override for the About Us page."
    )
    about_us_subheading1 = models.CharField(max_length=255, blank=True, null=True)
    about_us_paragraph1 = models.TextField(blank=True, null=True)
    about_us_paragraph2 = models.TextField(blank=True, null=True)
    about_us_subheading2 = models.CharField(max_length=255, blank=True, null=True)
    about_us_paragraph3 = models.TextField(blank=True, null=True)

    # --------------------------------------------
    # 📄 Contact Us Page (Optional Structured Fields)
    # --------------------------------------------
    contact_us_title = models.CharField(max_length=255, blank=True, null=True)
    contact_us_paragraph1 = models.TextField(blank=True, null=True)
    contact_us_paragraph2 = models.TextField(blank=True, null=True)

    # --------------------------------------------
    # 📄 Legal Pages (Plain Text)
    # --------------------------------------------
    privacy_policy = models.TextField(
        blank=True, null=True,
        help_text="Displayed in privacy_policy.html"
    )
    terms_of_service = models.TextField(
        blank=True, null=True,
        help_text="Displayed in terms_of_service.html"
    )

    # --------------------------------
    # 📅 Timestamps
    # --------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------------------
    # 🔒 Singleton + Integrity Control
    # --------------------------------
    def clean(self):
        """Ensure only one SchoolSettings entry exists."""
        if self.__class__.objects.exclude(pk=self.pk).exists():
            raise ValidationError("Only one School Settings entry is allowed.")

    def save(self, *args, **kwargs):
        """Singleton enforcement at DB level."""
        if not self.pk and self.__class__.objects.exists():
            raise ValidationError("Only one School Settings entry is allowed.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of the only SchoolSettings entry."""
        if self.__class__.objects.count() == 1:
            raise PermissionDenied("Cannot delete the only School Settings entry.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.school_name or "School Settings"

    class Meta:
        verbose_name = "School Settings"
        verbose_name_plural = "School Settings"
        constraints = [
            models.UniqueConstraint(fields=["singleton"], name="unique_school_settings_constraint")
        ]

    # --------------------------------
    # 🔧 Custom Properties (Frontend Friendly)
    # --------------------------------
    @property
    def about_us_page_title(self):
        return self.about_us_title or "About Our School"

    @property
    def contact_us_page_title(self):
        return self.contact_us_title or "Get in Touch"

    @property
    def homepage_title(self):
        return self.school_name or "Welcome to Our School"

    @property
    def contact_info(self):
        """Centralized contact info dictionary for DRY use in templates or APIs."""
        return {
            "address": self.address,
            "phone": self.contact_number,
            "email": self.email_address,
            "website": self.website_url,
        }



# =====================================================
# 🏢 Department Model — Academic Unit within the School
# =====================================================

class Department(models.Model):
    """
    Represents an academic department, like Science or ICT.
    Used to group staff, subjects, and internal organization.
    """

    code = models.CharField(
        max_length=10,
        unique=True,
        help_text=_("Unique department code (e.g., SCI, MAT, ICT).")
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Full name of the department (e.g., Computer Science).")
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Optional description of the department’s purpose or focus.")
    )
    head_of_department = models.ForeignKey(
        'users.Teacher',  # Replace with your actual Teacher model path
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments_led",
        help_text=_("Optional: Assign a department head.")
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_("Toggle to deactivate departments without deleting.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------
    # 🔎 String Display
    # --------------------
    def __str__(self):
        return f"{self.code} — {self.name}"

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['code']
        constraints = [
            models.UniqueConstraint(fields=['code', 'name'], name='unique_department_code_name')
        ]





# ===============================================
# 📘 Academic Year Model
# ===============================================

class AcademicYear(models.Model):
    """
    Defines a school academic year with lifecycle control.
    Enforces clean validations and singleton current year logic.
    """

    # -----------------------------
    # 🧾 Identifiers & Timeline
    # -----------------------------
    name = models.CharField(
        max_length=4,
        unique=True,
        help_text="Label for the academic year (e.g., 2025)."
    )
    start_date = models.DateField(
        help_text="Date when this academic year begins."
    )
    end_date = models.DateField(
        help_text="Date when this academic year ends."
    )

    # -----------------------------
    # 🚦 Status Flags
    # -----------------------------
    is_active = models.BooleanField(
        default=True,
        help_text="Can users interact with this academic year?"
    )
    is_closed = models.BooleanField(
        default=False,
        help_text="Marking as closed prevents further edits or associations."
    )
    is_current = models.BooleanField(
        default=False,
        help_text="The currently in-use academic year. Only one allowed."
    )

    # -----------------------------
    # 🕒 Timestamps
    # -----------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -----------------------------
    # ⚙️ Meta Options
    # -----------------------------
    class Meta:
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date.year}–{self.end_date.year})"

    # -----------------------------
    # ✅ Custom Validation
    # -----------------------------
    def clean(self):
        """
        Enforce business rules:
        - End must follow start.
        - Current year cannot be closed.
        """
        if self.end_date <= self.start_date:
            raise ValidationError("End date must be after the start date.")
        if self.is_current and self.is_closed:
            raise ValidationError("A current academic year cannot be marked as closed.")

    # -----------------------------
    # 💾 Singleton Enforcement
    # -----------------------------
    def save(self, *args, **kwargs):
        """
        If this is marked as current, demote all others.
        """
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


# ===============================================
# 🎓 Grade Level Model
# ===============================================

class GradeLevel(models.Model):
    """
    Represents a standard grade level within the school (e.g., Grade 9 - 12).
    Supports internal integer tracking, reference labels, and display names.
    """

    # -----------------------------
    # 🎯 Core Identifiers
    # -----------------------------
    grade_number = models.PositiveSmallIntegerField(
        unique=True,
        help_text="Numeric value of the grade (e.g., 9 for Grade 9)."
    )
    year_level = models.PositiveSmallIntegerField(
        help_text="Optional internal academic level indicator (e.g., 1 for Grade 9)."
    )
    reference_code = models.CharField(
        max_length=10,
        unique=True,
        help_text="Short code used internally or on transcripts (e.g., G9, G12)."
    )
    display_name = models.CharField(
        max_length=50,
        help_text="Display name for UI (e.g., 'Grade 9', 'Form 1')."
    )

    # -----------------------------
    # 🕒 Timestamps
    # -----------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -----------------------------
    # 🔒 Meta Configuration
    # -----------------------------
    class Meta:
        verbose_name = "Grade Level"
        verbose_name_plural = "Grade Levels"
        ordering = ["grade_number"]

    def __str__(self):
        return f"{self.display_name} ({self.reference_code})"

    # -----------------------------
    # ✅ Validation (Optional)
    # -----------------------------
    def clean(self):
        """
        Example validation: Ensure display_name includes grade_number.
        """
        if str(self.grade_number) not in self.display_name:
            raise ValidationError(
                "Display name should ideally include the grade number."
            )
            
            
            
# ===============================================
# 🏫 ClassGroup Model
# ===============================================

class ClassGroup(models.Model):
    """
    Represents a class group in a specific academic year and grade level.
    For example: '2025-G9' for Grade 9 in the 2025 academic year.
    """

    # -----------------------------
    # 🔗 Foreign Keys
    # -----------------------------
    academic_year = models.ForeignKey(
        'AcademicYear',
        on_delete=models.CASCADE,
        related_name="class_groups",
        verbose_name="Academic Year",
        help_text="The academic year this class group belongs to."
    )
    grade_level = models.ForeignKey(
        'GradeLevel',
        on_delete=models.PROTECT,
        related_name="class_groups",
        verbose_name="Grade Level",
        help_text="The grade level assigned to this class group."
    )

    # -----------------------------
    # 🆔 Class Identifier
    # -----------------------------
    name = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Class Group Name",
        help_text="Auto-generated name like '2025-G9'."
    )

    # -----------------------------
    # 🔒 Meta Configuration
    # -----------------------------
    class Meta:
        verbose_name = "Class Group"
        verbose_name_plural = "Class Groups"
        ordering = ['-academic_year', 'grade_level']
        unique_together = ('academic_year', 'grade_level')

    def __str__(self):
        return self.name

    # -----------------------------
    # ✅ Clean Validation
    # -----------------------------
    def clean(self):
        """
        Ensures required fields are set and name is correctly formatted.
        """
        if not self.academic_year or not self.grade_level:
            raise ValidationError("Academic year and grade level are required.")

        # Generate unique name (e.g., '2025-G9')
        self.name = f"{self.academic_year.name}-{self.grade_level.reference_code}"

    # -----------------------------
    # 💾 Save Logic
    # -----------------------------
    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure validation & name assignment
        super().save(*args, **kwargs)
            



# ===============================================
# 📘 Subject Model
# ===============================================
class Subject(models.Model):
    """
    Represents a subject taught in a particular grade level.
    Example: 'MAT-G9' for Mathematics in Grade 9.
    """

    # -----------------------------
    # 🔗 Foreign Keys
    # -----------------------------
    department = models.ForeignKey(
        'Department',
        on_delete=models.PROTECT,
        related_name='subjects',
        help_text="The department offering this subject (e.g., Mathematics)."
    )
    grade_level = models.ForeignKey(
        'GradeLevel',
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="The grade level where this subject is taught."
    )

    # -----------------------------
    # 📘 Subject Details
    # -----------------------------
    name = models.CharField(
        max_length=100,
        help_text="Full name of the subject (e.g., Algebra I, Physics)."
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        help_text="Auto-generated subject code (e.g., MAT-G9)."
    )

    # -----------------------------
    # 🔒 Meta Configuration
    # -----------------------------
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['grade_level', 'department', 'name']
        unique_together = ('department', 'grade_level', 'name')

    def __str__(self):
        return f"{self.name} ({self.code})"

    # -----------------------------
    # ✅ Clean Validation
    # -----------------------------
    def clean(self):
        """
        Ensures department and grade level are set, and validates logic.
        """
        if not self.department or not self.grade_level:
            raise ValidationError("Both department and grade level are required.")
        
        # Generate subject code like 'MAT-G9'
        self.code = f"{self.department.code}-{self.grade_level.reference_code}"

    # -----------------------------
    # 💾 Save Logic
    # -----------------------------
    def save(self, *args, **kwargs):
        self.full_clean()  # Runs clean() before saving
        super().save(*args, **kwargs)
