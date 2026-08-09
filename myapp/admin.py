from decimal import Decimal
from io import BytesIO
from urllib.parse import quote

from django.contrib import admin, messages
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.html import format_html, format_html_join

from .forms import DailyCollectionEntryForm, StaffProfileForm
from .models import (
    AdminProfile,
    Banner,
    CollectionRecord,
    Customer,
    CustomerKYCDocument,
    DailyCollection,
    Download,
    EBankingCredential,
    NewsActivity,
    Notice,
    RecycleBinItem,
    Ticket,
    Transaction,
    WebsitePopup,
)


admin.site.site_header = "Nanu Investment Admin"
admin.site.site_title = "Nanu Investment"
admin.site.index_title = "Website Management"


@admin.action(description="Move selected records to Recycle Bin")
def move_selected_to_recycle_bin(modeladmin, request, queryset):
    moved_count = modeladmin.delete_queryset(request, queryset)
    if moved_count:
        modeladmin.message_user(
            request,
            f"{moved_count} record(s) moved to the Recycle Bin.",
            messages.SUCCESS,
        )


class RecycleAdminMixin:
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        if self.has_delete_permission(request):
            actions["move_selected_to_recycle_bin"] = (
                move_selected_to_recycle_bin,
                "move_selected_to_recycle_bin",
                move_selected_to_recycle_bin.short_description,
            )
        return actions

    def delete_model(self, request, obj):
        RecycleBinItem.recycle(obj, deleted_by=request.user)

    def delete_queryset(self, request, queryset):
        moved_count = 0
        skipped_current_user = False
        for obj in queryset:
            if isinstance(obj, get_user_model()) and obj.pk == request.user.pk:
                skipped_current_user = True
                continue
            count, _ = RecycleBinItem.recycle(obj, deleted_by=request.user)
            moved_count += count

        if skipped_current_user:
            self.message_user(
                request,
                "Your currently signed-in account was not moved to the Recycle Bin.",
                messages.WARNING,
            )
        return moved_count


class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    extra = 0
    max_num = 1
    fields = ("phone_number", "address", "photo", "photo_preview")
    readonly_fields = ("photo_preview",)

    def photo_preview(self, obj):
        if not obj or not obj.photo:
            return "-"
        return format_html(
            '<img src="{}" alt="" style="width:72px;height:72px;object-fit:cover;border-radius:50%;">',
            obj.photo.url,
        )

    photo_preview.short_description = "Current photo"

    def _is_own_profile(self, request, obj=None):
        return bool(obj and obj.pk == request.user.pk)

    def has_view_permission(self, request, obj=None):
        return self._is_own_profile(request, obj) or super().has_view_permission(request, obj)

    def has_add_permission(self, request, obj=None):
        return self._is_own_profile(request, obj) or super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return self._is_own_profile(request, obj) or super().has_change_permission(request, obj)

    def get_extra(self, request, obj=None, **kwargs):
        if self._is_own_profile(request, obj) and obj and not hasattr(obj, "admin_profile"):
            return 1
        return super().get_extra(request, obj, **kwargs)


