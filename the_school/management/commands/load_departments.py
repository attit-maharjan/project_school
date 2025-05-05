import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from the_school.models import Department
from users.models import User, Teacher


class Command(BaseCommand):
    help = "Import departments from CSV file."

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'csv', 'department.csv')

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"❌ File not found: {file_path}"))
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                code = row.get("code", "").strip()
                name = row.get("name", "").strip()
                description = row.get("description", "").strip()
                hod_email = row.get("hod", "").strip()
                is_active = row.get("is_active", "True").strip().lower() in ["true", "1", "yes"]

                teacher = None
                full_name = None

                if hod_email:
                    try:
                        user = User.objects.get(email=hod_email)
                        teacher = Teacher.objects.get(user=user)
                        full_name = f"{user.first_name} {user.last_name}"
                    except User.DoesNotExist:
                        self.stderr.write(self.style.WARNING(f"⚠ User not found for email: {hod_email}"))
                    except Teacher.DoesNotExist:
                        self.stderr.write(self.style.WARNING(f"⚠ No Teacher associated with email: {hod_email}"))

                department, created = Department.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'description': description or None,
                        'head_of_department': teacher,
                        'is_active': is_active
                    }
                )

                action = "✅ Created" if created else "🔁 Updated"
                log_msg = f"{action} department: {department}"

                if full_name:
                    log_msg += f" | HOD: {full_name} ({hod_email})"

                self.stdout.write(self.style.SUCCESS(log_msg))
                count += 1

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Import complete. {count} department(s) processed."))
