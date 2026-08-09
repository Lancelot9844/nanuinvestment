from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from datetime import timedelta


def seed_dummy_collections(apps, schema_editor):
    Customer = apps.get_model("myapp", "Customer")
    CollectionRecord = apps.get_model("myapp", "CollectionRecord")

    customers = list(Customer.objects.filter(customer_id__startswith="CUST-DUMMY-").order_by("customer_id")[:5])
    amounts = [Decimal("500.00"), Decimal("1000.00"), Decimal("750.00"), Decimal("1500.00"), Decimal("300.00")]
    visit_types = ["shop", "home", "shop", "office", "home"]
    now = django.utils.timezone.now()

    for index, customer in enumerate(customers):
        CollectionRecord.objects.get_or_create(
            customer=customer,
            amount=amounts[index],
            collected_at=now - timedelta(hours=index),
            defaults={
                "visit_type": visit_types[index],
                "note": "Dummy daily collection entry",
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("myapp", "0011_customer_kyc_document_and_seed_customers"),
    ]

    operations = [
        migrations.CreateModel(
            name="CollectionRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "visit_type",
                    models.CharField(
                        choices=[("shop", "Shop Visit"), ("home", "Home Visit"), ("office", "Office Collection")],
                        default="shop",
                        max_length=20,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("collected_at", models.DateTimeField()),
                ("note", models.CharField(blank=True, max_length=220)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "collected_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="collection_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="collections", to="myapp.customer"),
                ),
            ],
            options={
                "verbose_name": "Collection Record",
                "verbose_name_plural": "Collection Records",
                "ordering": ["-collected_at"],
            },
        ),
        migrations.RunPython(seed_dummy_collections, migrations.RunPython.noop),
    ]
