import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import User, Parent


class Command(BaseCommand):
    help = "Upload alternative phone numbers for parents from parent_alternative_phone.csv"

    def handle(self, *args, **kwargs):
        csv_path = os.path.join(settings.BASE_DIR, "Data", "csv", "parent_alternative_phone.csv")

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        updated_count = 0
        skipped_count = 0

        with open(csv_path, newline='', encoding='iso-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                email = row.get("email")
                alt_phone = row.get("alternative_phone")

                if not email or not alt_phone:
                    self.stderr.write(self.style.WARNING(f"[SKIPPED] Missing data in row: {row}"))
                    skipped_count += 1
                    continue

                try:
                    user = User.objects.get(email=email.strip(), role='parent')
                    parent = Parent.objects.get(user=user)
                    parent.alternative_emergency_phone_number = alt_phone.strip()
                    parent.full_clean()
                    parent.save()

                    self.stdout.write(self.style.SUCCESS(
                        f"[UPDATED] {user.first_name} {user.last_name} ({email}) - Alternative phone updated."
                    ))
                    updated_count += 1

                except User.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"[ERROR] Parent user not found: {email}"))
                    skipped_count += 1
                except Parent.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"[ERROR] No Parent record linked to: {email}"))
                    skipped_count += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"[ERROR] Failed to update {email}: {e}"))
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nUpdate complete. Successfully updated: {updated_count}, Skipped: {skipped_count}"
        ))
