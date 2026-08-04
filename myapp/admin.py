from django.contrib import admin
from django.utils.html import format_html

from .models import Banner, Download, NewsActivity, Notice


admin.site.site_header = "Nanu Investment Admin"
admin.site.site_title = "Nanu Investment"
admin.site.index_title = "Website Management"


@admin.action(description="Mark selected items as active")
def mark_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected items as inactive")
def mark_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


class ContentAdminBase(admin.ModelAdmin):
    list_display = ("title", "status_badge", "published_at", "updated_at")
    list_filter = ("is_active", "published_at")
    search_fields = ("title", "description")
    ordering = ("-published_at", "-created_at")
    date_hierarchy = "published_at"
    list_per_page = 20
    actions = (mark_active, mark_inactive)
    fieldsets = (
        ("Content", {"fields": ("title", "description")}),
        ("Publishing", {"fields": ("published_at", "is_active")}),
    )

    def status_badge(self, obj):
        label = "Active" if obj.is_active else "Hidden"
        class_name = "status-active" if obj.is_active else "status-hidden"
        return format_html('<span class="admin-status {}">{}</span>', class_name, label)

    status_badge.short_description = "Status"


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "status_badge", "display_order", "image_preview", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
    ordering = ("display_order", "-created_at")
    list_editable = ("display_order",)
    list_per_page = 20
    actions = (mark_active, mark_inactive)
    fieldsets = (
        ("Banner", {"fields": ("title", "image", "display_order")}),
        ("Publishing", {"fields": ("is_active",)}),
    )

    def status_badge(self, obj):
        label = "Active" if obj.is_active else "Hidden"
        class_name = "status-active" if obj.is_active else "status-hidden"
        return format_html('<span class="admin-status {}">{}</span>', class_name, label)

    status_badge.short_description = "Status"

    def image_preview(self, obj):
        if not obj.image:
            return "-"
        return format_html('<a href="{}" target="_blank">View banner</a>', obj.image.url)

    image_preview.short_description = "Image"


@admin.register(NewsActivity)
class NewsActivityAdmin(ContentAdminBase):
    list_display = ("title", "status_badge", "published_at", "image_preview", "updated_at")
    fieldsets = ContentAdminBase.fieldsets + (
        ("Media", {"fields": ("image",)}),
    )

    def image_preview(self, obj):
        if not obj.image:
            return "-"
        return format_html('<a href="{}" target="_blank">View image</a>', obj.image.url)

    image_preview.short_description = "Image"


@admin.register(Notice)
class NoticeAdmin(ContentAdminBase):
    list_display = ("title", "status_badge", "published_at", "document_link", "updated_at")
    fieldsets = ContentAdminBase.fieldsets + (
        ("Document", {"fields": ("document",)}),
    )

    def document_link(self, obj):
        if not obj.document:
            return "-"
        return format_html('<a href="{}" target="_blank">Open file</a>', obj.document.url)

    document_link.short_description = "Document"


@admin.register(Download)
class DownloadAdmin(ContentAdminBase):
    list_display = ("title", "status_badge", "published_at", "document_link", "updated_at")
    fieldsets = ContentAdminBase.fieldsets + (
        ("Document", {"fields": ("document",)}),
    )

    def document_link(self, obj):
        return format_html('<a href="{}" target="_blank">Open file</a>', obj.document.url)

    document_link.short_description = "Document"
