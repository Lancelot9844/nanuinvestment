from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0013_banner_deleted_at_banner_is_deleted_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebsitePopup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("title", models.CharField(max_length=180)),
                ("message", models.TextField()),
                ("image", models.FileField(blank=True, upload_to="popups/")),
                ("button_text", models.CharField(blank=True, max_length=80)),
                ("button_url", models.CharField(blank=True, max_length=240)),
                ("is_active", models.BooleanField(default=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Website Popup",
                "verbose_name_plural": "Website Popups",
                "ordering": ["display_order", "-created_at"],
            },
        ),
    ]
