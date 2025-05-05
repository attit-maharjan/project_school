from django.core.management.base import BaseCommand
from django.utils import timezone
from django.apps import apps

from exams.models import Exam, ExamType, GradeScale
from the_school.models import AcademicYear
from enrollments.models import ClassGroupSubjectAssignment


# ============================================================
# 🛠️ Command: populate_all_exams
# ============================================================
# Populates exams for each subject assigned to a class group
# in the current academic year. Designed for bulk seeding.
#
# 🔒 Avoids duplicates using get_or_create
# 📘 Uses grading scale "CAPS 2024"
# 📧 Admin email defaults to sales@walsoftcomputers.com
# ============================================================

class Command(BaseCommand):
    help = "Auto-generate exam records for every class group subject assignment."

    def handle(self, *args, **options):
        # ✅ Step 1: Get active academic year
        try:
            current_year = AcademicYear.objects.get(is_current=True)
        except AcademicYear.DoesNotExist:
            self.stderr.write("❌ No active academic year found.")
            return

        # ✅ Step 2: Get grading scale
        try:
            grading_scale = GradeScale.objects.get(name="CAPS 2024")
        except GradeScale.DoesNotExist:
            self.stderr.write("❌ Grading scale 'CAPS 2024' not found.")
            return

        # ✅ Step 3: Get default exam type (assumes singleton)
        try:
            default_exam_type = ExamType.objects.get()
        except ExamType.DoesNotExist:
            self.stderr.write("❌ No exam type exists. Please create one.")
            return

        # ✅ Step 4: Loop through all subject assignments
        assignments = ClassGroupSubjectAssignment.objects.filter(
            academic_year=current_year,
            is_active=True
        )

        created_count = 0
        skipped_count = 0

        for assignment in assignments:
            subject = assignment.subject
            class_group = assignment.class_group

            # ✅ Attempt to assign the subject teacher
            TeacherSubjectAssignment = apps.get_model('enrollments', 'TeacherSubjectAssignment')
            teacher_assignment = TeacherSubjectAssignment.objects.filter(
                subject=subject,
                academic_year=current_year,
                is_active=True
            ).first()

            created_by = teacher_assignment.teacher if teacher_assignment else None

            if not created_by:
                self.stdout.write(f"⚠️ Skipped: No teacher assigned to {subject} ({class_group})")
                skipped_count += 1
                continue

            # ✅ Create the exam record (if not exists)
            exam, created = Exam.objects.get_or_create(
                subject=subject,
                class_group=class_group,
                academic_year=current_year,
                exam_type=default_exam_type,
                defaults={
                    'title': f"{subject.name} Exam",
                    'created_by': created_by,
                    'date_conducted': timezone.now(),
                    'max_marks': 100,
                    'grading_scale': grading_scale,
                    'admin_emails': 'sales@walsoftcomputers.com'
                }
            )

            if created:
                self.stdout.write(f"✅ Created Exam: {exam.title} ({class_group})")
                created_count += 1
            else:
                self.stdout.write(f"🟡 Skipped (Exists): {exam.title} ({class_group})")
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n✅ Done! Created: {created_count}, Skipped: {skipped_count}"))
