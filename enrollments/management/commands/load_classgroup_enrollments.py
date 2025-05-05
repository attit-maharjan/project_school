# ==========================================================
# 📦 Django Management Command to Import Class Enrollments
# ==========================================================
import csv
import os
from datetime import date
from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import Student
from the_school.models import ClassGroup
from enrollments.models import StudentEnrollmentType, ClassGroupStudentEnrollment

# -----------------------------------------
# 🛠 Command: load_classgroup_enrollments
# -----------------------------------------
class Command(BaseCommand):
    help = "📥 Import initial class group enrollments from initial_classgroup_enrollment.csv"

    def handle(self, *args, **kwargs):
        csv_path = settings.CSV_DATA_DIR / "initial_classgroup_enrollment.csv"

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"❌ File not found: {csv_path}"))
            return

        created_count = 0
        skipped_count = 0

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                email = row.get("email", "").strip().lower()
                classgroup_name = row.get("classgroup", "").strip()
                enrollment_code = row.get("code", "").strip().upper()

                if not email or not classgroup_name or not enrollment_code:
                    self.stderr.write(self.style.WARNING(f"⚠️ [SKIPPED] Missing required fields in row: {row}"))
                    skipped_count += 1
                    continue

                try:
                    student = Student.objects.select_related("user").get(user__email__iexact=email)
                except Student.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"⚠️ [SKIPPED] Student not found for email: {email}"))
                    skipped_count += 1
                    continue

                try:
                    class_group = ClassGroup.objects.get(name__iexact=classgroup_name)
                except ClassGroup.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"⚠️ [SKIPPED] Class group not found: {classgroup_name}"))
                    skipped_count += 1
                    continue

                try:
                    enrollment_type = StudentEnrollmentType.objects.get(code__iexact=enrollment_code)
                except StudentEnrollmentType.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"⚠️ [SKIPPED] Enrollment type not found for code: {enrollment_code}"))
                    skipped_count += 1
                    continue

                if ClassGroupStudentEnrollment.objects.filter(student=student, class_group=class_group).exists():
                    self.stdout.write(self.style.WARNING(f"⏭ [SKIPPED] Enrollment already exists for: {student} in {class_group}"))
                    skipped_count += 1
                    continue

                enrollment = ClassGroupStudentEnrollment.objects.create(
                    student=student,
                    class_group=class_group,
                    enrollment_type=enrollment_type,
                    enrollment_date=date.today(),
                    is_active=True
                )

                self.stdout.write(self.style.SUCCESS(f"✅ [CREATED] {enrollment}"))
                created_count += 1

        # -----------------------------------------
        # 🧾 Summary Output
        # -----------------------------------------
        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Enrollment import completed. Created: {created_count}, Skipped: {skipped_count}"
        ))
