import datetime
from django.core.management.base import BaseCommand
from exams.models import GradeScale, GradeRange, ExamType
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = "Populates initial grading data into GradeScale, GradeRange, and ExamType."

    def handle(self, *args, **kwargs):
        # 1. Create GradeScale
        scale_name = "CAPS 2024"
        scale_description = "Standard grading scale used for CAPS curriculum in 2024."

        scale, created = GradeScale.objects.get_or_create(
            name=scale_name,
            defaults={"description": scale_description}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created GradeScale: {scale.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ GradeScale '{scale.name}' already exists."))

        # 2. Populate GradeRanges for this scale (A to F)
        grade_ranges = [
            ("A", 80.00, 100.00, 4.0),
            ("B", 70.00, 79.99, 3.0),
            ("C", 60.00, 69.99, 2.0),
            ("D", 50.00, 59.99, 1.0),
            ("E", 40.00, 49.99, 0.5),
            ("F", 0.00, 39.99, 0.0),
        ]

        for letter, min_perc, max_perc, points in grade_ranges:
            gr, created = GradeRange.objects.get_or_create(
                scale=scale,
                letter=letter,
                defaults={
                    "min_percentage": min_perc,
                    "max_percentage": max_perc,
                    "points": points
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Added Grade {letter} to {scale.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Grade {letter} already exists in {scale.name}"))

        # 3. Create singleton ExamType
        try:
            exam_type = ExamType.objects.get()
            self.stdout.write(self.style.WARNING(f"⚠️ ExamType already exists: {exam_type}"))
        except ExamType.DoesNotExist:
            exam_type = ExamType.objects.create(name="Final Exam", weight=100.0)
            self.stdout.write(self.style.SUCCESS(f"✅ Created ExamType: {exam_type}"))
