import csv
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import QuoteRequestForm, ResponseUpdateForm, StaffAuthenticationForm
from .models import QuoteRequest

staff_required = user_passes_test(
    lambda u: u.is_authenticated and u.is_active and u.is_staff,
    login_url="staff_login",
)


# ---------------------------------------------------------------- public pages

def home(request):
    return render(request, "home.html")


def services(request):
    return render(request, "services.html")


def about(request):
    return render(request, "about.html")


def areas(request):
    return render(request, "areas.html")


def faq(request):
    return render(request, "faq.html")


def quote(request):
    form = QuoteRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not form.cleaned_data.get("website"):  # empty honeypot = real person
            form.save()
        return redirect("thank_you")
    return render(request, "quote.html", {"form": form})


def thank_you(request):
    return render(request, "thank_you.html")


# ---------------------------------------------------------------- staff area

class StaffLoginView(LoginView):
    template_name = "staff/login.html"
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("staff_dashboard")
        return super().dispatch(request, *args, **kwargs)


def _filtered(request):
    qs = QuoteRequest.objects.all()
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    if status in dict(QuoteRequest.STATUS_CHOICES):
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q)
                       | Q(phone__icontains=q) | Q(zip_code__icontains=q))
    return qs, status, q


@staff_required
def dashboard(request):
    now = timezone.now()
    base = QuoteRequest.objects.all()
    total = base.count()
    by_status = dict(base.values_list("status").annotate(n=Count("id")))
    by_service = {k: 0 for k, _ in QuoteRequest.SERVICE_CHOICES}
    by_service.update(dict(base.values_list("service").annotate(n=Count("id"))))
    service_rows = [{
        "label": label, "count": by_service[key],
        "pct": round(by_service[key] * 100 / total) if total else 0,
    } for key, label in QuoteRequest.SERVICE_CHOICES]
    return render(request, "staff/dashboard.html", {
        "total": total,
        "new": by_status.get("new", 0),
        "booked": by_status.get("booked", 0),
        "week": base.filter(created_at__gte=now - timedelta(days=7)).count(),
        "today": base.filter(created_at__date=timezone.localdate()).count(),
        "service_rows": service_rows,
        "recent": base[:6],
        "needs_reply": base.filter(status="new").order_by("created_at")[:5],
    })


@staff_required
def response_list(request):
    qs, status, q = _filtered(request)
    page = Paginator(qs, 20).get_page(request.GET.get("page"))
    counts = dict(QuoteRequest.objects.values_list("status").annotate(n=Count("id")))
    tabs = [(k, label, counts.get(k, 0)) for k, label in QuoteRequest.STATUS_CHOICES]
    return render(request, "staff/response_list.html", {
        "page": page, "status": status, "q": q, "tabs": tabs,
        "total": sum(counts.values()),
    })


@staff_required
def response_detail(request, pk):
    obj = get_object_or_404(QuoteRequest, pk=pk)
    form = ResponseUpdateForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Changes saved.")
        return redirect("staff_response_detail", pk=obj.pk)
    return render(request, "staff/response_detail.html", {"obj": obj, "form": form})


@staff_required
@require_POST
def response_delete(request, pk):
    obj = get_object_or_404(QuoteRequest, pk=pk)
    obj.delete()
    messages.success(request, "Response deleted.")
    return redirect("staff_responses")


def _safe_cell(value):
    """Stop spreadsheet apps from running a client's text as a formula."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@staff_required
def response_export(request):
    qs, _, _ = _filtered(request)
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="client-responses.csv"'
    w = csv.writer(resp)
    w.writerow(["Received", "Name", "Phone", "Email", "Address", "ZIP", "Service", "Bedrooms",
                "Bathrooms", "Frequency", "Preferred date", "Preferred time", "Extras",
                "Message", "Status", "Notes"])
    for r in qs:
        w.writerow([_safe_cell(x) for x in (
            timezone.localtime(r.created_at).strftime("%Y-%m-%d %H:%M"), r.name, r.phone,
            r.email, r.address, r.zip_code, r.get_service_display(), r.get_bedrooms_display(),
            r.get_bathrooms_display(), r.get_frequency_display(), r.preferred_date or "",
            r.get_preferred_time_display(), ", ".join(r.extras), r.message,
            r.get_status_display(), r.staff_notes)])
    return resp
