# Path: BIVGS > users/services/student_dashboard_service.py
# 
# ============================================================
# 📚 Student Dashboard Services
# ============================================================
# Purpose:
# - Handle all basic student dashboard data retrieval.
# ============================================================

from enrollments.models import ClassGroupStudentEnrollment, ClassGroupSubjectAssignment, TeacherSubjectAssignment 
from enrollments.models import ClassGroupStudentEnrollment
from exams.models import StudentMark, Exam
from django.db.models import Avg
from django.db.models import Prefetch  # 🆕 Optimization
from datetime import date


# ============================================================
# 📚 Student Dashboard Summary Service
# ============================================================

def get_student_dashboard_summary(student):
    """
    Returns the student dashboard summary context dictionary containing:
    - Current active class group
    - Average exam score
    - Total distinct subjects enrolled
    - List of exam labels (subject codes) for chart display
    - List of exam scores (numerical) for chart display
    - Mapping of subject code → subject full name
    """

    # 1️⃣ Fetch the student's active enrollment (their current class group)
    enrollment = ClassGroupStudentEnrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('class_group').first()

    # 2️⃣ Fetch all valid marks (ignore NULL scores safely)
    marks = StudentMark.objects.filter(
        student=student
    ).select_related(
        'exam__subject'
    ).order_by(
        'exam__date_conducted'
    )

    # 🛡️ Defensive check: Empty marks = empty lists
    if not marks.exists():
        return {
            "classgroup": enrollment.class_group if enrollment else None,
            "average_score": 0.0,
            "subjects_count": 0,
            "exam_labels": [],
            "exam_scores": [],
            "subject_code_name_map": {},
        }

    # 3️⃣ Prepare lists for performance chart
    exam_labels = []
    exam_scores = []
    subject_code_name_map = {}

    for mark in marks:
        # Some exams might be misconfigured — defensive
        if not mark.exam or not mark.exam.subject:
            continue

        subject_code = mark.exam.subject.code
        subject_name = mark.exam.subject.name

        # If score is None, treat it as 0
        score = float(mark.score) if mark.score is not None else 0.0

        exam_labels.append(subject_code)
        exam_scores.append(score)

        # Build the subject mapping dictionary
        if subject_code not in subject_code_name_map:
            subject_code_name_map[subject_code] = subject_name

    # 4️⃣ Calculate the student's overall average score
    average_score_raw = marks.aggregate(avg_score=Avg('score'))['avg_score']
    average_score = round(average_score_raw or 0, 2)

    # 5️⃣ Count distinct subjects the student has taken exams for
    subjects_count = marks.values('exam__subject').distinct().count()

    # 6️⃣ Final context dictionary returned to the view
    return {
        "classgroup": enrollment.class_group if enrollment else None,
        "average_score": average_score,
        "subjects_count": subjects_count,
        "exam_labels": exam_labels,
        "exam_scores": exam_scores,
        "subject_code_name_map": subject_code_name_map,
    }




# ============================================================
# 📚 Student Subjects Service
# ============================================================
# Purpose:
# - Fetch all subjects the student is enrolled in via their class group.
# - Fetch assigned teacher from TeacherSubjectAssignment based on subject.
# - Include subject details + teacher details + academic year.
# ============================================================


def get_student_subjects(student):
    """
    Fetches all active subjects assigned to the student's current class group,
    including subject details, assigned teacher (from subject assignment), and academic year.

    Args:
        student (Student): The logged-in student instance.

    Returns:
        Dict: Dictionary containing academic year and list of subject dictionaries.
    """

    # Step 1️⃣: Find the student's active enrollment
    enrollment = ClassGroupStudentEnrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('class_group', 'class_group__academic_year').first()

    if not enrollment:
        return {
            "academic_year": None,
            "subjects": []
        }

    # Step 2️⃣: Extract the academic year name
    academic_year = enrollment.class_group.academic_year.name if enrollment.class_group and enrollment.class_group.academic_year else None

    # Step 3️⃣: Fetch active subject assignments for the class group
    subject_assignments = ClassGroupSubjectAssignment.objects.filter(
        class_group=enrollment.class_group,
        is_active=True
    ).select_related('subject', 'subject__department')

    # Step 4️⃣: Prepare subject list with assigned teachers
    subjects = []
    for assignment in subject_assignments:
        subject = assignment.subject

        # 🧠 Find teacher assigned to this subject (global or scoped to year)
        teacher_assignment = TeacherSubjectAssignment.objects.filter(
            subject=subject,
            is_active=True
        ).select_related('teacher').first()

        teacher_name = teacher_assignment.teacher.user.get_full_name() if teacher_assignment and teacher_assignment.teacher else None
        teacher_email = teacher_assignment.teacher.user.email if teacher_assignment and teacher_assignment.teacher else None

        subjects.append({
            "name": subject.name,
            "code": subject.code,
            "department": subject.department.name if subject.department else None,
            "teacher_name": teacher_name,
            "teacher_email": teacher_email,
        })

    # Step 5️⃣: Final structured return
    return {
        "academic_year": academic_year,
        "subjects": subjects
    }



# ============================================================
# 📚 Student Exam Schedule Service
# ============================================================
# Purpose:
# - Fetch all upcoming and completed exams for the student's class group.
# - Show subject, teacher, and exam metadata properly.
# ============================================================

def get_student_exam_schedule(student):
    """
    Returns a dictionary containing:
    - Current academic year
    - Current class group
    - List of exams with relevant info
    """

    # Step 1️⃣: Find active enrollment
    enrollment = ClassGroupStudentEnrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('class_group', 'class_group__academic_year').first()

    if not enrollment:
        return {
            "academic_year": None,
            "class_group": None,
            "exams": []
        }

    academic_year = enrollment.class_group.academic_year.name if enrollment.class_group and enrollment.class_group.academic_year else None
    class_group_name = enrollment.class_group.name if enrollment.class_group else None

    # Step 2️⃣: Fetch all exams linked to the class group and year
    exams = Exam.objects.filter(
        class_group=enrollment.class_group,
        academic_year=enrollment.class_group.academic_year
    ).select_related('subject', 'created_by').order_by('date_conducted')

    # Step 3️⃣: Prepare the exam data
    exam_list = []
    for exam in exams:
        teacher = exam.created_by  # 'created_by' is linked to Teacher model
        teacher_name = teacher.user.get_full_name() if teacher and hasattr(teacher, 'user') else None
        teacher_email = teacher.user.email if teacher and hasattr(teacher, 'user') else None

        exam_list.append({
            "exam_code": exam.exam_code,
            "exam_name": exam.title,
            "teacher_name": teacher_name,
            "teacher_email": teacher_email,
            "date_conducted": exam.date_conducted,
            "status": "Done" if exam.date_conducted <= date.today() else "Upcoming",
        })

    # Step 4️⃣: Final structured context
    return {
        "academic_year": academic_year,
        "class_group": class_group_name,
        "exams": exam_list
    }
