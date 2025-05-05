import random
from collections import defaultdict
from django.core.management.base import BaseCommand
from users.models import Student, Parent


class Command(BaseCommand):
    help = "Smartly assign parents to students based on matching last names and gender."

    def handle(self, *args, **options):
        # STEP 1: Collect all unassigned students
        students = list(Student.objects.filter(father__isnull=True, mother__isnull=True, guardian__isnull=True).select_related('user'))
        self.stdout.write(self.style.NOTICE(f"Found {len(students)} unassigned students."))

        # STEP 2: Collect all parents and group by last_name
        parents_by_last_name = defaultdict(list)
        parent_assignments = {}  # parent_id -> count of assigned students

        for parent in Parent.objects.select_related('user'):
            last_name = parent.user.last_name.strip().lower()
            parents_by_last_name[last_name].append(parent)
            parent_assignments[parent.id] = 0  # start with 0 assignments

        total_assigned = 0

        # STEP 3: First-pass: Assign by matching last name and gender
        students_by_last_name = defaultdict(list)
        for student in students:
            students_by_last_name[student.user.last_name.strip().lower()].append(student)

        for last_name, student_group in students_by_last_name.items():
            parent_group = parents_by_last_name.get(last_name, [])

            if not parent_group:
                continue

            # Shuffle both to ensure fair pairing
            random.shuffle(student_group)
            random.shuffle(parent_group)

            student_index = 0
            parent_index = 0

            while student_index < len(student_group) and parent_index < len(parent_group):
                student = student_group[student_index]
                parent = parent_group[parent_index]
                gender = parent.user.gender.lower()

                if gender == "male" and student.father is None:
                    student.father = parent
                elif gender == "female" and student.mother is None:
                    student.mother = parent
                else:
                    parent_index += 1
                    continue

                student.save()
                parent_assignments[parent.id] += 1
                total_assigned += 1
                self.stdout.write(self.style.SUCCESS(
                    f"[MATCHED] {student.user.get_full_name()} ← {gender.title()} {parent.user.get_full_name()}"
                ))
                student_index += 1
                parent_index += 1

        # STEP 4: Second-pass: Assign unassigned students to unassigned parents as guardians
        remaining_students = Student.objects.filter(father__isnull=True, mother__isnull=True, guardian__isnull=True).select_related('user')
        unassigned_parents = [
            p for p in Parent.objects.select_related('user')
            if parent_assignments[p.id] == 0
        ]
        random.shuffle(unassigned_parents)

        parent_pointer = 0
        for student in remaining_students:
            if parent_pointer >= len(unassigned_parents):
                self.stdout.write(self.style.WARNING(f"[WARNING] No more unassigned parents for {student.user.get_full_name()}"))
                continue

            guardian = unassigned_parents[parent_pointer]
            student.guardian = guardian
            student.save()
            parent_assignments[guardian.id] += 1
            parent_pointer += 1
            total_assigned += 1
            self.stdout.write(self.style.SUCCESS(
                f"[GUARDIAN ASSIGNED] {student.user.get_full_name()} ← Guardian {guardian.user.get_full_name()}"
            ))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Assignment completed. Total students assigned: {total_assigned}"))
