from django import template
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone

from myapp.models import CollectionRecord, Customer, Ticket


register = template.Library()


def percent(value, total):
    if not total:
        return 0
    return round((value / total) * 100)


def get_admin_metrics():
    today = timezone.localdate()
    active_collections = CollectionRecord.objects.filter(customer__is_deleted=False)
    today_collections = active_collections.filter(collected_at__date=today)
    total_customers = Customer.objects.count()
    new_customers_today = Customer.objects.filter(created_at__date=today).count()
    total_collection_amount = today_collections.aggregate(total=Sum("amount"))["total"] or 0
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

    return {
        "total_customers": total_customers,
        "new_customers_today": new_customers_today,
        "staff_count": get_user_model().objects.filter(is_staff=True).count(),
        "today_collection_amount": total_collection_amount,
        "today_collection_count": today_collections.count(),
        "pending_kyc": Customer.objects.filter(kyc_status=Customer.KycStatus.PENDING).count(),
        "open_tickets": Ticket.objects.exclude(status=Ticket.Status.VERIFIED_COMPLETED).count(),
        "recent_collections": recent_collections,
        "kyc_chart": kyc_chart,
        "staff_chart": staff_chart,
        "ticket_chart": ticket_chart,
        "account_chart": account_chart,
    }


@register.simple_tag
def admin_dashboard_metrics():
    return get_admin_metrics()
