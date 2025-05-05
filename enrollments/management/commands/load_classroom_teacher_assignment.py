import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now

from users.models import User, Teacher
from the_school.models import ClassGroup, AcademicYear
from enrollments.models import ClassGroupTeacherAssignment


class Command(BaseCommand):
    help = "Import class group teacher assignments from a CSV file."

    def handle(self, *args, **options):
        csv_path = settings.CSV_DATA_DIR / "classroom_teacher_assignment.csv"

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"❌ CSV file not found at: {csv_path}"))
            return

        created, updated, errors = 0, 0, []

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                email = row.get("email", "").strip().lower()
                classgroup_name = row.get("name", "").strip()
                academic_year_name = row.get("year", "").strip()

                try:
                    # Lookup teacher from user email
                    user = User.objects.get(email=email)
                    teacher = Teacher.objects.get(user=user)

                    # Enforce classroom teacher role
                    if teacher.teacher_role != "Classroom Teacher":
                        raise ValueError(f"❌ {teacher} is not a Classroom Teacher.")

                    # Lookup class group
                    class_group = ClassGroup.objects.get(name__iexact=classgroup_name)

                    # Lookup academic year
                    academic_year = AcademicYear.objects.get(name=academic_year_name)

                    # Create or update assignment
                    obj, created_flag = ClassGroupTeacherAssignment.objects.update_or_create(
                        teacher=teacher,
                        academic_year=academic_year,
                        defaults={
                            "class_group": class_group,
                            "is_active": True,
                            "date_assigned": now().date()
                        }
                    )

                    if created_flag:
                        created += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"[CREATED] {teacher} → {class_group} ({academic_year})"
                        ))
                    else:
                        updated += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"[UPDATED] {teacher} → {class_group} ({academic_year})"
                        ))

                except User.DoesNotExist:
                    msg = f"❌ User with email '{email}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except Teacher.DoesNotExist:
                    msg = f"❌ No Teacher profile found for '{email}'."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except ClassGroup.DoesNotExist:
                    msg = f"❌ ClassGroup '{classgroup_name}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except AcademicYear.DoesNotExist:
                    msg = f"❌ AcademicYear '{academic_year_name}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except ValueError as e:
                    errors.append(str(e))
                    self.stderr.write(self.style.ERROR(str(e)))
                except Exception as e:
                    msg = f"❌ Unexpected error on row {row}: {str(e)}"
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))

        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n✅ Created: {created}"))
        self.stdout.write(self.style.SUCCESS(f"🛠️ Updated: {updated}"))
        self.stdout.write(self.style.ERROR(f"🚨 Errors: {len(errors)}"))
