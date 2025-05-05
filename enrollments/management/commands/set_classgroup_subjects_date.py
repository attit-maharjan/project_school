from datetime import date
from django.core.management.base import BaseCommand
from enrollments.models import ClassGroupSubjectAssignment


class Command(BaseCommand):
    help = "Update all ClassGroupSubjectAssignment records to have date_assigned set to 2025-01-01."

    def handle(self, *args, **options):
        target_date = date(2025, 1, 1)
        updated_count = 0

        assignments = ClassGroupSubjectAssignment.objects.all()

        for assignment in assignments:
            assignment.date_assigned = target_date
            assignment.save()
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(
                f"[UPDATED] {assignment.class_group} → {assignment.subject} → {assignment.academic_year} set to {target_date}"
            ))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully updated {updated_count} class group subject assignments."))
