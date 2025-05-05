# +++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 📊 Exam Analytics and Report Card Generation Service
# This module provides logic for building exam summaries,
# generating visual data, computing GPA, and rendering comments.
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ========== 🧾 Django & Standard Library Imports ==========
from collections import Counter
from django.db.models import Avg

# ========== 📦 Internal Helpers and Services ==========
from users.helpers.comment_generation import generate_intelligent_comment
from exams.models import GradeRange


# +++++++++++++++++++++++++++++++++++++++++++++
# 🧠 Exam Analytics Core Service Class
# +++++++++++++++++++++++++++++++++++++++++++++
class ExamAnalyticsAndReportsService:
    def __init__(self, student, student_marks):
        self.student = student                          # 🧑 The current student
        self.student_marks = student_marks              # 🧾 List of exam mark dicts

    # ---------------------------------------------
    # 📘 Generate summary of all exams taken
    # ---------------------------------------------
    def generate_exam_summary(self):
        if not self.student_marks:
            return {}

        first_exam = self.student_marks[0]['exam']
        class_group = first_exam['class_group']
        academic_year = first_exam['academic_year']

        exams_data = []
        for mark in self.student_marks:
            exam = mark['exam']
            exams_data.append({
                "subject": exam["subject"],
                "exam_type": exam["exam_type"],
                "title": exam["title"],
                "date_conducted": exam["date_conducted"].strftime("%Y-%m-%d"),
                "max_marks": exam["max_marks"],
                "score": mark["score"],
                "grade": mark["grade"],
            })

        return {
            "class_group": class_group,
            "academic_year": academic_year,
            "exams": exams_data
        }

    # ---------------------------------------------
    # 📊 Generate data for charts (bar/line)
    # ---------------------------------------------
    def get_exam_performance_chart_data(self):
        bar_chart_data = []
        labels = []
        student_scores = []
        class_avg_scores = []

        for mark in self.student_marks:
            exam = mark['exam']
            exam_title = exam['title']
            student_score = mark['score']
            class_avg = exam.get('class_avg', 0)  # Defaults to 0 if not available

            # Bar data for grouped comparison
            bar_chart_data.append({
                "exam_title": exam_title,
                "student_score": student_score,
                "class_avg": class_avg
            })

            # Line data for trend visualization
            labels.append(exam_title)
            student_scores.append(student_score)
            class_avg_scores.append(class_avg)

        return {
            "bar_chart_data": bar_chart_data,
            "line_chart_data": {
                "labels": labels,
                "student_scores": student_scores,
                "class_avg_scores": class_avg_scores
            }
        }

    # ---------------------------------------------
    # 🅰️ Analyze student's grades vs class
    # ---------------------------------------------
    def get_grade_insights(self):
        grade_data = []

        for mark in self.student_marks:
            exam = mark["exam"]
            student_grade = mark["grade"]
            exam_title = exam["title"]
            class_grades = exam.get("class_grades", [])  # List of all grades in the class

            # Count grade distribution per exam
            grade_distribution = dict(Counter(class_grades))

            grade_data.append({
                "exam_title": exam_title,
                "student_grade": student_grade,
                "grade_distribution": grade_distribution
            })

        return grade_data

    # ---------------------------------------------
    # 📄 Build printable report card dataset
    # ---------------------------------------------
    def build_report_card(self):
        """
        Builds a printable report card for all exams taken in the current academic year.

        Returns:
            List[Dict]: Structured exam records with grades and stats.
        """
        if not self.student_marks:
            return []

        report_card = []

        for mark in self.student_marks:
            exam = mark["exam"]
            report_card.append({
                "exam_title": exam["title"],
                "exam_code": exam.get("exam_code", "N/A"),
                "max_marks": exam["max_marks"],
                "grade": mark["grade"],
                "points": exam.get("points", None),
                "grade_distribution": dict(Counter(exam.get("class_grades", []))),
                "score": mark["score"],  # ✅ Student's actual score
            })

        return report_card

    # ---------------------------------------------
    # 💬 Generate intelligent subject-based comments
    # ---------------------------------------------
    def generate_subject_comments(self):
        comments = []

        for mark in self.student_marks:
            exam = mark["exam"]
            subject = exam["subject"]
            exam_title = exam["title"]
            student_score = mark["score"]
            student_grade = mark["grade"]
            class_grades = exam.get("class_grades", [])

            # Filter other students with same grade
            same_grade_scores = [
                m["score"] for m in self.student_marks
                if m["exam"]["title"] == exam_title and m["grade"] == student_grade and m["score"] is not None
            ]

            # AI-based comment generation
            comment = generate_intelligent_comment(
                subject, exam_title, student_grade, student_score, same_grade_scores
            )

            comments.append({
                "subject": subject,
                "exam_title": exam_title,
                "grade": student_grade,
                "comment": comment
            })

        return comments


# +++++++++++++++++++++++++++++++++++++++++++++
# 🎯 GPA Calculation Helper (Weighted Version)
# +++++++++++++++++++++++++++++++++++++++++++++

def calculate_gpa_and_grade(score_entries):
    """
    Calculates a weighted GPA and maps it to a grade.

    Args:
        score_entries (list): Each item is a dict with 'points' and 'weight'.

    Returns:
        dict: { "gpa": float, "grade": str }
    """

    # 🧪 Return early if no entries
    if not score_entries:
        return {"gpa": 0.0, "grade": "N/A"}

    total_weighted_points = 0.0
    total_weights = 0.0

    for entry in score_entries:
        try:
            points = float(entry.get("points", 0))       # Points earned
            weight = float(entry.get("weight", 1))       # Exam weight
            total_weighted_points += points * weight     # Contribution to GPA
            total_weights += weight                      # Total weight
        except (TypeError, ValueError):
            continue  # Ignore invalid entries

    if total_weights == 0:
        return {"gpa": 0.0, "grade": "N/A"}

    gpa = total_weighted_points / total_weights

    # 🅰️ Use default grading scale to map GPA
    grade_range = GradeRange.objects.filter(points__lte=gpa).order_by("-points").first()

    return {
        "gpa": round(gpa, 2),
        "grade": grade_range.letter if grade_range else "N/A"
    }
