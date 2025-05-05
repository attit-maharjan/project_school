from decimal import Decimal, ROUND_HALF_UP
import random
from django.core.management.base import BaseCommand
from exams.models import StudentMark

# ============================================================
# 🧠 Command: populate_student_scores
# ------------------------------------------------------------
# Fills empty student scores with a random number between 23–99
# and re-triggers grading logic via .save().
# ============================================================



class Command(BaseCommand):
    help = "Assign random scores (23–99) to all StudentMark entries without scores."

    def handle(self, *args, **kwargs):
        marks = StudentMark.objects.filter(score__isnull=True)
        count = marks.count()

        if count == 0:
            self.stdout.write("🎯 All student marks already have scores.")
            return

        for mark in marks:
            # Use Decimal with 2 decimal precision
            raw_score = Decimal(str(random.uniform(23, 99))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            mark.score = raw_score
            mark.save()

        self.stdout.write(self.style.SUCCESS(f"✅ Populated scores for {count} student marks."))
