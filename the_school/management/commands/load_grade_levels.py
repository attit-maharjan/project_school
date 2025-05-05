import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from the_school.models import GradeLevel


class Command(BaseCommand):
    help = "Load grade levels from CSV file."

    def handle(self, *args, **kwargs):
        # -----------------------------
        # 📄 Locate the CSV file
        # -----------------------------
        file_path = os.path.join(settings.BASE_DIR, 'data', 'csv', 'grade_level.csv')

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"❌ File not found: {file_path}"))
            return

        count = 0

        # -----------------------------
        # 📥 Read and parse the CSV
        # -----------------------------
        with open(file_path, newline='', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # 🚫 Skip empty rows
                if not any(row.values()):
                    continue

                try:
                    # -----------------------------
                    # 🧾 Extract and clean data
                    # -----------------------------
                    grade_number = int(row.get("grade_number", "").strip())
                    year_level = int(row.get("year_level", "").strip())
                    reference_code = row.get("reference_code", "").strip()
                    display_name = row.get("display_name", "").strip()

                    # -----------------------------
                    # 💾 Create or update entry
                    # -----------------------------
                    grade_level, created = GradeLevel.objects.update_or_create(
                        grade_number=grade_number,
                        defaults={
                            'year_level': year_level,
                            'reference_code': reference_code,
                            'display_name': display_name
                        }
                    )

                    action = "✅ Created" if created else "🔁 Updated"
                    self.stdout.write(self.style.SUCCESS(
                        f"{action} grade level: {grade_level.display_name} ({grade_level.reference_code})"
                    ))
                    count += 1

                except Exception as e:
                    self.stderr.write(self.style.WARNING(f"⚠ Failed to process row: {row} — {e}"))

        # -----------------------------
        # 🎉 Completion message
        # -----------------------------
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Import complete. {count} grade level(s) processed."))
