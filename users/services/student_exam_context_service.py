# Path: BIVGS > users app > services/student_exam_context_service.py

# 📦 Import necessary services and models
from users.services.exam_analytics_and_reports_service import (
    calculate_gpa_and_grade,  # GPA & grade calculator
    ExamAnalyticsAndReportsService,
)
from users.helpers.generate_chart_images import generate_report_chart_images          # Chart generator for PDF
from users.helpers.comment_generation import generate_subject_comments                # Subject-based comment logic
from exams.models import (
    StudentMark, # Student mark model
    GradeRange,
)


import json
from collections import Counter
from django.db.models import Avg
from django.utils.safestring import mark_safe
from the_school.models import AcademicYear
from enrollments.models import ClassGroupTeacherAssignment, ClassGroupStudentEnrollment
from exams.helpers.grade_calculation import get_overall_grade_from_points
from users.services.student_dashboard_service import get_student_dashboard_summary

from users.helpers.generate_chart_images import generate_grade_distribution_charts

# ------------------------------------------------------
# 🔁 Helper: Enrich marks with class avg + grades list
# ------------------------------------------------------
def _get_enriched_marks(student):
    active_year = AcademicYear.objects.get(is_current=True)
    marks = StudentMark.objects.select_related(
        'exam', 'exam__subject', 'exam__class_group', 'exam__exam_type', 'exam__academic_year'
    ).filter(student=student, exam__academic_year=active_year)

    enriched = []

    for mark in marks:
        exam = mark.exam
        class_avg = StudentMark.objects.filter(exam=exam).aggregate(avg=Avg("score"))['avg'] or 0
        class_grades = list(StudentMark.objects.filter(exam=exam).values_list("grade", flat=True))

        # 🔍 Pull GPA points if available
        points = None
        if exam.grading_scale:
            try:
                grade_obj = exam.grading_scale.grade_ranges.get(letter=mark.grade)
                points = float(grade_obj.points)
            except GradeRange.DoesNotExist:
                pass

        enriched.append({
            "score": float(mark.score),
            "grade": mark.grade,
            "exam": {
                "title": exam.title,
                "exam_code": exam.exam_code,
                "subject": exam.subject.name,
                "exam_type": exam.exam_type.name,
                "date_conducted": exam.date_conducted,
                "max_marks": exam.max_marks,
                "class_group": exam.class_group.name,
                "academic_year": exam.academic_year.name,
                "class_avg": round(class_avg, 2),
                "class_grades": class_grades,
                "points": points,
                "grading_scale": exam.grading_scale
            }
        })

    return enriched

# ------------------------------------------------------
# 📄 Exam Summary Context
# ------------------------------------------------------
def get_exam_summary_context(student):
    service = ExamAnalyticsAndReportsService(student, _get_enriched_marks(student))
    return {"summary": service.generate_exam_summary()}

# ------------------------------------------------------
# 📊 Performance Charts Context
# ------------------------------------------------------
def get_exam_performance_context(student):
    active_year = AcademicYear.objects.get(is_current=True)
    student_marks = StudentMark.objects.filter(student=student, exam__academic_year=active_year).select_related("exam")

    enriched = _get_enriched_marks(student)
    service = ExamAnalyticsAndReportsService(student, enriched)
    data = service.get_exam_performance_chart_data()

    labels = [mark.exam.exam_code for mark in student_marks]
    code_title_map = {mark.exam.exam_code: mark.exam.title for mark in student_marks}

    return {
        "labels": mark_safe(json.dumps(labels)),
        "student_scores": mark_safe(json.dumps([float(s) for s in data["line_chart_data"]["student_scores"]])),
        "class_avg_scores": mark_safe(json.dumps([float(s) for s in data["line_chart_data"]["class_avg_scores"]])),
        "code_title_map": code_title_map,
        "exam_code_map_js": mark_safe(json.dumps(code_title_map)),
        "academic_year": student_marks[0].exam.academic_year.name if student_marks else "",
        "class_group": student_marks[0].exam.class_group.name if student_marks else "",
    }

# ------------------------------------------------------
# 📈 Grade Insights Context
# ------------------------------------------------------
def get_exam_insights_context(student):
    active_year = AcademicYear.objects.get(is_current=True)
    student_marks = StudentMark.objects.filter(student=student, exam__academic_year=active_year).select_related("exam", "exam__class_group")

    if not student_marks.exists():
        return {"no_data": True, "academic_year": active_year.name, "class_group": "N/A"}

    enriched = _get_enriched_marks(student)
    service = ExamAnalyticsAndReportsService(student, enriched)
    insights = service.get_grade_insights()

    chart_data = []
    for item in insights:
        sorted_grades = sorted(item["grade_distribution"].items())
        chart_data.append({
            "exam_title": item["exam_title"],
            "student_grade": item["student_grade"],
            "labels": [g for g, _ in sorted_grades],
            "values": [c for _, c in sorted_grades],
        })

    return {
        "insight_charts": mark_safe(json.dumps(chart_data)),
        "raw_data": chart_data,
        "academic_year": active_year.name,
        "class_group": student_marks[0].exam.class_group.name,
    }

# ------------------------------------------------------
# 🧾 Report Card Context
# ------------------------------------------------------
# ------------------------------------------------------
# 🧾 Report Card Context
# ------------------------------------------------------
def get_exam_report_card_context(student):
    enriched_marks = _get_enriched_marks(student)
    service = ExamAnalyticsAndReportsService(student, enriched_marks)
    dashboard = get_student_dashboard_summary(student)

    # Fetch class group using the enrollment model (if it's not directly on the Student model)
    try:
        class_group = student.class_group  # Directly if class_group exists
    except AttributeError:
        # Access via enrollment if class_group is indirect
        enrollment = ClassGroupStudentEnrollment.objects.get(student=student)
        class_group = enrollment.class_group

    # Retrieve ClassGroupTeacherAssignment to get the class teacher
    classgroup_teacher = None
    try:
        classgroup_teacher = ClassGroupTeacherAssignment.objects.get(
            class_group=class_group,
            teacher__teacher_role='Classroom Teacher',
            is_active=True
        ).teacher
    except ClassGroupTeacherAssignment.DoesNotExist:
        classgroup_teacher = None  # In case there's no classroom teacher assignment

    report_card = service.build_report_card()

    # Generate base64 chart images for PDF only
    report_chart_images = generate_grade_distribution_charts(report_card)
    report_charts = []
    for entry in report_card:
        sorted_grades = sorted(entry["grade_distribution"].items())
        report_charts.append({
            "exam_title": entry["exam_title"],
            "student_grade": entry["grade"],
            "labels": [g for g, _ in sorted_grades],
            "values": [c for _, c in sorted_grades],
        })

    return {
        "report_card": report_card,
        "report_charts": report_charts,
        "report_chart_images": report_chart_images,
        "overall": get_overall_grade_from_points(StudentMark.objects.filter(student=student, exam__academic_year__is_current=True)),
        "academic_year": dashboard["classgroup"].academic_year.name if dashboard["classgroup"] else "N/A",
        "class_group": class_group.name if class_group else "N/A",
        "class_teacher_name": classgroup_teacher.user.get_full_name() if classgroup_teacher else "N/A",  # Added the teacher name
        "average_score": dashboard["average_score"]
    }



# ------------------------------------------------------
# 💬 Comments Context
# ------------------------------------------------------
def get_exam_comments_context(student):
    service = ExamAnalyticsAndReportsService(student, _get_enriched_marks(student))
    return {"comments": service.generate_subject_comments()}

