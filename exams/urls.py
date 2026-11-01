from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/dashboard-data/", views.dashboard_data, name="dashboard_data"),
    path("exams/", views.exam_list, name="exam_list"),
    path("exams/<int:pk>/register/", views.register_exam, name="register_exam"),
    path("registrations/", views.my_registrations, name="my_registrations"),
    path("registrations/<int:pk>/cancel/", views.cancel_registration, name="cancel_registration"),
    path("registrations/<int:pk>/hall-ticket/", views.hall_ticket, name="hall_ticket"),
    path("results/", views.results, name="results"),
    path("results/<int:pk>/", views.result_detail, name="result_detail"),
    path("profile/", views.profile, name="profile"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
