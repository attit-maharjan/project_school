# ========================================================
# 🔄 Sync Enrollment Dates and Created Timestamps
# ========================================================
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from enrollments.models import ClassGroupStudentEnrollment


class Command(BaseCommand):
    help = "🔄 Sync enrollment_date and created_at for each record (Jan 5–9, 2025 window)"

    def handle(self, *args, **kwargs):
        base_date = datetime(2025, 1, 5)
        date_range = [base_date + timedelta(days=i) for i in range(5)]
        updated_count = 0

        enrollments = ClassGroupStudentEnrollment.objects.select_related("student").all()

        for enrollment in enrollments:
            # 🎲 Use student ID to make the randomness deterministic
            assigned_date = random.Random(enrollment.student.id).choice(date_range)

            enrollment.enrollment_date = assigned_date.date()
            enrollment.created_at = assigned_date
            enrollment.save(update_fields=["enrollment_date", "created_at"])
            updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ Updated {enrollment.student} to {assigned_date.date()}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Done. Synced enrollment dates for {updated_count} records."
        ))
