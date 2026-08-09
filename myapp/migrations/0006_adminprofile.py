from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_profiles_for_existing_staff(apps, schema_editor):
    User = apps.get_model("auth", "User")
    AdminProfile = apps.get_model("myapp", "AdminProfile")

    for user in User.objects.filter(is_staff=True):
        AdminProfile.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("myapp", "0005_seed_default_banners"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone_number", models.CharField(blank=True, max_length=30)),
                ("address", models.TextField(blank=True)),
                ("photo", models.FileField(blank=True, upload_to="admin_profiles/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="admin_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Admin Profile",
                "verbose_name_plural": "Admin Profiles",
            },
        ),
        migrations.RunPython(create_profiles_for_existing_staff, migrations.RunPython.noop),
    ]
