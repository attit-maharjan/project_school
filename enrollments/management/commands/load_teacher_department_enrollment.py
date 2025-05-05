import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now
from users.models import Teacher, User
from the_school.models import Department, AcademicYear
from enrollments.models import TeacherDepartmentEnrollment

class Command(BaseCommand):
    help = "Import teacher-department enrollments from a CSV file."

    def handle(self, *args, **options):
        csv_path = settings.CSV_DATA_DIR / "teacher_department.csv"

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"CSV file not found at: {csv_path}"))
            return

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            created, skipped, errors = 0, 0, []

            for row in reader:
                email = row.get("email", "").strip().lower()
                department_code = row.get("department_code", "").strip().upper()
                academic_year_name = row.get("academic_year", "").strip()

                try:
                    user = User.objects.get(email=email)
                    teacher = Teacher.objects.get(user=user)
                    department = Department.objects.get(code=department_code)

                    academic_year = None
                    if academic_year_name:
                        academic_year = AcademicYear.objects.get(name=academic_year_name)

                    enrollment, was_created = TeacherDepartmentEnrollment.objects.get_or_create(
                        teacher=teacher,
                        department=department,
                        academic_year=academic_year,
                        defaults={"date_assigned": now()}
                    )

                    if was_created:
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"Enrolled: {teacher} → {department}"))
                    else:
                        skipped += 1
                        self.stdout.write(f"Skipped (already exists): {teacher} → {department}")

                except User.DoesNotExist:
                    error_msg = f"❌ User with email '{email}' not found."
                    self.stderr.write(self.style.ERROR(error_msg))
                    errors.append(error_msg)
                except Teacher.DoesNotExist:
                    error_msg = f"❌ No Teacher found for user with email '{email}'."
                    self.stderr.write(self.style.ERROR(error_msg))
                    errors.append(error_msg)
                except Department.DoesNotExist:
                    error_msg = f"❌ Department with code '{department_code}' not found."
                    self.stderr.write(self.style.ERROR(error_msg))
                    errors.append(error_msg)
                except AcademicYear.DoesNotExist:
                    error_msg = f"❌ Academic Year '{academic_year_name}' not found."
                    self.stderr.write(self.style.ERROR(error_msg))
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"❌ Error processing row {row}: {str(e)}"
                    self.stderr.write(self.style.ERROR(error_msg))
                    errors.append(error_msg)

            self.stdout.write(self.style.SUCCESS(f"\n✅ Created: {created}"))
            self.stdout.write(f"⚠️ Skipped (existing): {skipped}")
            if errors:
                self.stdout.write(self.style.WARNING(f"🚨 Errors: {len(errors)} (check above)"))
