from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("myapp", "0006_adminprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_id", models.CharField(blank=True, max_length=20, unique=True)),
                ("first_name", models.CharField(max_length=80)),
                ("last_name", models.CharField(max_length=80)),
                ("phone_number", models.CharField(max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("citizenship_number", models.CharField(blank=True, max_length=80)),
                ("address", models.TextField()),
                (
                    "account_type",
                    models.CharField(
                        choices=[
                            ("savings", "Savings Account"),
                            ("current", "Current Account"),
                            ("fixed", "Fixed Deposit"),
                            ("recurring", "Recurring Deposit"),
                        ],
                        default="savings",
                        max_length=20,
                    ),
                ),
                ("opening_balance", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("nominee_name", models.CharField(blank=True, max_length=160)),
                ("nominee_phone", models.CharField(blank=True, max_length=30)),
                ("kyc_document", models.FileField(blank=True, upload_to="customer_kyc/")),
                (
                    "kyc_status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("pending", "Sent for Approval"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("submitted_for_approval_at", models.DateTimeField(blank=True, null=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_customers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer & KYC",
                "verbose_name_plural": "Customers & KYC",
                "ordering": ["-created_at"],
            },
        ),
    ]
