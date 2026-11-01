from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    roll_no = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=80)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.roll_no} - {self.user.get_full_name() or self.user.username}"


class Exam(models.Model):
    title = models.CharField(max_length=150)
    code = models.CharField(max_length=15, unique=True)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=180)
    venue = models.CharField(max_length=120)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    seats = models.PositiveIntegerField(default=100)
    registration_deadline = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def seats_taken(self):
        return self.registrations.filter(status=Registration.CONFIRMED).count()

    @property
    def seats_left(self):
        return max(self.seats - self.seats_taken, 0)

    @property
    def deadline_passed(self):
        return timezone.localdate() > self.registration_deadline

    @property
    def is_open(self):
        return self.is_active and not self.deadline_passed and self.seats_left > 0

    @property
    def start_datetime(self):
        return timezone.make_aware(datetime.combine(self.date, self.start_time))


class Registration(models.Model):
    CONFIRMED, CANCELLED = "confirmed", "cancelled"
    STATUS_CHOICES = [(CONFIRMED, "Confirmed"), (CANCELLED, "Cancelled")]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registrations")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="registrations")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=CONFIRMED)
    hall_ticket = models.CharField(max_length=30, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "exam")
        ordering = ["exam__date"]

    def __str__(self):
        return f"{self.student.username} -> {self.exam.code} ({self.status})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.hall_ticket:
            self.hall_ticket = f"HT-{self.exam.code}-{self.pk:05d}"
            super().save(update_fields=["hall_ticket"])

    @property
    def can_cancel(self):
        return self.status == self.CONFIRMED and not self.exam.deadline_passed


class Result(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name="result")
    marks = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    remarks = models.CharField(max_length=200, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.registration} - {self.marks}/{self.max_marks}"

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def percentage(self):
        return round(float(self.marks) / float(self.max_marks) * 100, 1) if self.max_marks else 0

    @property
    def passed(self):
        return self.percentage >= settings.PASS_PERCENTAGE

    @property
    def grade(self):
        p = self.percentage
        for cutoff, g in [(90, "O"), (80, "A+"), (70, "A"), (60, "B+"), (50, "B"), (settings.PASS_PERCENTAGE, "C")]:
            if p >= cutoff:
                return g
        return "F"
