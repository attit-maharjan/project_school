import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Upload and create users from all_users.csv"

    def handle(self, *args, **kwargs):
        # Local imports to avoid circular import error
        from users.models import User, Parent, Student, Teacher

        csv_path = settings.CSV_DATA_DIR / "all_users.csv"

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        created_count = 0
        skipped_count = 0

        with open(csv_path, newline='', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                email = row.get("email")
                if not email:
                    self.stderr.write(self.style.WARNING(f"[SKIPPED] Missing email in row: {row}"))
                    skipped_count += 1
                    continue

                if User.objects.filter(email=email).exists():
                    self.stdout.write(self.style.WARNING(f"[SKIPPED] User already exists: {email}"))
                    skipped_count += 1
                    continue

                try:
                    # Parse DOB
                    dob = datetime.strptime(row["dob"], "%m/%d/%Y").date()

                    # Handle Address Creation
                    street = row.get("street_address", "").strip()
                    city = row.get("city", "").strip()
                    state = row.get("state_province", "").strip()
                    postal = row.get("postal_code", "").strip()
                    country = row.get("country", "").strip()

                    # Create User with role
                    user = User.objects.create_user(
                        email=email.strip(),
                        password=row["password1"].strip(),  # Assuming password1 is the actual password field
                        first_name=row.get("first_name", "").strip(),
                        initials=row.get("initials", "").strip(),
                        last_name=row.get("last_name", "").strip(),
                        phone_number=row.get("phone", "").strip(),
                        dob=dob,
                        gender=row.get("gender", "").lower(),
                        role=row.get("role", "student").lower(),  # Default role is "student"
                        street_address=street,  # Address fields as part of the user model
                        city=city,
                        state_province=state,
                        postal_code=postal,
                        country=country,
                    )

                    # Assign parent roles if the user is a parent
                    if user.role == "parent":
                        Parent.objects.create(user=user)
                        self.stdout.write(self.style.SUCCESS(
                            f"[CREATED] {user.first_name} {user.last_name} ({email}) - Parent"
                        ))

                    # If the role is student, create student record
                    elif user.role == "student":
                        student = Student.objects.create(user=user)
                        self.stdout.write(self.style.SUCCESS(
                            f"[CREATED] {user.first_name} {user.last_name} ({email}) - Student"
                        ))

                    # If the role is teacher, create teacher record
                    elif user.role == "teacher":
                        teacher = Teacher.objects.create(user=user)
                        self.stdout.write(self.style.SUCCESS(
                            f"[CREATED] {user.first_name} {user.last_name} ({email}) - Teacher"
                        ))

                    created_count += 1

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"[ERROR] Could not process row: {row}"))
                    self.stderr.write(self.style.ERROR(str(e)))
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nImport finished. Successfully created: {created_count}, Skipped: {skipped_count}"
        ))
