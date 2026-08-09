from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_transactions_for_existing_collections(apps, schema_editor):
    CollectionRecord = apps.get_model("myapp", "CollectionRecord")
    Transaction = apps.get_model("myapp", "Transaction")

    running_totals = {}
    next_number = 1
    for collection in CollectionRecord.objects.filter(is_deleted=False).select_related("customer").order_by("collected_at", "id"):
        customer = collection.customer
        current_total = running_totals.get(customer.pk, customer.opening_balance)
        balance_after = current_total + collection.amount
        running_totals[customer.pk] = balance_after
        Transaction.objects.get_or_create(
            collection_record=collection,
            defaults={
                "transaction_id": f"TXN-{next_number:08d}",
                "customer": customer,
                "transaction_type": "collection",
                "status": "completed",
                "amount": collection.amount,
                "balance_after": balance_after,
                "payment_method": "Cash",
                "visit_type": collection.visit_type,
                "collected_by": collection.collected_by,
                "note": collection.note,
                "transacted_at": collection.collected_at,
            },
        )
        next_number += 1


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0020_customer_profile_photo"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_deleted", models.BooleanField(db_index=True, default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("transaction_id", models.CharField(blank=True, max_length=24, unique=True)),
                ("transaction_type", models.CharField(choices=[("collection", "Collection")], default="collection", max_length=20)),
                ("status", models.CharField(choices=[("completed", "Completed"), ("cancelled", "Cancelled")], default="completed", max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("balance_after", models.DecimalField(decimal_places=2, max_digits=12)),
                ("payment_method", models.CharField(default="Cash", max_length=40)),
                ("visit_type", models.CharField(choices=[("shop", "Shop Visit"), ("home", "Home Visit"), ("office", "Office Collection")], max_length=20)),
                ("note", models.CharField(blank=True, max_length=220)),
                ("transacted_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("collected_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="transactions_collected", to=settings.AUTH_USER_MODEL)),
                ("collection_record", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="transaction", to="myapp.collectionrecord")),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transactions", to="myapp.customer")),
            ],
            options={
                "verbose_name": "Transaction",
                "verbose_name_plural": "Transactions",
                "ordering": ["-transacted_at", "-id"],
            },
        ),
        migrations.RunPython(create_transactions_for_existing_collections, migrations.RunPython.noop),
    ]
