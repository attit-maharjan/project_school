# ==========================================================
# 🔔 Exams App — Signal Handlers
# ==========================================================
# This module defines signal-based automation for the Exams app.
# It handles tasks such as:
# - Creating StudentMark records when a new exam is created
# - Notifying admins by email when an exam is created or deleted
# - Cleaning up student marks when an exam is deleted
# ==========================================================

from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import localtime
from django.apps import apps

from exams.models import Exam, StudentMark
from exams.utils import extract_emails_safe


# ==========================================================
# ✅ Signal: post_save — Exam Created
# ==========================================================
# Triggered after a new Exam is created.
# 1. Automatically generates StudentMark records
# 2. Sends a notification email to specified admins
# ==========================================================
@receiver(post_save, sender=Exam)
def handle_exam_created(sender, instance, created, **kwargs):
    if not created:
        return

    # 🔁 Get students enrolled in the class group
    ClassGroupStudentEnrollment = apps.get_model('enrollments', 'ClassGroupStudentEnrollment')
    student_ids = ClassGroupStudentEnrollment.objects.filter(
        class_group=instance.class_group,
        is_active=True
    ).values_list('student_id', flat=True).distinct()

    # 📝 Create StudentMark entries for these students
    existing_ids = StudentMark.objects.filter(exam=instance).values_list('student_id', flat=True)
    new_marks = [
        StudentMark(exam=instance, student_id=sid)
        for sid in student_ids if sid not in existing_ids
    ]
    StudentMark.objects.bulk_create(new_marks, ignore_conflicts=True)

    # 📧 Send notification email to admins
    emails = extract_emails_safe(instance.admin_emails)
    if emails:
        send_mail(
            subject=f"📘 Exam Created: {instance.title}",
            message=(
                f"Hello Admin,\n\n"
                f"A new exam has been created in the system.\n\n"
                f"📘 Title: {instance.title}\n"
                f"🏫 Class Group: {instance.class_group}\n"
                f"📚 Subject: {instance.subject.name}\n"
                f"🗓️ Academic Year: {instance.academic_year.name}\n"
                f"🧑‍🏫 Created by: {instance.created_by.user.get_full_name()} ({instance.created_by.user.email})\n"
                f"📝 Exam Type: {instance.exam_type.name}\n"
                f"🎯 Max Marks: {instance.max_marks}\n"
                f"⏰ Scheduled Date: {instance.date_conducted}\n"
                f"🆔 Exam Code: {instance.exam_code}\n"
                f"📅 Created At: {localtime(instance.created_at).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"Regards,\n"
                f"BIVGS Notification System"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True
        )


# ==========================================================
# ❌ Signal: pre_delete — Exam Deleted
# ==========================================================
# Triggered before an Exam is deleted.
# Removes all StudentMark records related to that exam.
# ==========================================================
@receiver(pre_delete, sender=Exam)
def delete_student_marks_for_exam(sender, instance, **kwargs):
    StudentMark.objects.filter(exam=instance).delete()


# ==========================================================
# 📤 Signal: post_delete — Notify Exam Deletion
# ==========================================================
# Sends an email notification to admins after an exam is deleted.
# Confirms the exam and its marks have been removed.
# ==========================================================
@receiver(post_delete, sender=Exam)
def notify_exam_deleted(sender, instance, **kwargs):
    emails = extract_emails_safe(instance.admin_emails)
    if emails:
        send_mail(
            subject=f"⚠️ Exam Deleted: {instance.title}",
            message=(
                f"Hello Admin,\n\n"
                f"The following exam has been removed from the system:\n\n"
                f"📘 Title: {instance.title}\n"
                f"🏫 Class Group: {instance.class_group}\n"
                f"📚 Subject: {instance.subject.name}\n"
                f"🧑‍🏫 Created by: {instance.created_by.user.get_full_name()} ({instance.created_by.user.email})\n"
                f"📝 Exam Type: {instance.exam_type.name}\n"
                f"🆔 Exam Code: {instance.exam_code}\n"
                f"🗑️ Deleted At: {localtime(instance.updated_at).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"⚠️ All student marks associated with this exam have also been removed.\n\n"
                f"Regards,\n"
                f"BIVGS Notification System"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True
        )
