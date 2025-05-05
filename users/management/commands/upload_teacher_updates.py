import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import User, Teacher


class Command(BaseCommand):
    help = "Update teacher role and salary from update_teacher.csv"

    def handle(self, *args, **kwargs):
        csv_path = os.path.join(settings.BASE_DIR, "Data", "csv", "update_teacher.csv")

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        updated_count = 0
        skipped_count = 0

        with open(csv_path, newline='', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                email = row.get("email")
                role = row.get("teacher_role")
                salary = row.get("salary")

                if not email or not role or not salary:
                    self.stderr.write(self.style.WARNING(f"[SKIPPED] Missing data in row: {row}"))
                    skipped_count += 1
                    continue

                try:
                    user = User.objects.get(email=email.strip(), role="teacher")
                    teacher = Teacher.objects.get(user=user)

                    teacher.teacher_role = role.strip()
                    teacher.salary = float(salary.strip())
                    teacher.full_clean()
                    teacher.save()

                    self.stdout.write(self.style.SUCCESS(
                        f"[UPDATED] {user.first_name} {user.last_name} ({email}) — Role: {role}, Salary: {salary}"
                    ))
                    updated_count += 1

                except User.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"[ERROR] Teacher user not found: {email}"))
                    skipped_count += 1
                except Teacher.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"[ERROR] No Teacher record linked to: {email}"))
                    skipped_count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"[ERROR] Failed to update {email}: {e}"))
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nUpdate complete. Successfully updated: {updated_count}, Skipped: {skipped_count}"
        ))
