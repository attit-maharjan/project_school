#++++++++++++++++++++++++++++++++++++++++++++
# Helper Function in exams app
# Path: BIVGS > exams app > helpers > grade_calculation.py
#++++++++++++++++++++++++++++++++++++++++++++

# ============================================
# Imports
# ============================================
from exams.models import GradeRange  # Model containing grade letter and corresponding GPA point mapping

# ============================================
# Function: get_overall_grade_from_points
# Purpose: Computes overall GPA and corresponding letter grade
# Input: student_marks - list of student mark instances, each linked to an exam and grade letter
# Output: Dictionary with GPA (float) and overall letter grade (str)
# ============================================
def get_overall_grade_from_points(student_marks):
    total_points = 0      # Cumulative GPA points from all valid exams
    total_exams = 0       # Count of valid exams considered for GPA calculation

    for mark in student_marks:
        exam = mark.exam                      # Get associated exam object
        grade_letter = mark.grade             # Grade letter earned (e.g., 'A', 'B', etc.)
        scale = exam.grading_scale            # Grading scale associated with the exam

        if not scale or not grade_letter:
            # Skip marks with missing grading scale or grade letter
            continue

        try:
            # Attempt to find the point value corresponding to the grade letter in the grading scale
            grade_range = scale.grade_ranges.get(letter=grade_letter)
            total_points += float(grade_range.points)  # Add grade points to total
            total_exams += 1                           # Increment count of valid exams
        except GradeRange.DoesNotExist:
            # If grade letter does not exist in grading scale, skip this mark
            continue

    if total_exams == 0:
        # Handle case where no valid exams were found
        return {"gpa": 0.0, "grade": "N/A"}

    gpa = total_points / total_exams  # Compute average GPA

    # Convert computed GPA back to the closest letter grade by finding highest grade with points <= GPA
    grade_letter = scale.grade_ranges.filter(points__lte=gpa).order_by("-points").first()

    return {
        "gpa": round(gpa, 2),  # Round GPA to 2 decimal places for readability
        "grade": grade_letter.letter if grade_letter else "N/A"  # Return letter grade or "N/A" if none matched
    }
