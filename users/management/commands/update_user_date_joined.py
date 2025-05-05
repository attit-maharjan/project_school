import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from users.models import User, Teacher

class Command(BaseCommand):
    help = "Update `date_joined` for all users randomly between 2025-01-01 and 2025-01-03, except teachers who will have 2024-12-31"

    def handle(self, *args, **kwargs):
        # Define the date ranges
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 3)
        teacher_date = datetime(2024, 12, 31)

        # Fetch all users and update the `date_joined`
        users = User.objects.all()
        updated_count = 0

        for user in users:
            if user.role == 'teacher':
                user.date_joined = teacher_date
                self.stdout.write(self.style.SUCCESS(f"Updated {user.email} to {teacher_date}"))
            else:
                random_date = start_date + timedelta(
                    seconds=random.randint(0, int((end_date - start_date).total_seconds()))
                )
                user.date_joined = random_date
                self.stdout.write(self.style.SUCCESS(f"Updated {user.email} to {random_date}"))

            # Save the user after updating
            user.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully updated {updated_count} users"))
