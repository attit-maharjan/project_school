from datetime import datetime
from django.core.management.base import BaseCommand
from enrollments.models import TeacherSubjectAssignment


class Command(BaseCommand):
    help = "Update all TeacherSubjectAssignments: set date_assigned to 2025-01-01"

    def handle(self, *args, **kwargs):
        target_date = datetime(2025, 1, 1).date()
        updated_count = 0

        assignments = TeacherSubjectAssignment.objects.all()

        for assignment in assignments:
            assignment.date_assigned = target_date
            assignment.save(update_fields=["date_assigned"])
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(
                f"[UPDATED] {assignment.teacher.user.email} → {assignment.subject.code} — Date assigned set to {target_date}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Successfully updated {updated_count} TeacherSubjectAssignment record(s)"
        ))
