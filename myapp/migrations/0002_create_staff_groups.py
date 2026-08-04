from django.db import migrations


def create_staff_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    model_names = ("newsactivity", "notice", "download")
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

    content_staff.permissions.set(staff_permissions)
    content_viewer.permissions.set(viewer_permissions)


def remove_staff_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=("Content Staff", "Content Viewer")).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_staff_groups, remove_staff_groups),
    ]
