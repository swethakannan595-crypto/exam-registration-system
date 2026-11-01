from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from exams.models import Exam, Registration, Result, StudentProfile


class Command(BaseCommand):
    help = "Create demo exams, a demo student and sample results."

    def handle(self, *args, **opts):
        today = timezone.localdate()
        specs = [
            ("CS101", "Programming in Python", -40, 120, 100, "Block A, Hall 1", 0),
            ("CS102", "Database Management Systems", -25, 80, 100, "Block A, Hall 2", 0),
            ("CS103", "Web Technologies", -10, 25, 100, "Block B, Hall 3", 0),
            ("CS201", "Cloud Computing", 12, 100, 350, "Block B, Hall 1", 0),
            ("CS202", "Data Structures", 20, 60, 300, "Block C, Lab 2", 0),
            ("CS203", "Computer Networks", 30, 2, 300, "Block C, Hall 4", 0),
            ("CS204", "Machine Learning", 45, 80, 400, "Block A, Hall 5", 0),
        ]
        exams = {}
        for code, title, offset, seats, fee, venue, _ in specs:
            exam, _c = Exam.objects.get_or_create(code=code, defaults=dict(
                title=title, description=f"End-term examination for {title}.",
                date=today + timedelta(days=offset), start_time="10:00", duration_minutes=180,
                venue=venue, fee=fee, seats=seats,
                registration_deadline=today + timedelta(days=offset - 5)))
            exams[code] = exam

        user, created = User.objects.get_or_create(username="student", defaults=dict(
            first_name="Demo", last_name="Student", email="student@example.com"))
        if created:
            user.set_password("student123")
            user.save()
        StudentProfile.objects.get_or_create(user=user, defaults=dict(
            roll_no="IT2027001", department="BSc Information Technology", phone="9876543210"))

        marks = {"CS101": 82, "CS102": 67, "CS103": 35}
        for code, m in marks.items():
            reg, _c = Registration.objects.get_or_create(student=user, exam=exams[code])
            Result.objects.get_or_create(registration=reg, defaults=dict(
                marks=m, is_published=True, remarks="Good effort" if m >= 40 else "Reappear"))
        Registration.objects.get_or_create(student=user, exam=exams["CS201"])
        Registration.objects.get_or_create(student=user, exam=exams["CS202"])

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
        self.stdout.write(self.style.SUCCESS("Demo data ready. student/student123, admin/admin123"))
