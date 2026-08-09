from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0008_customer_kyc_document_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyCollection",
            fields=[],
            options={
                "verbose_name": "Daily Collection",
                "verbose_name_plural": "Daily Collections",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("myapp.customer",),
        ),
    ]
