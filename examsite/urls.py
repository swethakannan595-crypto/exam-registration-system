from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Exam Registration Admin"
admin.site.site_title = "Exam Registration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("exams.urls")),
]
