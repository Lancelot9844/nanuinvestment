from pathlib import Path
import shutil

from django.conf import settings
from django.db import migrations


DEFAULT_BANNERS = (
    ("Trusted Financial Growth", "banner1.png", 1),
    ("Member First Approach", "banner2.png", 2),
    ("Reliable Partnership", "banner3.png", 3),
    ("Community Financial Support", "banner4.png", 4),
    ("Secure Savings Services", "banner5.png", 5),
    ("Growing Together", "banner6.png", 6),
)


def seed_default_banners(apps, schema_editor):
    Banner = apps.get_model("myapp", "Banner")
    media_banner_dir = Path(settings.MEDIA_ROOT) / "banners"
    media_banner_dir.mkdir(parents=True, exist_ok=True)

    for title, filename, display_order in DEFAULT_BANNERS:
        destination = media_banner_dir / filename
        source = Path(settings.BASE_DIR) / "templates" / filename

        if source.exists() and not destination.exists():
            shutil.copy2(source, destination)

        Banner.objects.get_or_create(
            title=title,
            defaults={
                "image": f"banners/{filename}",
                "display_order": display_order,
                "is_active": True,
            },
        )


def remove_default_banners(apps, schema_editor):
    Banner = apps.get_model("myapp", "Banner")
    Banner.objects.filter(title__in=[title for title, _, _ in DEFAULT_BANNERS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0004_add_banner_group_permissions"),
    ]

    operations = [
        migrations.RunPython(seed_default_banners, remove_default_banners),
    ]
