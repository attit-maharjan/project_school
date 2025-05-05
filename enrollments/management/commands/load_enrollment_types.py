# ==========================================================
# 📦 Django Management Command to Import Enrollment Types
# ==========================================================
import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from enrollments.models import StudentEnrollmentType

# -----------------------------------------
# 🛠 Command: import_enrollment_types
# -----------------------------------------
class Command(BaseCommand):
    help = "📥 Import student enrollment types from enrollment_types.csv"

    def handle(self, *args, **kwargs):
        # -----------------------------------------
        # 🔍 Locate CSV File
        # -----------------------------------------
        csv_path = settings.CSV_DATA_DIR / "enrollment_types.csv"

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"❌ File not found: {csv_path}"))
            return

        created_count = 0
        skipped_count = 0

        # -----------------------------------------
        # 📤 Open and Read CSV
        # -----------------------------------------
        with open(csv_path, newline='', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # -----------------------------------------
                # 🧪 Validate Required Fields
                # -----------------------------------------
                required_fields = ["Code", "Name"]
                if not all(row.get(field) for field in required_fields):
                    self.stderr.write(self.style.WARNING(f"⚠️ [SKIPPED] Missing required field(s): {row}"))
                    skipped_count += 1
                    continue

                code = row["Code"].strip()
                name = row["Name"].strip()
                description = (row.get("Description") or "").strip()

                try:
                    # -----------------------------------------
                    # ✅ Create or Update Record
                    # -----------------------------------------
                    obj, created = StudentEnrollmentType.objects.update_or_create(
                        code=code,
                        defaults={"name": name, "description": description}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"✅ [CREATED] {obj}"))
                    else:
                        self.stdout.write(self.style.NOTICE(f"ℹ [UPDATED] {obj}"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ [ERROR] Failed to process {code} - {name}"))
                    self.stderr.write(self.style.ERROR(str(e)))
                    skipped_count += 1

        # -----------------------------------------
        # 🧾 Summary Output
        # -----------------------------------------
        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Import completed. Created: {created_count}, Skipped: {skipped_count}"
        ))
