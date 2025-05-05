# Path: BIVGS > users app > views/dashboards/student_views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.services.student_dashboard_service import (
    get_student_dashboard_summary,
    get_student_subjects,
    get_student_exam_schedule,
)
from users.services.student_exam_context_service import (
    get_exam_summary_context,
    get_exam_performance_context,
    get_exam_insights_context,
    get_exam_report_card_context,
    get_exam_comments_context,
)


# views/dashboards/student_views.py
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from users.helpers.generate_chart_images import generate_grade_distribution_charts
# ============================================================
# 📚 Student Dashboard View
# ============================================================

@login_required
def student_dashboard(request):
    student = request.user.student
    context = get_student_dashboard_summary(student)
    return render(request, 'dashboards/student/student_dashboard.html', context)


# ============================================================
# 📚 Student Subjects View
# ============================================================

@login_required
def student_subjects_view(request):
    student = request.user.student
    context = get_student_subjects(student)
    return render(request, 'dashboards/student/student_subjects.html', context)


# ============================================================
# 🧪 Student Exam Schedule View
# ============================================================

@login_required
def student_exam_schedule_view(request):
    student = request.user.student
    context = get_student_exam_schedule(student)
    return render(request, 'dashboards/student/student_exam_schedule.html', context)


# ============================================================
# 📄 Summary of All Exams
# ============================================================

@login_required
def exam_summary_view(request):
    student = request.user.student
    context = get_exam_summary_context(student)
    return render(request, 'dashboards/student/exam_summary.html', context)


# ============================================================
# 📊 Performance Chart View
# ============================================================

@login_required
def exam_performance_view(request):
    student = request.user.student
    context = get_exam_performance_context(student)
    return render(request, 'dashboards/student/exam_performance.html', context)


# ============================================================
# 📈 Grade Insights View
# ============================================================

@login_required
def exam_insights_view(request):
    student = request.user.student
    context = get_exam_insights_context(student)
    return render(request, 'dashboards/student/exam_insights.html', context)


# ============================================================
# 🧾 Report Card View
# ============================================================

@login_required
def exam_report_card_view(request):
    student = request.user.student
    context = get_exam_report_card_context(student)
    return render(request, 'dashboards/student/exam_report_card.html', context)


# ============================================================
# 💬 Subject Comments View
# ============================================================

@login_required
def exam_comments_view(request):
    student = request.user.student
    context = get_exam_comments_context(student)
    return render(request, 'dashboards/student/exam_comments.html', context)




# ============================================================
# 📄 PDF Report Card Download View
# ============================================================



@login_required
def exam_report_card_pdf_view(request):
    student = request.user.student
    context = get_exam_report_card_context(student)

    # Inject chart image base64
    context["report_chart_images"] = generate_grade_distribution_charts(context["report_card"])
    context["user"] = request.user

    template = get_template("dashboards/student/pdf/pdf_report_card_template.html")
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report_card.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("PDF generation failed", status=500)
    return response

