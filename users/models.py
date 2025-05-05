# users app > models.py
# =====================================================
#                   IMPORT STATEMENTS
# =====================================================

from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from django.utils.timezone import now
from datetime import date
import uuid


# =====================================================
#                   VALIDATORS
# =====================================================

phone_validator = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
)


# =====================================================
#               CUSTOM USER MANAGER
# =====================================================

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# =====================================================
#               CUSTOM USER MODEL
# =====================================================

class User(AbstractUser):
    # ----- CHOICES -----
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    # ----- BASIC INFO -----
    username = None  # Email replaces username
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=30)
    initials = models.CharField(max_length=10, blank=True, null=True)
    last_name = models.CharField(max_length=30)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student', db_index=True)

    # ----- CONTACT -----
    phone_number = models.CharField(max_length=15, blank=True, null=True, validators=[phone_validator], db_index=True)

    # ----- PROFILE IMAGE -----
    profile_image = models.ImageField(
        upload_to='profile_photos/',
        default='profile_photos/default.png',
        blank=True,
        null=True
    )

    # ----- EMBEDDED ADDRESS FIELDS -----
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank_label='(Select Country)', null=True, blank=True, db_index=True)

    # ----- SYSTEM FIELDS -----
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # ----- MANAGER -----
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    # ----- PERMISSIONS -----
    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)

    def save(self, *args, **kwargs):
        if not self.profile_image:
            self.profile_image = 'profile_photos/default.png'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


# =====================================================
#                   PARENT MODEL
# =====================================================

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alternative_emergency_phone_number = models.CharField(
        max_length=15, blank=True, null=True, validators=[phone_validator]
    )

    def __str__(self):
        return f"Parent: {self.user.first_name} {self.user.last_name}"


# =====================================================
#                   STUDENT MODEL
# =====================================================

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)
    enrollment_date = models.DateField(default=now)
    student_id = models.CharField(max_length=20, unique=True, blank=True, null=True, editable=False, db_index=True)

    is_active_student = models.BooleanField(default=True)

    father = models.ForeignKey(Parent, related_name='father', null=True, blank=True, on_delete=models.SET_NULL)
    mother = models.ForeignKey(Parent, related_name='mother', null=True, blank=True, on_delete=models.SET_NULL)
    guardian = models.ForeignKey(Parent, related_name='guardian', null=True, blank=True, on_delete=models.SET_NULL)

    def clean(self):
        if not self.father and not self.mother and not self.guardian:
            raise ValidationError("At least one parent (Father, Mother, or Guardian) must be assigned.")

    def save(self, *args, **kwargs):
        if not self.student_id:
            while True:
                sid = f"S{self.enrollment_date.year}{uuid.uuid4().hex[:8].upper()}"
                if not Student.objects.filter(student_id=sid).exists():
                    self.student_id = sid
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Student: {self.user.first_name} {self.user.last_name}"


# =====================================================
#                   TEACHER MODEL
# =====================================================

class Teacher(models.Model):
    TEACHER_ROLE_CHOICES = [
        ('Subject Teacher', 'Subject Teacher'),
        ('HOD', 'Head of Department'),
        ('Classroom Teacher', 'Classroom Teacher'),
        ('Principal', 'Principal'),
        ('Vice Principal', 'Vice Principal'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, db_index=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hire_date = models.DateField(auto_now_add=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, editable=False, db_index=True)
    teacher_role = models.CharField(max_length=30, choices=TEACHER_ROLE_CHOICES, default="Subject Teacher")
    custom_teacher_role = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="If 'Other' is selected, specify the role here."
    )

    def clean(self):
        if self.teacher_role == 'Other' and not self.custom_teacher_role:
            raise ValidationError({'custom_teacher_role': "Please specify the custom role when 'Other' is selected."})
        if self.teacher_role != 'Other':
            self.custom_teacher_role = None

    def save(self, *args, **kwargs):
        if not self.employee_id:
            while True:
                eid = f"T{date.today().year}{uuid.uuid4().hex[:8].upper()}"
                if not Teacher.objects.filter(employee_id=eid).exists():
                    self.employee_id = eid
                    break
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        display_role = self.custom_teacher_role if self.teacher_role == 'Other' else self.teacher_role
        return f"Teacher: {self.user.first_name} {self.user.last_name} ({display_role})"
