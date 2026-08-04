from django.apps import AppConfig
from django.db.models.signals import post_migrate


def ensure_content_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    model_names = ("banner", "newsactivity", "notice", "download")
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


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self):
        post_migrate.connect(ensure_content_groups, sender=self)
