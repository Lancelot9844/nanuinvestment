from django.db import models


class TimestampedContent(models.Model):
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    published_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title


class NewsActivity(TimestampedContent):
    image = models.FileField(upload_to="news/", blank=True)

    class Meta(TimestampedContent.Meta):
        verbose_name = "News & Activity"
        verbose_name_plural = "News & Activities"


class Banner(models.Model):
    title = models.CharField(max_length=180)
    image = models.FileField(upload_to="banners/")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

    def __str__(self):
        return self.title


class Notice(TimestampedContent):
    document = models.FileField(upload_to="notices/", blank=True)

    class Meta(TimestampedContent.Meta):
        verbose_name = "Notice"
        verbose_name_plural = "Notices"


class Download(TimestampedContent):
    document = models.FileField(upload_to="downloads/")

    class Meta(TimestampedContent.Meta):
        verbose_name = "Download"
        verbose_name_plural = "Downloads"