User = get_user_model()
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(RecycleAdminMixin, DjangoUserAdmin):
    inlines = (AdminProfileInline,)
    readonly_fields = DjangoUserAdmin.readonly_fields + ("password_change_action",)
    fieldsets = (
        (None, {"fields": ("username", "password_change_action")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    staff_profile_fieldsets = (
        (None, {"fields": ("username", "password_change_action")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
    )

    def _is_own_profile(self, request, obj=None):
        return bool(obj and obj.pk == request.user.pk)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        user_type = ContentType.objects.get_for_model(User)
        recycled_user_ids = RecycleBinItem.objects.filter(
            content_type=user_type,
        ).values("object_id")
        return queryset.exclude(pk__in=recycled_user_ids)

    def get_fieldsets(self, request, obj=None):
        if obj and self._is_own_profile(request, obj) and not request.user.is_superuser:
            return self.staff_profile_fieldsets
        return super().get_fieldsets(request, obj)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and self._is_own_profile(request, obj):
            AdminProfile.objects.get_or_create(user=obj)
        return super().change_view(request, object_id, form_url, extra_context)

    def has_view_permission(self, request, obj=None):
        return self._is_own_profile(request, obj) or super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return self._is_own_profile(request, obj) or super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.pk == request.user.pk:
            return False
        return super().has_delete_permission(request, obj)

    def password_change_action(self, obj):
        if not obj or not obj.pk:
            return "Save this user before changing password."

        url = reverse("admin:auth_user_password_change", args=[obj.pk])
        return format_html(
            '<a class="button" href="{}">Change password</a>'
            '<p class="help">Password is hidden for security. Use this button only when you need to set a new password.</p>',
            url,
        )

    password_change_action.short_description = "Password"


@admin.action(description="Mark selected items as active")
def mark_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected items as inactive")
def mark_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description="Send selected customers for KYC approval")
def send_for_kyc_approval(modeladmin, request, queryset):
    queryset.exclude(kyc_status=Customer.KycStatus.APPROVED).update(
        kyc_status=Customer.KycStatus.PENDING,
        submitted_for_approval_at=timezone.now(),
    )


@admin.action(description="Approve selected customer KYC")
def approve_customer_kyc(modeladmin, request, queryset):
    queryset.update(
        kyc_status=Customer.KycStatus.APPROVED,
        approved_at=timezone.now(),
        approved_by=request.user,
    )


@admin.register(Customer)
class CustomerAdmin(RecycleAdminMixin, admin.ModelAdmin):
    list_display = (
        "customer_id",
        "full_name_display",
        "phone_number",
        "account_type",
        "opening_balance",
        "kyc_document_count",
        "kyc_status_badge",
        "created_at",
    )
    list_filter = ("kyc_status", "account_type", "created_at")
    search_fields = (
        "customer_id",
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "citizenship_number",
    )
    autocomplete_fields = ("user",)
    readonly_fields = (
        "customer_id",
        "submitted_for_approval_at",
        "approved_at",
        "approved_by",
        "kyc_document_link",
        "customer_login_info",
        "password_reset_action",
        "profile_photo_preview",
    )
    actions = (send_for_kyc_approval, approve_customer_kyc)
    ordering = ("-created_at",)
    list_per_page = 25
    fieldsets = (
        ("Customer Account", {"fields": ("customer_id", "user", "customer_login_info", "password_reset_action", "first_name", "last_name", "phone_number", "email", "profile_photo", "profile_photo_preview", "date_of_birth")}),
        ("KYC Information", {"fields": ("citizenship_number", "address", "kyc_status")}),
        ("Bank Account", {"fields": ("account_type", "opening_balance")}),
        ("Nominee", {"fields": ("nominee_name", "nominee_phone")}),
        ("Approval", {"fields": ("submitted_for_approval_at", "approved_at", "approved_by")}),
    )
    inlines = ()

    def get_urls(self):
        custom_urls = [
            path(
                "<int:customer_id>/reset-password/",
                self.admin_site.admin_view(self.reset_customer_password_view),
                name="myapp_customer_reset_password",
            ),
        ]
        return custom_urls + super().get_urls()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.user:
            return

        password = get_random_string(12)
        username = obj.customer_id.lower()
        user = get_user_model().objects.create_user(
            username=username,
            email=obj.email,
            password=password,
            first_name=obj.first_name,
            last_name=obj.last_name,
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )
        obj.user = user
        obj.save(update_fields=("user",))
        EBankingCredential.objects.update_or_create(
            customer=obj,
            defaults={
                "user": user,
                "username": username,
                "temporary_password": password,
                "password_changed_at": None,
            },
        )
        self.message_user(
            request,
            f"Customer login created. Username: {username} Password: {password}",
            messages.SUCCESS,
        )

    def reset_customer_password_view(self, request, customer_id):
        customer = get_object_or_404(Customer, pk=customer_id)
        if not self.has_change_permission(request, customer):
            raise PermissionDenied

        if not customer.user:
            self.message_user(request, "This customer does not have a login account yet.", messages.ERROR)
            return redirect("admin:myapp_customer_change", customer.pk)

        if request.method == "POST":
            form = SetPasswordForm(customer.user, request.POST)
            if form.is_valid():
                form.save()
                EBankingCredential.objects.update_or_create(
                    customer=customer,
                    defaults={
                        "user": customer.user,
                        "username": customer.user.get_username(),
                        "temporary_password": form.cleaned_data["new_password1"],
                        "password_changed_at": None,
                    },
                )
                self.message_user(request, "Customer password has been reset.", messages.SUCCESS)
                return redirect("admin:myapp_customer_change", customer.pk)
        else:
            form = SetPasswordForm(customer.user)

        context = {
            **self.admin_site.each_context(request),
            "title": "Reset Customer Password",
            "opts": self.model._meta,
            "customer": customer,
            "form": form,
        }
        return TemplateResponse(request, "admin/customer_password_reset.html", context)

    def full_name_display(self, obj):
        return obj.full_name

    full_name_display.short_description = "Customer"

    def kyc_status_badge(self, obj):
        class_name = {
            Customer.KycStatus.DRAFT: "status-hidden",
            Customer.KycStatus.PENDING: "status-pending",
            Customer.KycStatus.APPROVED: "status-active",
            Customer.KycStatus.REJECTED: "status-hidden",
        }.get(obj.kyc_status, "status-hidden")
        return format_html('<span class="admin-status {}">{}</span>', class_name, obj.get_kyc_status_display())

    kyc_status_badge.short_description = "KYC Status"

    def kyc_document_link(self, obj):
        if not obj or not obj.kyc_document:
            return "-"
        return format_html('<a href="{}" target="_blank">Open KYC document</a>', obj.kyc_document.url)

    kyc_document_link.short_description = "Uploaded KYC document"

    def profile_photo_preview(self, obj):
        if not obj or not obj.profile_photo:
            return "-"
        return format_html(
            '<img src="{}" alt="" style="width:72px;height:72px;object-fit:cover;border-radius:50%;">',
            obj.profile_photo.url,
        )

    profile_photo_preview.short_description = "Current profile photo"

    def kyc_document_count(self, obj):
        count = obj.kyc_documents.count()
        return f"{count} document" if count == 1 else f"{count} documents"

    kyc_document_count.short_description = "KYC Documents"

    def customer_login_info(self, obj):
        if not obj or not obj.user:
            return "A login will be created automatically after saving this customer."
        credential = getattr(obj, "ebanking_credential", None)
        if credential and credential.temporary_password:
            return format_html(
                "Username: <strong>{}</strong><br>Password: <strong>{}</strong>",
                credential.username,
                credential.temporary_password,
            )
        return format_html("Username: <strong>{}</strong>", obj.user.get_username())

    customer_login_info.short_description = "Customer login"

    def password_reset_action(self, obj):
        if not obj or not obj.pk or not obj.user:
            return "Save this customer first."
        url = reverse("admin:myapp_customer_reset_password", args=(obj.pk,))
        return format_html('<a class="button" href="{}">Reset customer password</a>', url)

    password_reset_action.short_description = "Password reset"


@admin.register(EBankingCredential)
class EBankingCredentialAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "phone_number",
        "email_address",
        "username",
        "temporary_password_display",
        "password_status",
        "contact_actions",
        "updated_at",
    )
    search_fields = (
        "customer__customer_id",
        "customer__first_name",
        "customer__last_name",
        "customer__phone_number",
        "customer__email",
        "username",
    )
    readonly_fields = (
        "customer",
        "user",
        "phone_number",
        "email_address",
        "username",
        "temporary_password",
        "password_changed_at",
        "contact_actions",
        "created_at",
        "updated_at",
        "customer_link",
    )
    fieldsets = (
        ("Customer", {"fields": ("customer_link", "customer", "user")}),
        ("Contact", {"fields": ("phone_number", "email_address", "contact_actions")}),
        ("Login", {"fields": ("username", "temporary_password", "password_changed_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    list_per_page = 25

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def customer_link(self, obj):
        if not obj or not obj.customer_id:
            return "-"
        url = reverse("admin:myapp_customer_change", args=(obj.customer_id,))
        return format_html('<a href="{}">{}</a>', url, obj.customer)

    customer_link.short_description = "Customer profile"

    def temporary_password_display(self, obj):
        return obj.temporary_password or "Changed by customer"

    temporary_password_display.short_description = "Password"

    def phone_number(self, obj):
        return obj.customer.phone_number or "-"

    phone_number.short_description = "Phone"

    def email_address(self, obj):
        return obj.customer.email or "-"

    email_address.short_description = "Email"

    def contact_actions(self, obj):
        actions = []
        customer = obj.customer
        message = (
            f"Nanu Investment E-Banking login. "
            f"Username: {obj.username} Password: {obj.temporary_password or '[changed by customer]'}"
        )
        encoded_subject = quote("Nanu Investment E-Banking Login")
        encoded_message = quote(message)
        if customer.email:
            actions.append(
                format_html(
                    '<a class="button ebanking-contact-button" href="mailto:{}?subject={}&body={}">Send Email</a>',
                    customer.email,
                    encoded_subject,
                    encoded_message,
                )
            )
        if customer.phone_number:
            actions.append(
                format_html(
                    '<a class="button ebanking-contact-button" href="sms:{}?body={}">Send SMS</a>',
                    customer.phone_number,
                    encoded_message,
                )
            )
            actions.append(
                format_html(
                    '<a class="button ebanking-contact-button" href="tel:{}">Call</a>',
                    customer.phone_number,
                )
            )
        if not actions:
            return "-"
        return format_html(
            '<span class="ebanking-contact-actions">{}</span>',
            format_html_join("", "{}", ((action,) for action in actions)),
        )

    contact_actions.short_description = "Send"

    def password_status(self, obj):
        if obj.password_changed_at:
            return format_html('<span class="admin-status status-active">{}</span>', "Changed")
        return format_html('<span class="admin-status status-pending">{}</span>', "Temporary")

    password_status.short_description = "Status"


class CustomerKYCDocumentInline(admin.TabularInline):
    model = CustomerKYCDocument
    extra = 1
    fields = ("document_type", "document_name", "document", "document_link", "uploaded_at")
    readonly_fields = ("document_link", "uploaded_at")

    def document_link(self, obj):
        if not obj or not obj.document:
            return "-"
        return format_html('<a href="{}" target="_blank">{}</a>', obj.document.url, obj.document_name)

    document_link.short_description = "Uploaded file"


CustomerAdmin.inlines = (CustomerKYCDocumentInline,)


def sync_collection_transaction(collection):
    collected_total = (
        collection.customer.collections.filter(is_deleted=False)
        .aggregate(total=models.Sum("amount"))["total"]
        or Decimal("0.00")
    )
    balance_after = collection.customer.opening_balance + collected_total
    transaction_obj, _ = Transaction.objects.update_or_create(
        collection_record=collection,
        defaults={
            "customer": collection.customer,
            "amount": collection.amount,
            "balance_after": balance_after,
            "payment_method": "Cash",
            "status": Transaction.Status.COMPLETED,
            "visit_type": collection.visit_type,
            "collected_by": collection.collected_by,
            "note": collection.note,
            "transacted_at": collection.collected_at,
        },
    )
    return transaction_obj


def load_receipt_font(size, bold=False):
    from PIL import ImageFont

    font_name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(font_name, size)
    except OSError:
        return ImageFont.load_default(size=size)


def draw_receipt_row(draw, y, label, value, label_font, value_font, color="#173b35", muted="#697d78"):
    draw.text((88, y), label, fill=muted, font=label_font)
    draw.text((330, y), str(value), fill=color, font=value_font)
    return y + 34


def build_receipt_image(transaction_obj):
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise RuntimeError("Pillow is required to generate PDF/JPG bills. Install it with: python -m pip install Pillow==11.3.0") from exc

    customer = transaction_obj.customer
    width, height = 1240, 1754
    image = Image.new("RGB", (width, height), "#f3f7f6")
    draw = ImageDraw.Draw(image)

    nav = "#173b35"
    accent = "#c73535"
    text = "#152724"
    muted = "#657b76"
    line = "#d6e3df"

    title_font = load_receipt_font(52, bold=True)
    subtitle_font = load_receipt_font(28)
    heading_font = load_receipt_font(28, bold=True)
    label_font = load_receipt_font(22, bold=True)
    value_font = load_receipt_font(25)
    amount_font = load_receipt_font(32, bold=True)
    small_font = load_receipt_font(20)

    x0, y0, x1, y1 = 70, 70, width - 70, height - 70
    draw.rounded_rectangle((x0, y0, x1, y1), radius=22, fill="white", outline=line, width=2)
    draw.rectangle((x0, y0, x1, y0 + 150), fill=nav)
    draw.text((105, 105), "Nanu Investment", fill="white", font=title_font)
    draw.text((108, 170), "Collection Transaction Bill", fill="#dfece9", font=subtitle_font)
    draw.rounded_rectangle((820, 110, 1135, 205), radius=14, fill="white")
    draw.text((850, 128), "RECEIPT NO.", fill=muted, font=small_font)
    draw.text((850, 158), transaction_obj.transaction_id, fill=accent, font=heading_font)

    y = 270
    draw.text((88, y), "Transaction Summary", fill=nav, font=heading_font)
    draw.line((88, y + 44, 1152, y + 44), fill=line, width=2)
    y += 75
    summary = [
        ("Date", transaction_obj.transacted_at.strftime("%d %b %Y, %H:%M")),
        ("Status", transaction_obj.get_status_display()),
        ("Payment Method", transaction_obj.payment_method),
        ("Collection Location", transaction_obj.get_visit_type_display()),
    ]
    for index, (label, value) in enumerate(summary):
        left = 88 if index % 2 == 0 else 620
        top = y + (index // 2) * 92
        draw.rounded_rectangle((left, top, left + 484, top + 66), radius=10, fill="#f8fbfa", outline=line)
        draw.text((left + 20, top + 12), label.upper(), fill=muted, font=small_font)
        draw.text((left + 20, top + 37), str(value), fill=text, font=value_font)

    y += 220
    draw.text((88, y), "Customer Details", fill=nav, font=heading_font)
    draw.text((620, y), "Collection Details", fill=nav, font=heading_font)
    draw.line((88, y + 44, 1152, y + 44), fill=line, width=2)
    left_y = right_y = y + 76
    for label, value in (
        ("Name", customer.full_name),
        ("Account Number", customer.customer_id),
        ("Phone", customer.phone_number),
        ("Account Type", customer.get_account_type_display()),
    ):
        draw.text((88, left_y), label, fill=muted, font=label_font)
        draw.text((300, left_y), str(value), fill=text, font=value_font)
        left_y += 42

    for label, value in (
        ("Collected By", transaction_obj.collected_by or "-"),
        ("Transaction Type", transaction_obj.get_transaction_type_display()),
        ("Remarks", transaction_obj.note or "-"),
    ):
        draw.text((620, right_y), label, fill=muted, font=label_font)
        draw.text((840, right_y), str(value), fill=text, font=value_font)
        right_y += 42

    y = 890
    draw.rounded_rectangle((88, y, 1152, y + 240), radius=16, fill="#f8fbfa", outline=line, width=2)
    draw.text((126, y + 36), "Collected Amount", fill=muted, font=label_font)
    draw.text((126, y + 78), f"Rs {transaction_obj.amount:.2f}", fill=accent, font=amount_font)
    draw.line((126, y + 136, 1114, y + 136), fill=line, width=2)
    draw.text((126, y + 164), "Total Balance After Transaction", fill=muted, font=label_font)
    draw.text((715, y + 156), f"Rs {transaction_obj.balance_after:.2f}", fill=nav, font=amount_font)

    y = 1240
    draw.line((120, y, 480, y), fill=nav, width=2)
    draw.text((190, y + 18), "Customer Signature", fill=text, font=label_font)
    draw.line((760, y, 1120, y), fill=nav, width=2)
    draw.text((820, y + 18), "Authorized Signature", fill=text, font=label_font)
    draw.text((88, 1595), "This bill was generated by Nanu Investment transaction system.", fill=muted, font=small_font)
    draw.text((88, 1628), "Please keep this receipt for your records.", fill=muted, font=small_font)
    return image


def build_receipt_pdf(transaction_obj):
    buffer = BytesIO()
    image = build_receipt_image(transaction_obj)
    image.save(buffer, format="PDF", resolution=150.0)
    return buffer.getvalue()


def build_receipt_jpg(transaction_obj):
    buffer = BytesIO()
    image = build_receipt_image(transaction_obj)
    image.save(buffer, format="JPEG", quality=95, optimize=True)
    return buffer.getvalue()


@admin.register(DailyCollection)
class DailyCollectionAdmin(admin.ModelAdmin):
    change_list_template = "admin/daily_collection_changelist.html"
    list_display = (
        "account_number",
        "full_name_display",
        "phone_number",
        "citizenship_number",
        "account_type",
        "opening_balance",
        "current_account_amount",
        "kyc_status_badge",
        "add_collection_action",
    )
    list_display_links = None
    list_filter = ("account_type", "kyc_status")
    search_fields = (
        "customer_id",
        "first_name",
        "last_name",
        "phone_number",
        "citizenship_number",
    )
    search_help_text = "Name, phone, account number, or citizenship number"
    ordering = ("first_name", "last_name")
    list_per_page = 25

    def get_urls(self):
        custom_urls = [
            path(
                "<int:customer_id>/collect/",
                self.admin_site.admin_view(self.collect_view),
                name="myapp_dailycollection_collect",
            ),
        ]
        return custom_urls + super().get_urls()

    def get_queryset(self, request):
        money_field = models.DecimalField(max_digits=16, decimal_places=2)
        return super().get_queryset(request).annotate(
            collected_total=Coalesce(
                models.Sum(
                    "collections__amount",
                    filter=models.Q(collections__is_deleted=False),
                ),
                models.Value(Decimal("0.00")),
                output_field=money_field,
            ),
        )

    def collect_view(self, request, customer_id):
        if not request.user.has_perm("myapp.add_collectionrecord"):
            raise PermissionDenied

        customer = get_object_or_404(Customer, pk=customer_id)
        if request.method == "POST":
            form = DailyCollectionEntryForm(request.POST)
            if form.is_valid():
                collection = form.save(commit=False)
                collection.customer = customer
                collection.collected_by = request.user
                collection.collected_at = timezone.now()
                collection.save()
                transaction_obj = sync_collection_transaction(collection)
                self.message_user(
                    request,
                    f"Rs {collection.amount:.2f} collected for {customer.full_name}. Transaction {transaction_obj.transaction_id} generated.",
                    messages.SUCCESS,
                )
                return redirect("admin:myapp_transaction_receipt", transaction_id=transaction_obj.pk)
        else:
            form = DailyCollectionEntryForm()

        collected_total = customer.collections.aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
        context = {
            **self.admin_site.each_context(request),
            "title": "Add Daily Collection",
            "opts": self.model._meta,
            "customer": customer,
            "form": form,
            "collected_total": collected_total,
            "account_total": customer.opening_balance + collected_total,
            "recent_collections": customer.collections.select_related("collected_by")[:8],
        }
        return TemplateResponse(request, "admin/daily_collection_entry.html", context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def full_name_display(self, obj):
        return obj.full_name

    full_name_display.short_description = "Customer"

    @admin.display(description="Account number", ordering="customer_id")
    def account_number(self, obj):
        return obj.customer_id

    @admin.display(description="Total amount")
    def current_account_amount(self, obj):
        return obj.opening_balance + obj.collected_total

    @admin.display(description="Collection")
    def add_collection_action(self, obj):
        url = reverse("admin:myapp_dailycollection_collect", args=(obj.pk,))
        return format_html('<a class="button" href="{}">Add Collection</a>', url)

    def kyc_status_badge(self, obj):
        class_name = "status-active" if obj.kyc_status == Customer.KycStatus.APPROVED else "status-pending"
        return format_html('<span class="admin-status {}">{}</span>', class_name, obj.get_kyc_status_display())

    kyc_status_badge.short_description = "KYC Status"


@admin.register(CollectionRecord)
class CollectionRecordAdmin(RecycleAdminMixin, admin.ModelAdmin):
    list_display = ("customer", "amount", "visit_type", "collected_by", "collected_at", "transaction_link", "note")
    list_filter = ("visit_type", "collected_by", "collected_at")
    search_fields = ("customer__first_name", "customer__last_name", "customer__customer_id", "note")
    autocomplete_fields = ("customer", "collected_by")
    date_hierarchy = "collected_at"
    ordering = ("-collected_at",)
    list_per_page = 25
    fieldsets = (
        ("Collection", {"fields": ("customer", "amount", "visit_type", "collected_by", "collected_at")}),
        ("Visit Note", {"fields": ("note",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(customer__is_deleted=False)

    def save_model(self, request, obj, form, change):
        if not obj.collected_by_id:
            obj.collected_by = request.user
        super().save_model(request, obj, form, change)
        sync_collection_transaction(obj)

    def transaction_link(self, obj):
        transaction_obj = getattr(obj, "transaction", None)
        if not transaction_obj:
            return "-"
        url = reverse("admin:myapp_transaction_receipt", args=(transaction_obj.pk,))
        return format_html('<a class="button" href="{}">Receipt</a>', url)

    transaction_link.short_description = "Transaction"


@admin.register(Transaction)
class TransactionAdmin(RecycleAdminMixin, admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "customer",
        "amount",
        "balance_after",
        "status",
        "payment_method",
        "collected_by",
        "transacted_at",
        "receipt_actions",
    )
    list_filter = ("transaction_type", "status", "payment_method", "collected_by", "transacted_at")
    search_fields = (
        "transaction_id",
        "customer__customer_id",
        "customer__first_name",
        "customer__last_name",
        "customer__phone_number",
        "note",
    )
    readonly_fields = (
        "transaction_id",
        "collection_record",
        "customer",
        "transaction_type",
        "amount",
        "balance_after",
        "status",
        "payment_method",
        "visit_type",
        "collected_by",
        "note",
        "transacted_at",
        "created_at",
        "receipt_actions",
    )
    fields = readonly_fields
    date_hierarchy = "transacted_at"
    ordering = ("-transacted_at", "-id")
    list_per_page = 30

    def get_urls(self):
        custom_urls = [
            path(
                "<int:transaction_id>/receipt/",
                self.admin_site.admin_view(self.receipt_view),
                name="myapp_transaction_receipt",
            ),
            path(
                "<int:transaction_id>/download/pdf/",
                self.admin_site.admin_view(self.download_pdf_view),
                name="myapp_transaction_download_pdf",
            ),
            path(
                "<int:transaction_id>/download/jpg/",
                self.admin_site.admin_view(self.download_jpg_view),
                name="myapp_transaction_download_jpg",
            ),
        ]
        return custom_urls + super().get_urls()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def receipt_actions(self, obj):
        if not obj or not obj.pk:
            return "-"
        receipt_url = reverse("admin:myapp_transaction_receipt", args=(obj.pk,))
        pdf_url = reverse("admin:myapp_transaction_download_pdf", args=(obj.pk,))
        jpg_url = reverse("admin:myapp_transaction_download_jpg", args=(obj.pk,))
        return format_html(
            '<span class="transaction-actions"><a class="button" href="{}">Print</a>'
            '<a class="button" href="{}">PDF</a>'
            '<a class="button" href="{}">JPG</a></span>',
            receipt_url,
            pdf_url,
            jpg_url,
        )

    receipt_actions.short_description = "Bill"

    def receipt_view(self, request, transaction_id):
        transaction_obj = get_object_or_404(Transaction, pk=transaction_id)
        if not self.has_view_permission(request, transaction_obj):
            raise PermissionDenied
        context = {
            **self.admin_site.each_context(request),
            "title": f"Receipt {transaction_obj.transaction_id}",
            "transaction": transaction_obj,
        }
        return TemplateResponse(request, "admin/transaction_receipt.html", context)

    def download_jpg_view(self, request, transaction_id):
        transaction_obj = get_object_or_404(Transaction, pk=transaction_id)
        if not self.has_view_permission(request, transaction_obj):
            raise PermissionDenied
        response = HttpResponse(build_receipt_jpg(transaction_obj), content_type="image/jpeg")
        response["Content-Disposition"] = f'attachment; filename="{transaction_obj.transaction_id}.jpg"'
        return response

    def download_pdf_view(self, request, transaction_id):
        transaction_obj = get_object_or_404(Transaction, pk=transaction_id)
        if not self.has_view_permission(request, transaction_obj):
            raise PermissionDenied
        response = HttpResponse(build_receipt_pdf(transaction_obj), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{transaction_obj.transaction_id}.pdf"'
        return response


@admin.action(description="Mark selected tickets complete as staff")
def mark_tickets_staff_completed(modeladmin, request, queryset):
    queryset.exclude(status=Ticket.Status.VERIFIED_COMPLETED).update(
        status=Ticket.Status.STAFF_COMPLETED,
        staff_completed_at=timezone.now(),
    )


@admin.action(description="Admin verify selected tickets as completed")
def verify_tickets_completed(modeladmin, request, queryset):
    queryset.filter(status=Ticket.Status.STAFF_COMPLETED).update(
        status=Ticket.Status.VERIFIED_COMPLETED,
        verified_by=request.user,
        verified_at=timezone.now(),
    )


@admin.action(description="Admin return selected tickets as not completed")
def return_tickets_not_completed(modeladmin, request, queryset):
    queryset.filter(status=Ticket.Status.STAFF_COMPLETED).update(
        status=Ticket.Status.NOT_COMPLETED,
        verified_by=request.user,
        verified_at=timezone.now(),
    )


@admin.register(Ticket)
class TicketAdmin(RecycleAdminMixin, admin.ModelAdmin):
    list_display = (
        "title",
        "customer",
        "priority",
        "status_badge",
        "created_by",
        "assigned_to",
        "staff_completed_at",
        "verified_at",
    )
    list_filter = ("status", "priority", "assigned_to", "customer", "created_at")
    search_fields = (
        "title",
        "description",
        "customer__customer_id",
        "customer__first_name",
        "customer__last_name",
        "staff_completion_note",
        "admin_verification_reason",
    )
    autocomplete_fields = ("customer", "assigned_to")
    readonly_fields = ("created_by", "staff_completed_at", "verified_by", "verified_at", "created_at", "updated_at")
    actions = (mark_tickets_staff_completed, verify_tickets_completed, return_tickets_not_completed)
    ordering = ("-created_at",)
    list_per_page = 25
    fieldsets = (
        ("Ticket", {"fields": ("customer", "title", "description", "priority", "status")}),
        ("Assignment", {"fields": ("created_by", "assigned_to")}),
        ("Staff Completion", {"fields": ("staff_completion_note", "staff_completed_at")}),
        ("Admin Verification", {"fields": ("admin_verification_reason", "verified_by", "verified_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(models.Q(created_by=request.user) | models.Q(assigned_to=request.user))

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        if obj.assigned_to and obj.status in (Ticket.Status.OPEN, Ticket.Status.NOT_COMPLETED):
            obj.status = Ticket.Status.ASSIGNED
        if obj.status == Ticket.Status.STAFF_COMPLETED and not obj.staff_completed_at:
            obj.staff_completed_at = timezone.now()
        if obj.status in (Ticket.Status.VERIFIED_COMPLETED, Ticket.Status.NOT_COMPLETED):
            obj.verified_by = request.user
            if not obj.verified_at:
                obj.verified_at = timezone.now()
        super().save_model(request, obj, form, change)

    def status_badge(self, obj):
        class_name = {
            Ticket.Status.OPEN: "status-pending",
            Ticket.Status.ASSIGNED: "status-pending",
            Ticket.Status.STAFF_COMPLETED: "status-pending",
            Ticket.Status.VERIFIED_COMPLETED: "status-active",
            Ticket.Status.NOT_COMPLETED: "status-hidden",
        }.get(obj.status, "status-hidden")
        return format_html('<span class="admin-status {}">{}</span>', class_name, obj.get_status_display())

    status_badge.short_description = "Status"


class ContentAdminBase(RecycleAdminMixin, admin.ModelAdmin):
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
class BannerAdmin(RecycleAdminMixin, admin.ModelAdmin):
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


@admin.register(WebsitePopup)
class WebsitePopupAdmin(RecycleAdminMixin, admin.ModelAdmin):
    list_display = ("title", "status_badge", "display_order", "popup_file_preview", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "message")
    ordering = ("display_order", "-created_at")
    list_editable = ("display_order",)
    actions = (mark_active, mark_inactive)
    fieldsets = (
        ("Popup Content", {"fields": ("title", "image")}),
        ("Publishing", {"fields": ("is_active", "display_order")}),
    )

    def status_badge(self, obj):
        label = "Active" if obj.is_active else "Hidden"
        class_name = "status-active" if obj.is_active else "status-hidden"
        return format_html('<span class="admin-status {}">{}</span>', class_name, label)

    status_badge.short_description = "Status"

    def popup_file_preview(self, obj):
        if not obj.image:
            return "-"
        return format_html('<a href="{}" target="_blank">Open uploaded file</a>', obj.image.url)

    popup_file_preview.short_description = "Popup file"


@admin.register(RecycleBinItem)
class RecycleBinAdmin(admin.ModelAdmin):
    list_display = ("object_label", "record_type", "deleted_by", "deleted_at", "record_status")
    list_filter = ("content_type", "deleted_at", "deleted_by")
    search_fields = ("object_label", "content_type__model", "deleted_by__username")
    readonly_fields = (
        "object_label",
        "record_type",
        "object_id",
        "deleted_by",
        "deleted_at",
        "record_status",
    )
    fields = readonly_fields
    actions = ("restore_selected", "permanently_delete_selected")
    date_hierarchy = "deleted_at"
    list_per_page = 30

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("content_type", "deleted_by")

    def record_type(self, obj):
        return obj.content_type.name.title()

    record_type.short_description = "Record type"

    def record_status(self, obj):
        return "Available" if obj.get_recycled_object() is not None else "Original record missing"

    record_status.short_description = "Status"

    @admin.action(description="Restore selected records")
    def restore_selected(self, request, queryset):
        restored_count = 0
        for item in queryset:
            restored_count += int(item.restore_object())
        self.message_user(
            request,
            f"{restored_count} record(s) restored to their original section.",
            messages.SUCCESS,
        )

    @admin.action(description="Permanently delete selected records")
    def permanently_delete_selected(self, request, queryset):
        if request.POST.get("confirm_permanent") != "yes":
            context = {
                **self.admin_site.each_context(request),
                "title": "Permanently delete selected records?",
                "queryset": queryset,
                "opts": self.model._meta,
                "action_checkbox_name": ACTION_CHECKBOX_NAME,
            }
            return TemplateResponse(request, "admin/recycle_permanent_confirmation.html", context)

        deleted_count = 0
        skipped_current_user = False
        for item in queryset:
            recycled_object = item.get_recycled_object()
            if isinstance(recycled_object, get_user_model()) and recycled_object.pk == request.user.pk:
                skipped_current_user = True
                continue
            deleted_count += int(item.permanently_delete_object())

        self.message_user(
            request,
            f"{deleted_count} record(s) permanently deleted.",
            messages.SUCCESS,
        )
        if skipped_current_user:
            self.message_user(request, "Your current account was not deleted.", messages.WARNING)

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False


def admin_reports_view(request):
    from .templatetags.admin_metrics import get_admin_metrics

    context = {
        **admin.site.each_context(request),
        "title": "Reports",
        "metrics": get_admin_metrics(),
    }
    return TemplateResponse(request, "admin/reports.html", context)


def admin_accounting_view(request):
    today = timezone.localdate()
    transactions = Transaction.objects.select_related("customer", "collected_by").filter(is_deleted=False)
    monthly_transactions = transactions.filter(
        transacted_at__year=today.year,
        transacted_at__month=today.month,
    )
    income_this_month = monthly_transactions.aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
    expenses_this_month = Decimal("0.00")

    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    voucher_rows = transactions
    if search_query:
        voucher_rows = voucher_rows.filter(
            models.Q(transaction_id__icontains=search_query)
            | models.Q(customer__customer_id__icontains=search_query)
            | models.Q(customer__first_name__icontains=search_query)
            | models.Q(customer__last_name__icontains=search_query)
            | models.Q(note__icontains=search_query)
        )
    if status_filter:
        voucher_rows = voucher_rows.filter(status=status_filter)

    context = {
        **admin.site.each_context(request),
        "title": "Accounting",
        "income_this_month": income_this_month,
        "expenses_this_month": expenses_this_month,
        "net_surplus": income_this_month - expenses_this_month,
        "unposted_vouchers": transactions.exclude(status=Transaction.Status.COMPLETED).count(),
        "voucher_rows": voucher_rows[:40],
        "search_query": search_query,
        "status_filter": status_filter,
        "status_choices": Transaction.Status.choices,
    }
    return TemplateResponse(request, "admin/accounting.html", context)


def admin_approvals_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        object_id = request.POST.get("object_id")

        if action in {"approve_kyc", "reject_kyc"}:
            customer = get_object_or_404(Customer, pk=object_id)
            if not request.user.has_perm("myapp.change_customer"):
                raise PermissionDenied
            if action == "approve_kyc":
                customer.kyc_status = Customer.KycStatus.APPROVED
                customer.approved_at = timezone.now()
                customer.approved_by = request.user
                message = f"KYC approved for {customer.full_name}."
            else:
                customer.kyc_status = Customer.KycStatus.REJECTED
                customer.approved_at = None
                customer.approved_by = None
                message = f"KYC rejected for {customer.full_name}."
            customer.save(update_fields=("kyc_status", "approved_at", "approved_by"))
            messages.success(request, message)
            return redirect("admin:myapp_approvals")

        if action in {"verify_ticket", "return_ticket"}:
            ticket = get_object_or_404(Ticket, pk=object_id)
            if not request.user.has_perm("myapp.change_ticket"):
                raise PermissionDenied
            if ticket.status != Ticket.Status.STAFF_COMPLETED:
                messages.warning(request, "This ticket is no longer waiting for approval.")
                return redirect("admin:myapp_approvals")
            if action == "verify_ticket":
                ticket.status = Ticket.Status.VERIFIED_COMPLETED
                message = f"Ticket verified: {ticket.title}."
            else:
                ticket.status = Ticket.Status.NOT_COMPLETED
                message = f"Ticket returned as not completed: {ticket.title}."
            ticket.verified_by = request.user
            ticket.verified_at = timezone.now()
            ticket.save(update_fields=("status", "verified_by", "verified_at"))
            messages.success(request, message)
            return redirect("admin:myapp_approvals")

    pending_kyc = Customer.objects.filter(kyc_status=Customer.KycStatus.PENDING).order_by("-submitted_for_approval_at", "-created_at")
    pending_tickets = Ticket.objects.select_related("customer", "created_by", "assigned_to").filter(
        status=Ticket.Status.STAFF_COMPLETED,
    ).order_by("-staff_completed_at", "-created_at")
    context = {
        **admin.site.each_context(request),
        "title": "Approvals",
        "pending_kyc": pending_kyc,
        "pending_tickets": pending_tickets,
        "approval_count": pending_kyc.count() + pending_tickets.count(),
    }
    return TemplateResponse(request, "admin/approvals.html", context)


def admin_recent_actions_view(request):
    recent_actions = LogEntry.objects.select_related("content_type", "user").filter(user=request.user)[:50]
    context = {
        **admin.site.each_context(request),
        "title": "Recent Actions",
        "recent_actions": recent_actions,
    }
    return TemplateResponse(request, "admin/recent_actions.html", context)


def admin_profile_settings_view(request):
    profile, _ = AdminProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = StaffProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile settings updated.")
            return redirect("admin:myapp_staff_profile_settings")
    else:
        form = StaffProfileForm(instance=profile)

    context = {
        **admin.site.each_context(request),
        "title": "Profile Settings",
        "profile": profile,
        "form": form,
    }
    return TemplateResponse(request, "admin/staff_profile_settings.html", context)


if not getattr(admin.site, "_nanu_custom_urls_installed", False):
    original_get_urls = admin.site.get_urls

    def get_urls():
        custom_urls = [
            path("profile-settings/", admin.site.admin_view(admin_profile_settings_view), name="myapp_staff_profile_settings"),
            path("reports/", admin.site.admin_view(admin_reports_view), name="myapp_reports"),
            path("accounting/", admin.site.admin_view(admin_accounting_view), name="myapp_accounting"),
            path("approvals/", admin.site.admin_view(admin_approvals_view), name="myapp_approvals"),
            path("recent-actions/", admin.site.admin_view(admin_recent_actions_view), name="myapp_recent_actions"),
        ]
        return custom_urls + original_get_urls()

    admin.site.get_urls = get_urls
    admin.site._nanu_custom_urls_installed = True
