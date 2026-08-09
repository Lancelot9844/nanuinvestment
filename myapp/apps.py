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


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_save

        post_migrate.connect(ensure_content_groups, sender=self)
        post_save.connect(ensure_admin_profile, sender=get_user_model())
