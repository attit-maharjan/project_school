from datetime import datetime
from django.core.management.base import BaseCommand
from enrollments.models import TeacherDepartmentEnrollment

class Command(BaseCommand):
    help = "Update all TeacherDepartmentEnrollments: set date_assigned to 2025-01-01"

    def handle(self, *args, **kwargs):
        target_date = datetime(2025, 1, 1).date()
        updated_count = 0

        enrollments = TeacherDepartmentEnrollment.objects.all()

        for enrollment in enrollments:
            enrollment.date_assigned = target_date
            enrollment.save(update_fields=['date_assigned'])
            updated_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"[UPDATED] {enrollment.teacher.user.email} → {enrollment.department.name} ({enrollment.academic_year or 'Permanent'})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Successfully updated {updated_count} enrollment(s) to {target_date}")
        )
