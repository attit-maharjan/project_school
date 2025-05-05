# ==========================================================
# 📦 Django Management Command to Import School Settings
# ==========================================================
import csv
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import ValidationError
from the_school.models import SchoolSettings

# -----------------------------------------
# 🛠 Command: load_school_info
# -----------------------------------------
class Command(BaseCommand):
    help = "🏫 Import school settings from school_info.csv"

    def handle(self, *args, **kwargs):
        csv_path = settings.CSV_DATA_DIR / "school_info.csv"

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"❌ File not found: {csv_path}"))
            return

        with open(csv_path, newline='', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile,)  # Tabs if you kept the original format

            for row in reader:
                try:
                    if SchoolSettings.objects.exists():
                        self.stdout.write(self.style.WARNING("⚠️ School settings already exist. Skipping creation."))
                        return

                    # Parse JSON string into a dictionary
                    social_links = row["social_media_links"].strip()
                    try:
                        social_links_dict = json.loads(social_links.replace("'", "\""))
                    except json.JSONDecodeError as e:
                        raise ValidationError(f"Invalid JSON in social_media_links: {social_links}")

                    settings_instance = SchoolSettings.objects.create(
                        singleton=row["singleton"].strip().lower() == "true",
                        school_name=row["school_name"].strip(),
                        school_motto=row["school_motto"].strip(),
                        established_year=int(row["established_year"].strip()),
                        address=row["address"].strip(),
                        contact_number=row["contact_number"].strip(),
                        email_address=row["email_address"].strip(),
                        website_url=row["website_url"].strip(),
                        social_media_links=social_links_dict,
                        homepage_intro=row["homepage_intro"].strip(),
                        about_us_title=row["about_us_title"].strip(),
                        about_us_subheading1=row["about_us_subheading1"].strip(),
                        about_us_paragraph1=row["about_us_paragraph1"].strip(),
                        about_us_paragraph2=row["about_us_paragraph2"].strip(),
                        about_us_subheading2=row["about_us_subheading2"].strip(),
                        about_us_paragraph3=row["about_us_paragraph3"].strip(),
                        contact_us_title=row["contact_us_title"].strip(),
                        contact_us_paragraph1=row["contact_us_paragraph1"].strip(),
                        contact_us_paragraph2=row["contact_us_paragraph2"].strip(),
                        privacy_policy=row["privacy_policy"].strip(),
                        terms_of_service=row["terms_of_service"].strip(),
                    )

                    self.stdout.write(self.style.SUCCESS(f"✅ [CREATED] {settings_instance.school_name}"))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ [ERROR] Could not import school settings"))
                    self.stderr.write(self.style.ERROR(str(e)))
