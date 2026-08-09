from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0019_ebankingcredential"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="profile_photo",
            field=models.FileField(blank=True, upload_to="customer_profiles/"),
        ),
    ]
