# Path: users/helpers/generate_chart_images.py
import matplotlib
matplotlib.use("Agg")  # Non-GUI backend for PDF generation

import matplotlib.pyplot as plt
import io
import base64

GRADE_ORDER = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E', 'F']


def generate_report_chart_images(student, marks):
    """
    Generates base64-encoded bar chart images for each exam from StudentMark data.
    Each chart highlights the student's grade in that exam.

    Args:
        student (User): The student object
        marks (QuerySet): StudentMark queryset

    Returns:
        List[dict]: Each item has 'exam_title' and 'image_base64'
    """
    chart_images = []

    for mark in marks:
        exam = mark.exam
        distribution = exam.studentmark_set.values_list('grade', flat=True)
        student_grade = mark.grade

        # Count occurrences of each grade
        grade_counts = {grade: 0 for grade in GRADE_ORDER}
        for g in distribution:
            if g in grade_counts:
                grade_counts[g] += 1

        labels = [g for g in GRADE_ORDER if grade_counts[g] > 0]
        values = [grade_counts[g] for g in labels]
        colors = ['#3b82f6' if grade == student_grade else '#e5e7eb' for grade in labels]

        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(labels, values, color=colors)
        ax.set_title(f"{exam.title} — Grade Distribution")
        ax.set_ylabel("# Students")
        ax.set_xlabel("Grade")
        ax.set_ylim(bottom=0)
        ax.grid(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        chart_images.append({
            "exam_title": exam.title,
            "image_base64": f"data:image/png;base64,{image_base64}"
        })

    return chart_images


# users/helpers/generate_chart_images.py

import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for PDF generation
import matplotlib.pyplot as plt
import io
import base64

def generate_grade_distribution_charts(report_card):
    """
    Generates grade distribution bar charts for each exam in the report card.

    Args:
        report_card (list): List of dictionaries containing exam results and grade distributions.

    Returns:
        List[dict]: A list of dictionaries containing 'exam_title' and 'image_base64'.
    """
    chart_images = []

    for entry in report_card:
        # Ensure grade_distribution is a list of grades, not a dict
        if isinstance(entry["grade_distribution"], dict):
            # If it's a dictionary, get keys (grades) and values (count of students per grade)
            grade_counts = entry["grade_distribution"]
        else:
            # Otherwise, count the occurrences of each grade in the list
            grade_counts = {grade: entry["grade_distribution"].count(grade) for grade in set(entry["grade_distribution"])}

        sorted_grades = sorted(grade_counts.items(), key=lambda x: x[0])  # Sort by grade letter
        
        # Plot the chart
        labels = [item[0] for item in sorted_grades]
        values = [item[1] for item in sorted_grades]

        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(labels, values, color=['#3b82f6' if grade == entry['grade'] else '#e5e7eb' for grade in labels])
        ax.set_title(f"{entry['exam_title']} - Grade Distribution")
        ax.set_xlabel("Grade")
        ax.set_ylabel("Number of Students")
        ax.set_ylim(0, max(values) + 1)
        ax.grid(False)

        # Convert chart to base64
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')

        chart_images.append({
            "exam_title": entry["exam_title"],
            "image_base64": f"data:image/png;base64,{image_base64}"
        })

    return chart_images
