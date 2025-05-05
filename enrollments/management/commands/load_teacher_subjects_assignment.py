import csv
from datetime import date
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now

from users.models import User, Teacher
from the_school.models import Subject, AcademicYear
from enrollments.models import TeacherSubjectAssignment


class Command(BaseCommand):
    help = "Import teacher subject assignments from a CSV file using subject CODE."

    def handle(self, *args, **options):
        csv_path = settings.CSV_DATA_DIR / "teacher_subjects_assignment.csv"

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"❌ CSV file not found at: {csv_path}"))
            return

        created, updated, skipped, errors = 0, 0, 0, []

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                email = row.get("email", "").strip().lower()
                subject_code = row.get("Subject_Name", "").strip().upper()
                academic_year_name = row.get("year", "").strip()
                is_active_str = row.get("is_active", "True").strip().lower()

                try:
                    # Lookup user and teacher
                    user = User.objects.get(email=email)
                    teacher = Teacher.objects.get(user=user)

                    # Lookup subject using CODE, not name
                    subject = Subject.objects.get(code__iexact=subject_code)

                    # Optional academic year lookup
                    academic_year = None
                    if academic_year_name:
                        academic_year = AcademicYear.objects.get(name=academic_year_name)

                    # Clean boolean parsing
                    is_active = is_active_str in ['1', 'true', 'yes']

                    # Create or update assignment
                    obj, created_flag = TeacherSubjectAssignment.objects.update_or_create(
                        teacher=teacher,
                        academic_year=academic_year,
                        defaults={
                            "subject": subject,
                            "is_active": is_active,
                            "date_assigned": now().date()
                        }
                    )

                    if created_flag:
                        created += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"[CREATED] {teacher} → {subject.code} ({academic_year or 'Permanent'})"
                        ))
                    else:
                        updated += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"[UPDATED] {teacher} → {subject.code} ({academic_year or 'Permanent'})"
                        ))

                except User.DoesNotExist:
                    msg = f"❌ User with email '{email}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except Teacher.DoesNotExist:
                    msg = f"❌ No teacher found for user '{email}'."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except Subject.DoesNotExist:
                    msg = f"❌ Subject with code '{subject_code}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except AcademicYear.DoesNotExist:
                    msg = f"❌ Academic year '{academic_year_name}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except Exception as e:
                    msg = f"❌ Unexpected error on row {row}: {str(e)}"
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))

        # Final report
        self.stdout.write(self.style.SUCCESS(f"\n✅ Created: {created}"))
        self.stdout.write(self.style.SUCCESS(f"🛠️ Updated: {updated}"))
        self.stdout.write(self.style.WARNING(f"⚠️ Skipped: {skipped}"))
        self.stdout.write(self.style.ERROR(f"🚨 Errors: {len(errors)}"))
