# ==========================================================
# 📦 Django Management Command to Import Accreditor Records
# ==========================================================
import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from the_school.models import Accreditor

# -----------------------------------------
# 🛠 Command: import_accreditors
# -----------------------------------------
class Command(BaseCommand):
    help = "📥 Import accrediting organizations from accreditor.csv"

    def handle(self, *args, **kwargs):
        # -----------------------------------------
        # 🔍 Locate CSV File
        # -----------------------------------------
        csv_path = settings.CSV_DATA_DIR / "accreditor.csv"

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"❌ File not found: {csv_path}"))
            return

        created_count = 0
        skipped_count = 0

        # -----------------------------------------
        # 📤 Open and Read CSV
        # -----------------------------------------
        with open(csv_path, newline='', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile,)  # Your file uses tabs

            for row in reader:
                # -----------------------------------------
                # 🧪 Validate Required Fields
                # -----------------------------------------
                required_fields = ["name", "registration_number", "website", "accreditation_date", "status"]
                if not all(row.get(field) for field in required_fields):
                    self.stderr.write(self.style.WARNING(f"⚠️ [SKIPPED] Missing required field in row: {row}"))
                    skipped_count += 1
                    continue

                name = row["name"].strip()
                reg_no = row["registration_number"].strip()

                # -----------------------------------------
                # 🚫 Skip Existing Records
                # -----------------------------------------
                if Accreditor.objects.filter(name=name).exists() or Accreditor.objects.filter(registration_number=reg_no).exists():
                    self.stdout.write(self.style.WARNING(f"❌ [SKIPPED] Accreditor already exists: {name}"))
                    skipped_count += 1
                    continue

                try:
                    # -----------------------------------------
                    # 📆 Parse Accreditation Date
                    # -----------------------------------------
                    date_obj = datetime.strptime(row["accreditation_date"].strip(), "%m/%d/%Y").date()

                    # -----------------------------------------
                    # ✅ Create Accreditor Record
                    # -----------------------------------------
                    accreditor = Accreditor.objects.create(
                        name=name,
                        registration_number=reg_no,
                        website=row["website"].strip(),
                        accreditation_date=date_obj,
                        status=row["status"].strip()
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ [CREATED] {accreditor}"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ [ERROR] Could not create accreditor: {name}"))
                    self.stderr.write(self.style.ERROR(str(e)))
                    skipped_count += 1

        # -----------------------------------------
        # 🧾 Summary Output
        # -----------------------------------------
        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Import completed. Created: {created_count}, Skipped: {skipped_count}"
        ))
