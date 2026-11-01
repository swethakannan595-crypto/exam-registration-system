from django.contrib import admin
from django.utils import timezone

from .models import Exam, Registration, Result, StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("roll_no", "user", "department", "phone")
    search_fields = ("roll_no", "user__username", "user__first_name")


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "date", "venue", "seats", "registration_deadline", "is_active")
    list_filter = ("is_active", "date")
    search_fields = ("code", "title")


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("hall_ticket", "student", "exam", "status", "registered_at")
    list_filter = ("status", "exam")
    search_fields = ("hall_ticket", "student__username")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("registration", "marks", "max_marks", "grade", "is_published", "published_at")
    list_filter = ("is_published",)
    actions = ["publish", "unpublish"]

    @admin.action(description="Publish selected results")
    def publish(self, request, queryset):
        queryset.filter(is_published=False).update(is_published=True, published_at=timezone.now())

    @admin.action(description="Unpublish selected results")
    def unpublish(self, request, queryset):
        queryset.update(is_published=False, published_at=None)
