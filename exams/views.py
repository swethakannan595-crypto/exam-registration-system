from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ProfileForm, StudentSignUpForm
from .models import Exam, Registration, Result, StudentProfile


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = StudentSignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created. You can now register for exams.")
        return redirect("dashboard")
    return render(request, "registration/signup.html", {"form": form})


def _published_results(user):
    return Result.objects.filter(
        registration__student=user, is_published=True
    ).select_related("registration__exam").order_by("registration__exam__date")


@login_required
def dashboard(request):
    today = timezone.localdate()
    regs = request.user.registrations.select_related("exam")
    confirmed = regs.filter(status=Registration.CONFIRMED)
    upcoming = confirmed.filter(exam__date__gte=today).order_by("exam__date", "exam__start_time")
    results_qs = _published_results(request.user)
    percentages = [r.percentage for r in results_qs]
    next_exam = upcoming.first()
    ctx = {
        "total_registered": confirmed.count(),
        "upcoming_count": upcoming.count(),
        "results_count": len(percentages),
        "average": round(sum(percentages) / len(percentages), 1) if percentages else None,
        "upcoming": upcoming[:5],
        "latest_results": results_qs.order_by("-published_at")[:4],
        "open_exams": [e for e in Exam.objects.filter(is_active=True, date__gte=today)
                       if e.is_open and not regs.filter(exam=e, status=Registration.CONFIRMED).exists()][:4],
        "next_exam": next_exam,
        "next_exam_iso": next_exam.exam.start_datetime.isoformat() if next_exam else "",
    }
    return render(request, "exams/dashboard.html", ctx)


@login_required
def dashboard_data(request):
    """JSON feed for the interactive charts on the dashboard."""
    results_qs = list(_published_results(request.user))
    passed = sum(1 for r in results_qs if r.passed)
    regs = request.user.registrations
    return JsonResponse({
        "labels": [r.registration.exam.code for r in results_qs],
        "titles": [r.registration.exam.title for r in results_qs],
        "percentages": [r.percentage for r in results_qs],
        "pass_fail": [passed, len(results_qs) - passed],
        "status": [regs.filter(status=Registration.CONFIRMED).count(),
                   regs.filter(status=Registration.CANCELLED).count()],
    })


@login_required
def exam_list(request):
    q = request.GET.get("q", "").strip()
    flt = request.GET.get("filter", "all")
    today = timezone.localdate()
    exams = Exam.objects.filter(is_active=True, date__gte=today)
    if q:
        exams = exams.filter(Q(title__icontains=q) | Q(code__icontains=q) | Q(venue__icontains=q))
    mine = set(request.user.registrations.filter(status=Registration.CONFIRMED).values_list("exam_id", flat=True))
    rows = []
    for e in exams:
        registered = e.pk in mine
        if flt == "open" and not e.is_open:
            continue
        if flt == "registered" and not registered:
            continue
        rows.append({"exam": e, "registered": registered})
    return render(request, "exams/exam_list.html", {"rows": rows, "q": q, "flt": flt})


@login_required
@require_POST
def register_exam(request, pk):
    with transaction.atomic():
        exam = get_object_or_404(Exam.objects.select_for_update(), pk=pk, is_active=True)
        existing = Registration.objects.filter(student=request.user, exam=exam).first()
        if existing and existing.status == Registration.CONFIRMED:
            messages.info(request, f"You are already registered for {exam.code}.")
        elif exam.deadline_passed:
            messages.error(request, "Registration for this exam has closed.")
        elif exam.seats_left <= 0:
            messages.error(request, "No seats left for this exam.")
        else:
            if existing:
                existing.status = Registration.CONFIRMED
                existing.save()
            else:
                Registration.objects.create(student=request.user, exam=exam)
            messages.success(request, f"Registered for {exam.title}. Your hall ticket is ready.")
    return redirect(request.POST.get("next") or "my_registrations")


@login_required
def my_registrations(request):
    regs = request.user.registrations.select_related("exam").order_by("-registered_at")
    return render(request, "exams/my_registrations.html", {"regs": regs})


@login_required
@require_POST
def cancel_registration(request, pk):
    reg = get_object_or_404(Registration, pk=pk, student=request.user)
    if reg.can_cancel:
        reg.status = Registration.CANCELLED
        reg.save()
        messages.success(request, f"Registration for {reg.exam.code} cancelled.")
    else:
        messages.error(request, "This registration can no longer be cancelled.")
    return redirect("my_registrations")


@login_required
def hall_ticket(request, pk):
    reg = get_object_or_404(Registration, pk=pk, student=request.user, status=Registration.CONFIRMED)
    return render(request, "exams/hall_ticket.html", {"reg": reg})


@login_required
def results(request):
    qs = _published_results(request.user)
    pending = request.user.registrations.filter(status=Registration.CONFIRMED).exclude(
        result__is_published=True).filter(exam__date__lt=timezone.localdate()).select_related("exam")
    return render(request, "exams/results.html", {"results": qs, "pending": pending})


@login_required
def result_detail(request, pk):
    result = get_object_or_404(_published_results(request.user), pk=pk)
    return render(request, "exams/result_detail.html", {"result": result})


@login_required
def profile(request):
    prof, _ = StudentProfile.objects.get_or_create(
        user=request.user, defaults={"roll_no": f"TMP{request.user.pk}", "department": ""})
    form = ProfileForm(request.POST or None, instance=prof)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("profile")
    return render(request, "exams/profile.html", {"form": form, "prof": prof})
