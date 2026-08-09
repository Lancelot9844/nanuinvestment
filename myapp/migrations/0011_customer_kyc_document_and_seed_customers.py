from django.db import migrations, models
import django.db.models.deletion


def seed_dummy_customers(apps, schema_editor):
    Customer = apps.get_model("myapp", "Customer")

    dummy_customers = [
        {
            "customer_id": "CUST-DUMMY-001",
            "first_name": "Ram",
            "last_name": "Sah",
            "phone_number": "9800000001",
            "email": "ram.sah@example.com",
            "citizenship_number": "CTZ-1001",
            "address": "Main Road, Ward 01",
            "account_type": "savings",
            "opening_balance": 2500,
            "nominee_name": "Sita Sah",
            "nominee_phone": "9810000001",
            "kyc_document_name": "",
            "kyc_status": "approved",
        },
        {
            "customer_id": "CUST-DUMMY-002",
            "first_name": "Sita",
            "last_name": "Devi",
            "phone_number": "9800000002",
            "email": "sita.devi@example.com",
            "citizenship_number": "CTZ-1002",
            "address": "Market Area, Ward 03",
            "account_type": "current",
            "opening_balance": 5000,
            "nominee_name": "Hari Devi",
            "nominee_phone": "9810000002",
            "kyc_document_name": "",
            "kyc_status": "pending",
        },
        {
            "customer_id": "CUST-DUMMY-003",
            "first_name": "Amit",
            "last_name": "Chaudhary",
            "phone_number": "9800000003",
            "email": "amit.chaudhary@example.com",
            "citizenship_number": "CTZ-1003",
            "address": "Bus Park, Ward 05",
            "account_type": "savings",
            "opening_balance": 1500,
            "nominee_name": "Mina Chaudhary",
            "nominee_phone": "9810000003",
            "kyc_document_name": "",
            "kyc_status": "draft",
        },
        {
            "customer_id": "CUST-DUMMY-004",
            "first_name": "Maya",
            "last_name": "Kumari",
            "phone_number": "9800000004",
            "email": "maya.kumari@example.com",
            "citizenship_number": "CTZ-1004",
            "address": "School Chowk, Ward 02",
            "account_type": "fixed",
            "opening_balance": 25000,
            "nominee_name": "Anil Kumari",
            "nominee_phone": "9810000004",
            "kyc_document_name": "",
            "kyc_status": "approved",
        },
        {
            "customer_id": "CUST-DUMMY-005",
            "first_name": "Nabin",
            "last_name": "Yadav",
            "phone_number": "9800000005",
            "email": "nabin.yadav@example.com",
            "citizenship_number": "CTZ-1005",
            "address": "Temple Road, Ward 04",
            "account_type": "recurring",
            "opening_balance": 1000,
            "nominee_name": "Rina Yadav",
            "nominee_phone": "9810000005",
            "kyc_document_name": "",
            "kyc_status": "pending",
        },
    ]

    for data in dummy_customers:
        Customer.objects.get_or_create(customer_id=data["customer_id"], defaults=data)


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0010_ticket"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerKYCDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("citizenship_front", "Citizenship Front"),
                            ("citizenship_back", "Citizenship Back"),
                            ("passport_photo", "Passport Size Photo"),
                            ("signature", "Signature"),
                            ("address_proof", "Address Proof"),
                            ("other", "Other"),
                        ],
                        max_length=40,
                    ),
                ),
                ("document_name", models.CharField(help_text="Label shown for this uploaded document.", max_length=160)),
                ("document", models.FileField(upload_to="customer_kyc/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "customer",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="kyc_documents", to="myapp.customer"),
                ),
            ],
            options={
                "verbose_name": "KYC Document",
                "verbose_name_plural": "KYC Documents",
                "ordering": ["document_type", "document_name"],
            },
        ),
        migrations.RunPython(seed_dummy_customers, migrations.RunPython.noop),
    ]
