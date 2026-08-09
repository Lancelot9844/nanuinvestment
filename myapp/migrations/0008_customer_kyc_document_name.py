from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0007_customer"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="kyc_document_name",
            field=models.CharField(blank=True, max_length=160),
        ),
    ]
