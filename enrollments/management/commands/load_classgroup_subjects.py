import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now

from the_school.models import Subject, ClassGroup, AcademicYear
from enrollments.models import ClassGroupSubjectAssignment


class Command(BaseCommand):
    help = "Import class group subject assignments from a CSV file."

    def handle(self, *args, **options):
        csv_path = settings.CSV_DATA_DIR / "classgroup_subjects_assignment.csv"

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"❌ CSV file not found at: {csv_path}"))
            return

        created, updated, errors = 0, 0, []

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                class_group_name = row.get("class_group", "").strip()
                subject_code = row.get("Subject_Code", "").strip().upper()
                academic_year_name = row.get("year", "").strip()
                is_active_raw = row.get("is_active", "True").strip().lower()
                is_active = is_active_raw in ["1", "true", "yes"]

                try:
                    subject = Subject.objects.get(code=subject_code)
                    class_group = ClassGroup.objects.get(name=class_group_name)
                    academic_year = AcademicYear.objects.get(name=academic_year_name)

                    obj, created_flag = ClassGroupSubjectAssignment.objects.update_or_create(
                        class_group=class_group,
                        subject=subject,
                        academic_year=academic_year,
                        defaults={
                            "is_active": is_active,
                            "date_assigned": now().date()
                        }
                    )

                    if created_flag:
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f"[CREATED] {class_group} → {subject} ({academic_year})"))
                    else:
                        updated += 1
                        self.stdout.write(self.style.SUCCESS(f"[UPDATED] {class_group} → {subject} ({academic_year})"))

                except Subject.DoesNotExist:
                    msg = f"❌ Subject with code '{subject_code}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except ClassGroup.DoesNotExist:
                    msg = f"❌ Class group '{class_group_name}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except AcademicYear.DoesNotExist:
                    msg = f"❌ Academic year '{academic_year_name}' not found."
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))
                except Exception as e:
                    msg = f"❌ Unexpected error: {str(e)} on row: {row}"
                    errors.append(msg)
                    self.stderr.write(self.style.ERROR(msg))

        # ✅ Summary
        self.stdout.write(self.style.SUCCESS(f"\n✅ Created: {created}"))
        self.stdout.write(self.style.SUCCESS(f"🛠️ Updated: {updated}"))
        self.stdout.write(self.style.ERROR(f"🚨 Errors: {len(errors)}"))
