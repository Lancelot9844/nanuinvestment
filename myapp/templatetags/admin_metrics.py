from django import template
from django.contrib.auth import get_user_model
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone

from myapp.models import CollectionRecord, Customer, DepositAccount, LoanApplication, Ticket


register = template.Library()


def percent(value, total):
    if not total:
        return 0
    return round((value / total) * 100)


def get_admin_metrics():
    today = timezone.localdate()
    active_collections = CollectionRecord.objects.filter(customer__is_deleted=False)
    today_collections = active_collections.filter(collected_at__date=today)
    yesterday_collections = active_collections.filter(collected_at__date=today - timedelta(days=1))
    month_collections = active_collections.filter(collected_at__year=today.year, collected_at__month=today.month)
    total_customers = Customer.objects.count()
    new_customers_today = Customer.objects.filter(created_at__date=today).count()
    total_collection_amount = today_collections.aggregate(total=Sum("amount"))["total"] or 0
    yesterday_collection_amount = yesterday_collections.aggregate(total=Sum("amount"))["total"] or 0
    month_collection_amount = month_collections.aggregate(total=Sum("amount"))["total"] or 0
    total_opening_balance = Customer.objects.aggregate(total=Sum("opening_balance"))["total"] or 0
    total_collected_amount = active_collections.aggregate(total=Sum("amount"))["total"] or 0
    total_savings = total_opening_balance + total_collected_amount
    recent_collections = active_collections.select_related("customer", "collected_by")[:8]

    kyc_rows = list(Customer.objects.values("kyc_status").annotate(count=Count("id")).order_by("kyc_status"))
    kyc_chart = [
        {
            "label": dict(Customer.KycStatus.choices).get(row["kyc_status"], row["kyc_status"]),
            "count": row["count"],
            "percent": percent(row["count"], total_customers),
        }
        for row in kyc_rows
    ]

    staff_rows = list(
        active_collections.values("collected_by__username")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")[:6]
    )
    max_staff_total = max([row["total"] or 0 for row in staff_rows], default=0)
    staff_chart = [
        {
            "label": row["collected_by__username"] or "Unassigned",
            "total": row["total"] or 0,
            "count": row["count"],
            "percent": percent(row["total"] or 0, max_staff_total),
        }
        for row in staff_rows
    ]

    ticket_total = Ticket.objects.count()
    ticket_rows = list(Ticket.objects.values("status").annotate(count=Count("id")).order_by("status"))
    ticket_chart = [
        {
            "label": dict(Ticket.Status.choices).get(row["status"], row["status"]),
            "count": row["count"],
            "percent": percent(row["count"], ticket_total),
        }
        for row in ticket_rows
    ]

    account_rows = list(Customer.objects.values("account_type").annotate(count=Count("id")).order_by("account_type"))
    account_chart = [
        {
            "label": dict(Customer.AccountType.choices).get(row["account_type"], row["account_type"]),
            "count": row["count"],
            "percent": percent(row["count"], total_customers),
        }
        for row in account_rows
    ]

    weekly_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    weekly_totals = []
    for day in weekly_days:
        total = active_collections.filter(collected_at__date=day).aggregate(total=Sum("amount"))["total"] or 0
        weekly_totals.append({"label": day.strftime("%a"), "total": total})
    max_weekly_total = max([row["total"] for row in weekly_totals], default=0)
    weekly_collection_chart = [
        {
            "label": row["label"],
            "total": row["total"],
            "percent": max(percent(row["total"], max_weekly_total), 8) if row["total"] else 0,
        }
        for row in weekly_totals
    ]

    if yesterday_collection_amount:
        today_collection_change_percent = round(
            ((total_collection_amount - yesterday_collection_amount) / yesterday_collection_amount) * 100,
            1,
        )
    else:
        today_collection_change_percent = 100 if total_collection_amount else 0

    staff_completed_tickets = Ticket.objects.filter(status=Ticket.Status.STAFF_COMPLETED).count()
    pending_kyc_count = Customer.objects.filter(kyc_status=Customer.KycStatus.PENDING).count()
    pending_collection_datetime_count = CollectionRecord.objects.filter(
        datetime_approval_status=CollectionRecord.DateTimeApprovalStatus.PENDING,
        is_deleted=False,
    ).count()
    active_loans = LoanApplication.objects.filter(
        status=LoanApplication.Status.APPROVED,
        is_deleted=False,
    ).select_related("customer")
    loan_outstanding = sum((loan.outstanding_amount for loan in active_loans), start=Decimal("0.00"))
    overdue_loans = [loan for loan in active_loans if loan.is_overdue]
    loan_overdue = sum((loan.outstanding_amount for loan in overdue_loans), start=Decimal("0.00"))
    pending_loan_count = LoanApplication.objects.filter(
        status=LoanApplication.Status.PENDING,
        is_deleted=False,
    ).count()
    pending_deposit_count = DepositAccount.objects.filter(
        status=DepositAccount.Status.PENDING,
        is_deleted=False,
    ).count()
    fixed_deposit_accounts = DepositAccount.objects.filter(
        deposit_type=DepositAccount.DepositType.FIXED,
        status=DepositAccount.Status.ACTIVE,
        is_deleted=False,
    ).count()
    deposits_maturing_soon = DepositAccount.objects.filter(
        status=DepositAccount.Status.ACTIVE,
        maturity_date__gte=today,
        maturity_date__lte=today + timedelta(days=7),
        is_deleted=False,
    ).count()
    assigned_open_tickets = Ticket.objects.filter(status__in=[Ticket.Status.OPEN, Ticket.Status.ASSIGNED]).count()
    cash_collectors_pending = (
        today_collections.exclude(collected_by__isnull=True).values("collected_by").distinct().count()
    )

    return {
        "total_customers": total_customers,
        "new_customers_today": new_customers_today,
        "staff_count": get_user_model().objects.filter(is_staff=True).count(),
        "today_collection_amount": total_collection_amount,
        "today_collection_change_percent": today_collection_change_percent,
        "today_collection_count": today_collections.count(),
        "month_collection_amount": month_collection_amount,
        "total_savings": total_savings,
        "loan_outstanding": loan_outstanding,
        "loan_overdue": loan_overdue,
        "cash_to_reconcile": total_collection_amount,
        "cash_collectors_pending": cash_collectors_pending,
        "pending_kyc": pending_kyc_count,
        "approval_count": pending_kyc_count + staff_completed_tickets + pending_collection_datetime_count + pending_loan_count + pending_deposit_count,
        "pending_loan_count": pending_loan_count,
        "pending_deposit_count": pending_deposit_count,
        "pending_collection_datetime_count": pending_collection_datetime_count,
        "staff_completed_tickets": staff_completed_tickets,
        "assigned_open_tickets": assigned_open_tickets,
        "fixed_deposit_accounts": fixed_deposit_accounts,
        "deposits_maturing_soon": deposits_maturing_soon,
        "open_tickets": Ticket.objects.exclude(status=Ticket.Status.VERIFIED_COMPLETED).count(),
        "recent_collections": recent_collections,
        "kyc_chart": kyc_chart,
        "staff_chart": staff_chart,
        "ticket_chart": ticket_chart,
        "account_chart": account_chart,
        "weekly_collection_chart": weekly_collection_chart,
        "weekly_collection_total": sum(row["total"] for row in weekly_totals),
    }


@register.simple_tag
def admin_dashboard_metrics():
    return get_admin_metrics()
