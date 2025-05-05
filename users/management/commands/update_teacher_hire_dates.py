from datetime import datetime
from django.core.management.base import BaseCommand
from users.models import User, Teacher

class Command(BaseCommand):
    help = "Update teachers: set date_joined and hire_date to 2025-01-01"

    def handle(self, *args, **kwargs):
        target_date = datetime(2025, 1, 1)
        updated_count = 0

        teachers = Teacher.objects.select_related('user')

        for teacher in teachers:
            user = teacher.user
            user.date_joined = target_date
            user.save()

            teacher.hire_date = target_date
            teacher.save()

            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f"[UPDATED] {user.email} - date_joined & hire_date set to {target_date.date()}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully updated {updated_count} teacher(s)"))
