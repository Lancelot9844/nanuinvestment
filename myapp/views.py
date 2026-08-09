from pathlib import Path
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import CustomerProfilePhotoForm, CustomerTicketForm
from .models import (
    Banner,
    Customer,
    DepositAccount,
    Download,
    EBankingCredential,
    LoanApplication,
    NewsActivity,
    Notice,
    SystemSetting,
    WebsitePopup,
)


def customer_must_change_password(user):
    try:
        credential = user.ebanking_credential
    except EBankingCredential.DoesNotExist:
        return False
    return credential.password_changed_at is None


def serialize_item(item):
    data = {
        "title": item.title,
        "description": item.description,
        "published_at": item.published_at.strftime("%d %b %Y"),
    }

    document = getattr(item, "document", None)
    if document:
        data["document_url"] = document.url

    image = getattr(item, "image", None)
    if image:
        data["image_url"] = image.url

    return data


def serialize_banner(banner):
    return {
        "title": banner.title,
        "image": banner.image.url,
    }


def serialize_popup(popup):
    data = {
        "id": popup.pk,
        "title": popup.title,
        "message": popup.message,
        "button_text": popup.button_text,
        "button_url": popup.button_url,
    }
    if popup.image:
        file_extension = Path(popup.image.name).suffix.lower()
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}
        data["file_url"] = popup.image.url
        data["file_name"] = Path(popup.image.name).name
        if file_extension in image_extensions:
            data["file_type"] = "image"
            data["image_url"] = popup.image.url
        elif file_extension == ".pdf":
            data["file_type"] = "pdf"
            data["pdf_url"] = popup.image.url
            data["document_url"] = popup.image.url
        else:
            data["file_type"] = "document"
            data["document_url"] = popup.image.url
    return data


def get_site_content():
    active_popup = WebsitePopup.objects.filter(is_active=True).first()
    return {
        "banners": [serialize_banner(item) for item in Banner.objects.filter(is_active=True)[:10]],
        "news": [serialize_item(item) for item in NewsActivity.objects.filter(is_active=True)[:6]],
        "notices": [serialize_item(item) for item in Notice.objects.filter(is_active=True)[:6]],
        "downloads": [serialize_item(item) for item in Download.objects.filter(is_active=True)[:6]],
        "popup": serialize_popup(active_popup) if active_popup else None,
    }


def home(request):
    return render(request, "index_react.html", {"site_content": get_site_content()})


def site_content_api(request):
    return JsonResponse(get_site_content())


def login_page(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin:index")
        return redirect("customer_dashboard")
    return render(request, "login.html")


def customer_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin:index")
        if customer_must_change_password(request.user):
            return redirect("customer_change_password")
        return redirect("customer_dashboard")

    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect(request.GET.get("next") or "admin:index")
            if customer_must_change_password(user):
                return redirect("customer_change_password")
            return redirect(request.GET.get("next") or "customer_dashboard")
        error = "Invalid username or password."

    return render(request, "customer/login.html", {"error": error})


def customer_logout(request):
    logout(request)
    return redirect("customer_login")


@login_required(login_url="customer_login")
def customer_dashboard(request):
    customer = getattr(request.user, "customer_profile", None)
    if customer is None:
        return render(request, "customer/no_account.html")
    if customer_must_change_password(request.user):
        return redirect("customer_change_password")

    system_setting = SystemSetting.get_solo()
    collection_queryset = customer.collections.select_related("collected_by")
    collections = collection_queryset[:12]
    transactions = customer.transactions.select_related("collected_by")[:10]
    collected_total = collection_queryset.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    account_total = customer.opening_balance + collected_total
    now = timezone.localtime()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_collected = (
        collection_queryset.filter(collected_at__gte=month_start).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )
    last_collection = collection_queryset.first()
    tickets = customer.tickets.select_related("assigned_to")[:10]
    open_ticket_count = customer.tickets.exclude(status=customer.tickets.model.Status.VERIFIED_COMPLETED).count()
    active_loans = customer.loan_applications.filter(status=LoanApplication.Status.APPROVED)
    loan_outstanding = sum((loan.outstanding_amount for loan in active_loans), Decimal("0.00"))
    active_deposits = customer.deposit_accounts.filter(status=DepositAccount.Status.ACTIVE)
    deposit_total = sum((deposit.total_paid for deposit in active_deposits), Decimal("0.00"))
    weekly_activity = []
    max_weekly_amount = Decimal("0.00")
    for offset in range(6, -1, -1):
        day = timezone.localdate() - timezone.timedelta(days=offset)
        amount = (
            collection_queryset.filter(collected_at__date=day).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        max_weekly_amount = max(max_weekly_amount, amount)
        weekly_activity.append({"label": day.strftime("%a"), "amount": amount, "height": 0})
    if max_weekly_amount > 0:
        weekly_activity = [
            {**item, "height": max(12, int((item["amount"] / max_weekly_amount) * 100))}
            for item in weekly_activity
        ]

    return render(
        request,
        "customer/dashboard.html",
        {
            "customer": customer,
            "currency_label": system_setting.currency_label or "Rs",
            "collections": collections,
            "transactions": transactions,
            "account_total": account_total,
            "monthly_collected": monthly_collected,
            "last_collection": last_collection,
            "tickets": tickets,
            "open_ticket_count": open_ticket_count,
            "loan_outstanding": loan_outstanding,
            "deposit_total": deposit_total,
            "active_deposit_count": active_deposits.count(),
            "active_loan_count": active_loans.count(),
            "weekly_activity": weekly_activity,
        },
    )


@login_required(login_url="customer_login")
def customer_create_ticket(request):
    customer = getattr(request.user, "customer_profile", None)
    if customer is None:
        return render(request, "customer/no_account.html")
    if customer_must_change_password(request.user):
        return redirect("customer_change_password")

    if request.method == "POST":
        form = CustomerTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.customer = customer
            ticket.created_by = request.user
            ticket.status = ticket.Status.OPEN
            ticket.save()
            return redirect("customer_dashboard")
    else:
        form = CustomerTicketForm()

    return render(request, "customer/ticket_form.html", {"form": form, "customer": customer})


@login_required(login_url="customer_login")
def customer_profile_settings(request):
    customer = getattr(request.user, "customer_profile", None)
    if customer is None:
        return render(request, "customer/no_account.html")
    if customer_must_change_password(request.user):
        return redirect("customer_change_password")

    if request.method == "POST":
        form = CustomerProfilePhotoForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_dashboard")
    else:
        form = CustomerProfilePhotoForm(instance=customer)

    return render(request, "customer/profile_settings.html", {"form": form, "customer": customer})


@login_required(login_url="customer_login")
def customer_change_password(request):
    customer = getattr(request.user, "customer_profile", None)
    if customer is None:
        return render(request, "customer/no_account.html")

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            EBankingCredential.objects.update_or_create(
                customer=customer,
                defaults={
                    "user": user,
                    "username": user.get_username(),
                    "temporary_password": "",
                    "password_changed_at": timezone.now(),
                },
            )
            update_session_auth_hash(request, user)
            return redirect("customer_dashboard")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "customer/password_change.html",
        {
            "form": form,
            "customer": customer,
            "password_change_required": customer_must_change_password(request.user),
        },
    )
