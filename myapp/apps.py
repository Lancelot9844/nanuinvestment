from django.apps import AppConfig
from django.db.models.signals import post_migrate


def ensure_content_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    model_names = (
        "banner",
        "newsactivity",
        "notice",
        "download",
        "customer",
        "dailycollection",
        "collectionrecord",
        "transaction",
        "loanapplication",
        "loanrepayment",
        "depositaccount",
        "depositpayment",
        "securityevent",
        "smsdelivery",
        "systemsetting",
        "ticket",
    )
    content_types = ContentType.objects.filter(app_label="myapp", model__in=model_names)

    content_staff, _ = Group.objects.get_or_create(name="Content Staff")
    content_viewer, _ = Group.objects.get_or_create(name="Content Viewer")

    staff_permissions = Permission.objects.filter(
        content_type__in=content_types,
        codename__regex=r"^(add|change|delete|view)_",
    )
    viewer_permissions = Permission.objects.filter(
        content_type__in=content_types,
        codename__regex=r"^view_",
    )

    content_staff.permissions.add(*staff_permissions)
    content_viewer.permissions.add(*viewer_permissions)


def ensure_admin_profile(sender, instance, created, **kwargs):
    if not created:
        return

    from .models import AdminProfile

    if instance.is_staff or instance.is_superuser:
        AdminProfile.objects.get_or_create(user=instance)


def schedule_transaction_sms(sender, instance, created, **kwargs):
    if not created or instance.status != sender.Status.COMPLETED:
        return

    from .sms import schedule_collection_receipt_sms

    schedule_collection_receipt_sms(instance.pk)


def get_request_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def record_login_success(sender, request, user, **kwargs):
    from .models import SecurityEvent

    SecurityEvent.objects.create(
        event_type=SecurityEvent.EventType.LOGIN_SUCCESS,
        user=user,
        username=user.get_username(),
        ip_address=get_request_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        path=request.path[:220],
        message="Successful login",
    )


def record_login_failed(sender, credentials, request, **kwargs):
    from .models import SecurityEvent

    username = (credentials or {}).get("username", "")
    SecurityEvent.objects.create(
        event_type=SecurityEvent.EventType.LOGIN_FAILED,
        username=username,
        ip_address=get_request_ip(request) if request else None,
        user_agent=(request.META.get("HTTP_USER_AGENT", "") if request else "")[:300],
        path=(request.path if request else "")[:220],
        message="Failed login attempt",
    )


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self):
        from django.contrib.auth.signals import user_login_failed, user_logged_in
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_save

        from .models import Transaction

        post_migrate.connect(ensure_content_groups, sender=self)
        post_save.connect(ensure_admin_profile, sender=get_user_model())
        post_save.connect(
            schedule_transaction_sms,
            sender=Transaction,
            dispatch_uid="myapp.schedule_transaction_sms",
        )
        user_logged_in.connect(record_login_success, sender=get_user_model())
        user_login_failed.connect(record_login_failed)
