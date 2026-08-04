from django.db import migrations


def add_banner_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    try:
        banner_type = ContentType.objects.get(app_label="myapp", model="banner")
    except ContentType.DoesNotExist:
        return

    content_staff, _ = Group.objects.get_or_create(name="Content Staff")
    content_viewer, _ = Group.objects.get_or_create(name="Content Viewer")

    staff_permissions = Permission.objects.filter(
        content_type=banner_type,
        codename__in=("add_banner", "change_banner", "delete_banner", "view_banner"),
    )
    viewer_permissions = Permission.objects.filter(
        content_type=banner_type,
        codename="view_banner",
    )

    content_staff.permissions.add(*staff_permissions)
    content_viewer.permissions.add(*viewer_permissions)


def remove_banner_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    try:
        banner_type = ContentType.objects.get(app_label="myapp", model="banner")
    except ContentType.DoesNotExist:
        return

    banner_permissions = Permission.objects.filter(content_type=banner_type)
    for group_name in ("Content Staff", "Content Viewer"):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue
        group.permissions.remove(*banner_permissions)


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0003_banner"),
    ]

    operations = [
        migrations.RunPython(add_banner_permissions, remove_banner_permissions),
    ]
