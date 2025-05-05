import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from the_school.models import Subject, Department, GradeLevel


class Command(BaseCommand):
    help = "Import subjects from CSV file."

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'csv', 'subjects.csv')

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"❌ File not found: {file_path}"))
            return

        count = 0
        with open(file_path, newline='', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get("name", "").strip()
                department_code = row.get("department_code", "").strip()
                grade_reference = row.get("grade_reference", "").strip()

                if not all([name, department_code, grade_reference]):
                    self.stderr.write(self.style.WARNING(
                        f"⚠ Missing required field(s) in row: {row}"
                    ))
                    continue

                try:
                    department = Department.objects.get(code=department_code)
                except Department.DoesNotExist:
                    self.stderr.write(self.style.WARNING(
                        f"⚠ Department not found: {department_code}"
                    ))
                    continue

                try:
                    grade_level = GradeLevel.objects.get(reference_code=grade_reference)
                except GradeLevel.DoesNotExist:
                    self.stderr.write(self.style.WARNING(
                        f"⚠ GradeLevel not found: {grade_reference}"
                    ))
                    continue

                # Create or update the Subject
                subject, created = Subject.objects.update_or_create(
                    name=name,
                    department=department,
                    grade_level=grade_level,
                    defaults={},  # Let clean() handle the code generation
                )

                action = "✅ Created" if created else "🔁 Updated"
                self.stdout.write(self.style.SUCCESS(
                    f"{action} subject: {subject.name} ({subject.code})"
                ))
                count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Import complete. {count} subject(s) processed."
        ))
