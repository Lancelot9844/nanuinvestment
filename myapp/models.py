from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        deleted_count = 0
        deleted_by_model = {}
        for obj in self:
            count, details = obj.delete()
            deleted_count += count
            for model_label, model_count in details.items():
                deleted_by_model[model_label] = deleted_by_model.get(model_label, 0) + model_count
        return deleted_count, deleted_by_model

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, deleted_by=None):
        if not self.pk or self.is_deleted:
            return 0, {}

        database = using or self._state.db
        with transaction.atomic(using=database):
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(using=database, update_fields=("is_deleted", "deleted_at"))
            content_type = ContentType.objects.db_manager(database).get_for_model(self)
            RecycleBinItem.objects.using(database).update_or_create(
                content_type=content_type,
                object_id=self.pk,
                defaults={
                    "object_label": str(self)[:250],
                    "deleted_by": deleted_by if getattr(deleted_by, "pk", None) else None,
                },
            )

        return 1, {self._meta.label: 1}

    def restore(self, using=None):
        if not self.pk:
            return False

        database = using or self._state.db
        with transaction.atomic(using=database):
            self.is_deleted = False
            self.deleted_at = None
            self.save(using=database, update_fields=("is_deleted", "deleted_at"))
            content_type = ContentType.objects.db_manager(database).get_for_model(self)
            RecycleBinItem.objects.using(database).filter(
                content_type=content_type,
                object_id=self.pk,
            ).delete()
        return True

    def hard_delete(self, using=None, keep_parents=False):
        database = using or self._state.db
        content_type = ContentType.objects.db_manager(database).get_for_model(self)
        RecycleBinItem.objects.using(database).filter(
            content_type=content_type,
            object_id=self.pk,
        ).delete()
        return super().delete(using=database, keep_parents=keep_parents)


class TimestampedContent(SoftDeleteModel):
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


class Banner(SoftDeleteModel):
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


class WebsitePopup(SoftDeleteModel):
    title = models.CharField(max_length=180)
    message = models.TextField(blank=True, default="")
    image = models.FileField(upload_to="popups/", blank=True)
    button_text = models.CharField(max_length=80, blank=True)
    button_url = models.CharField(max_length=240, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Website Popup"
        verbose_name_plural = "Website Popups"

    def __str__(self):
        return self.title


class AdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_profile",
    )
    phone_number = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    photo = models.FileField(upload_to="admin_profiles/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"

    def __str__(self):
        return f"{self.user.get_username()} profile"


class Customer(SoftDeleteModel):
    class AccountType(models.TextChoices):
        SAVINGS = "savings", "Savings Account"
        CURRENT = "current", "Current Account"
        FIXED = "fixed", "Fixed Deposit"
        RECURRING = "recurring", "Recurring Deposit"

    class KycStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Sent for Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    customer_id = models.CharField(max_length=20, unique=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_profile",
        help_text="Normal user account this customer uses for the customer portal.",
    )
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone_number = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    profile_photo = models.FileField(upload_to="customer_profiles/", blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    citizenship_number = models.CharField(max_length=80, blank=True)
    address = models.TextField()
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.SAVINGS,
    )
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nominee_name = models.CharField(max_length=160, blank=True)
    nominee_phone = models.CharField(max_length=30, blank=True)
    kyc_document_name = models.CharField(max_length=160, blank=True)
    kyc_document = models.FileField(upload_to="customer_kyc/", blank=True)
    kyc_status = models.CharField(
        max_length=20,
        choices=KycStatus.choices,
        default=KycStatus.DRAFT,
    )
    submitted_for_approval_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_customers",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Customer & KYC"
        verbose_name_plural = "Customers & KYC"

    def save(self, *args, **kwargs):
        if not self.customer_id:
            last_customer = Customer.all_objects.order_by("-id").first()
            next_id = (last_customer.id + 1) if last_customer else 1
            self.customer_id = f"CUST-{next_id:06d}"
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.customer_id} - {self.full_name}"


class CustomerKYCDocument(SoftDeleteModel):
    class DocumentType(models.TextChoices):
        CITIZENSHIP_FRONT = "citizenship_front", "Citizenship Front"
        CITIZENSHIP_BACK = "citizenship_back", "Citizenship Back"
        PASSPORT_PHOTO = "passport_photo", "Passport Size Photo"
        SIGNATURE = "signature", "Signature"
        ADDRESS_PROOF = "address_proof", "Address Proof"
        OTHER = "other", "Other"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="kyc_documents")
    document_type = models.CharField(max_length=40, choices=DocumentType.choices)
    document_name = models.CharField(max_length=160, help_text="Label shown for this uploaded document.")
    document = models.FileField(upload_to="customer_kyc/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["document_type", "document_name"]
        verbose_name = "KYC Document"
        verbose_name_plural = "KYC Documents"

    def __str__(self):
        return f"{self.customer.full_name} - {self.document_name}"


class EBankingCredential(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="ebanking_credential")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ebanking_credential",
    )
    username = models.CharField(max_length=150, unique=True)
    temporary_password = models.CharField(
        max_length=128,
        blank=True,
        help_text="Raw temporary passwords are shown once during handover and are not stored.",
    )
    password_changed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["customer__customer_id"]
        verbose_name = "E-Banking"
        verbose_name_plural = "E-Banking"

    def __str__(self):
        return f"{self.customer.customer_id} - {self.username}"


class DailyCollection(Customer):
    class Meta:
        proxy = True
        verbose_name = "Daily Collection"
        verbose_name_plural = "Daily Collections"


class CollectionRecord(SoftDeleteModel):
    class VisitType(models.TextChoices):
        SHOP = "shop", "Shop Visit"
        HOME = "home", "Home Visit"
        OFFICE = "office", "Office Collection"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        ONLINE = "online", "Online"

    class DateTimeApprovalStatus(models.TextChoices):
        NOT_REQUIRED = "not_required", "Not Required"
        PENDING = "pending", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="collections")
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collection_records",
    )
    visit_type = models.CharField(max_length=20, choices=VisitType.choices, default=VisitType.SHOP)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    payment_reference = models.CharField(max_length=120, blank=True)
    payment_receipt = models.FileField(upload_to="payment_receipts/", blank=True)
    collected_at = models.DateTimeField(default=timezone.now)
    collected_at_was_manual = models.BooleanField(default=False)
    datetime_approval_status = models.CharField(
        max_length=20,
        choices=DateTimeApprovalStatus.choices,
        default=DateTimeApprovalStatus.NOT_REQUIRED,
    )
    datetime_approval_requested_at = models.DateTimeField(null=True, blank=True)
    datetime_approved_at = models.DateTimeField(null=True, blank=True)
    datetime_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_collection_datetimes",
    )
    note = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-collected_at"]
        verbose_name = "Collection Record"
        verbose_name_plural = "Collection Records"

    def __str__(self):
        return f"{self.customer.full_name} - {self.amount}"


class Transaction(SoftDeleteModel):
    class TransactionType(models.TextChoices):
        COLLECTION = "collection", "Collection"

    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    transaction_id = models.CharField(max_length=24, unique=True, blank=True)
    collection_record = models.OneToOneField(
        CollectionRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transaction",
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.COLLECTION,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=40, default="Cash")
    payment_reference = models.CharField(max_length=120, blank=True)
    payment_receipt = models.FileField(upload_to="payment_receipts/", blank=True)
    visit_type = models.CharField(max_length=20, choices=CollectionRecord.VisitType.choices)
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions_collected",
    )
    note = models.CharField(max_length=220, blank=True)
    transacted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transacted_at", "-id"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            last_transaction = Transaction.all_objects.order_by("-id").first()
            next_id = (last_transaction.id + 1) if last_transaction else 1
            self.transaction_id = f"TXN-{next_id:08d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.customer.full_name}"


class SMSDelivery(models.Model):
    class EventType(models.TextChoices):
        COLLECTION_RECEIPT = "collection_receipt", "Collection Receipt"
        EBANKING_LOGIN = "ebanking_login", "E-Banking Login"
        TEMPORARY_PASSWORD = "temporary_password", "Temporary Password"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUEUED = "queued", "Queued by AakashSMS"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sms_delivery",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sms_deliveries",
    )
    event_type = models.CharField(
        max_length=40,
        choices=EventType.choices,
        default=EventType.COLLECTION_RECEIPT,
    )
    provider = models.CharField(max_length=40, default="AakashSMS")
    recipient = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    provider_reference = models.CharField(max_length=80, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    attempt_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    queued_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "SMS Message"
        verbose_name_plural = "SMS Messages"

    def __str__(self):
        reference = self.transaction.transaction_id if self.transaction else self.recipient
        return f"{reference} - {self.get_status_display()}"


class LoanApplication(SoftDeleteModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CLOSED = "closed", "Closed"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loan_applications")
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    duration_months = models.PositiveIntegerField(default=12)
    purpose = models.CharField(max_length=220)
    collateral_details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_loans",
    )
    disbursed_at = models.DateTimeField(null=True, blank=True)
    first_due_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at", "-id"]
        verbose_name = "Loan Application"
        verbose_name_plural = "Loan Management"

    def save(self, *args, **kwargs):
        if self.status == self.Status.APPROVED and not self.approved_amount:
            self.approved_amount = self.requested_amount
        super().save(*args, **kwargs)

    @property
    def principal_amount(self):
        return self.approved_amount or self.requested_amount

    @property
    def paid_amount(self):
        return self.repayments.filter(is_deleted=False).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

    @property
    def outstanding_amount(self):
        if self.status not in (self.Status.APPROVED, self.Status.CLOSED):
            return Decimal("0.00")
        return max(self.principal_amount - self.paid_amount, Decimal("0.00"))

    @property
    def is_overdue(self):
        return bool(
            self.status == self.Status.APPROVED
            and self.first_due_date
            and self.first_due_date < timezone.localdate()
            and self.outstanding_amount > 0
        )

    def __str__(self):
        return f"{self.customer.full_name} - Rs {self.requested_amount}"


class LoanRepayment(SoftDeleteModel):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        ONLINE = "online", "Online"

    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name="repayments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    payment_reference = models.CharField(max_length=120, blank=True)
    payment_receipt = models.FileField(upload_to="loan_payment_receipts/", blank=True)
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan_repayments_collected",
    )
    paid_at = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at", "-id"]
        verbose_name = "Loan Repayment"
        verbose_name_plural = "Loan Repayments"

    def __str__(self):
        return f"{self.loan.customer.full_name} - Rs {self.amount}"


class DepositAccount(SoftDeleteModel):
    class DepositType(models.TextChoices):
        FIXED = "fixed", "Fixed Deposit"
        RECURRING = "recurring", "Recurring Deposit"

    class InterestPayout(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"
        MATURITY = "maturity", "On Maturity"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Approval"
        ACTIVE = "active", "Active"
        MATURED = "matured", "Matured"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="deposit_accounts")
    deposit_type = models.CharField(max_length=20, choices=DepositType.choices, default=DepositType.FIXED)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tenure_months = models.PositiveIntegerField(default=12)
    interest_payout = models.CharField(max_length=20, choices=InterestPayout.choices, default=InterestPayout.MATURITY)
    start_date = models.DateField(default=timezone.localdate)
    maturity_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    nominee_name = models.CharField(max_length=160, blank=True)
    nominee_phone = models.CharField(max_length=30, blank=True)
    certificate_file = models.FileField(upload_to="deposit_certificates/", blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_deposits",
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    closure_reason = models.CharField(max_length=220, blank=True)
    remarks = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Fixed / Recurring Deposit"
        verbose_name_plural = "Fixed / Recurring Deposits"

    @property
    def total_paid(self):
        payments_total = self.payments.filter(is_deleted=False).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
        if self.deposit_type == self.DepositType.FIXED:
            return self.principal_amount + payments_total
        return payments_total

    @property
    def maturity_amount(self):
        base_amount = self.principal_amount if self.deposit_type == self.DepositType.FIXED else self.installment_amount * self.tenure_months
        interest = (base_amount * self.interest_rate * self.tenure_months) / Decimal("1200")
        return base_amount + interest

    @property
    def is_maturing_soon(self):
        if not self.maturity_date or self.status != self.Status.ACTIVE:
            return False
        today = timezone.localdate()
        return today <= self.maturity_date <= today + timezone.timedelta(days=7)

    @property
    def is_overdue(self):
        return bool(
            self.deposit_type == self.DepositType.RECURRING
            and self.status == self.Status.ACTIVE
            and self.next_due_date
            and self.next_due_date < timezone.localdate()
        )

    def __str__(self):
        return f"{self.customer.full_name} - {self.get_deposit_type_display()}"


class DepositPayment(SoftDeleteModel):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        ONLINE = "online", "Online"

    deposit = models.ForeignKey(DepositAccount, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    payment_reference = models.CharField(max_length=120, blank=True)
    payment_receipt = models.FileField(upload_to="deposit_payment_receipts/", blank=True)
    collected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deposit_payments_collected",
    )
    paid_at = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at", "-id"]
        verbose_name = "Deposit Payment"
        verbose_name_plural = "Deposit Payments"

    def __str__(self):
        return f"{self.deposit.customer.full_name} - Rs {self.amount}"


class Ticket(SoftDeleteModel):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ASSIGNED = "assigned", "Assigned to Staff"
        STAFF_COMPLETED = "staff_completed", "Staff Marked Complete"
        VERIFIED_COMPLETED = "verified_completed", "Completed"
        NOT_COMPLETED = "not_completed", "Not Completed"

    title = models.CharField(max_length=180)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.OPEN)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
        help_text="Customer this support ticket belongs to, when created from the customer portal.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tickets",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        help_text="Invite/assign a staff member to solve this ticket.",
    )
    staff_completion_note = models.TextField(
        blank=True,
        help_text="Staff adds the work note before marking this ticket complete.",
    )
    staff_completed_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_tickets",
    )
    admin_verification_reason = models.TextField(
        blank=True,
        help_text="Admin adds the reason before verifying completed or returning as not completed.",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ticket Created"
        verbose_name_plural = "Ticket Created"

    def __str__(self):
        return self.title


class RecycleBinItem(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    object_label = models.CharField(max_length=250)
    deleted_at = models.DateTimeField(auto_now_add=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recycled_items",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-deleted_at",)
        constraints = (
            models.UniqueConstraint(
                fields=("content_type", "object_id"),
                name="unique_recycled_object",
            ),
        )
        verbose_name = "Recycle Bin Item"
        verbose_name_plural = "Recycle Bin"

    @classmethod
    def recycle(cls, obj, deleted_by=None):
        if isinstance(obj, SoftDeleteModel):
            return obj.delete(deleted_by=deleted_by)

        if isinstance(obj, get_user_model()):
            with transaction.atomic():
                content_type = ContentType.objects.get_for_model(obj)
                cls.objects.update_or_create(
                    content_type=content_type,
                    object_id=obj.pk,
                    defaults={
                        "object_label": str(obj)[:250],
                        "deleted_by": deleted_by if getattr(deleted_by, "pk", None) else None,
                        "metadata": {"was_active": obj.is_active},
                    },
                )
                obj.is_active = False
                obj.save(update_fields=("is_active",))
            return 1, {obj._meta.label: 1}

        raise TypeError(f"{obj._meta.label} does not support the Recycle Bin.")

    def get_recycled_object(self):
        model = self.content_type.model_class()
        if model is None:
            return None
        manager = getattr(model, "all_objects", model._base_manager)
        return manager.filter(pk=self.object_id).first()

    def restore_object(self):
        obj = self.get_recycled_object()
        if obj is None:
            return False

        if isinstance(obj, SoftDeleteModel):
            return obj.restore()

        if isinstance(obj, get_user_model()):
            obj.is_active = self.metadata.get("was_active", True)
            obj.save(update_fields=("is_active",))
            type(self).objects.filter(pk=self.pk).delete()
            return True

        return False

    def permanently_delete_object(self):
        item_pk = self.pk
        obj = self.get_recycled_object()
        if obj is not None:
            if isinstance(obj, SoftDeleteModel):
                obj.hard_delete()
            else:
                obj.delete()
        type(self).objects.filter(pk=item_pk).delete()
        return obj is not None

    def __str__(self):
        return self.object_label


class SecurityEvent(models.Model):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login Success"
        LOGIN_FAILED = "login_failed", "Login Failed"
        LOGOUT = "logout", "Logout"
        SECURITY_REVIEW = "security_review", "Security Review"

    event_type = models.CharField(max_length=40, choices=EventType.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_events",
    )
    username = models.CharField(max_length=150, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    path = models.CharField(max_length=220, blank=True)
    message = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"

    def __str__(self):
        label = self.username or self.user or "Unknown"
        return f"{self.get_event_type_display()} - {label}"


class SystemSetting(models.Model):
    company_name = models.CharField(max_length=180, default="Nanu Investment Pvt. Ltd.")
    company_address = models.CharField(max_length=220, default="Barahathawa-12, Sarlahi, Nepal")
    company_phone = models.CharField(max_length=40, default="+977 9744360267")
    company_email = models.EmailField(blank=True)
    pan_vat_number = models.CharField(max_length=80, blank=True)
    company_logo = models.FileField(upload_to="system/", blank=True)
    favicon = models.FileField(upload_to="system/", blank=True)

    receipt_prefix = models.CharField(max_length=12, default="TXN")
    date_format = models.CharField(max_length=40, default="d M Y, H:i")
    currency_label = models.CharField(max_length=12, default="Rs")
    customer_signature_label = models.CharField(max_length=80, default="Customer Signature")
    authorized_signature_label = models.CharField(max_length=80, default="Authorized Signature")
    default_payment_method = models.CharField(max_length=40, default="Cash")
    receipt_footer_text = models.CharField(
        max_length=250,
        default="This bill was generated by Nanu Investment transaction system.",
    )

    default_saving_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    default_loan_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12)
    default_fixed_deposit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=8)
    default_recurring_deposit_rate = models.DecimalField(max_digits=5, decimal_places=2, default=7)
    penalty_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grace_period_days = models.PositiveIntegerField(default=0)

    require_manual_collection_datetime_approval = models.BooleanField(default=True)
    require_loan_approval = models.BooleanField(default=True)
    require_deposit_approval = models.BooleanField(default=True)
    approval_threshold_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    failed_login_alert_threshold = models.PositiveIntegerField(default=5)
    session_timeout_minutes = models.PositiveIntegerField(default=120)
    password_policy_note = models.CharField(max_length=220, default="Use a strong password and do not share credentials.")
    allow_staff_profile_uploads = models.BooleanField(default=True)

    sms_sender_name = models.CharField(
        max_length=80,
        blank=True,
        help_text="Name shown at the start of SMS messages. The AakashSMS account controls the network Sender ID.",
    )
    email_sender = models.EmailField(blank=True)
    whatsapp_template = models.TextField(blank=True)
    sms_receipt_template = models.TextField(
        blank=True,
        help_text=(
            "Optional collection SMS template. Available fields: {company_name}, {customer_name}, "
            "{customer_id}, {currency}, {amount}, {receipt}, {balance}, {date}, {payment_method}."
        ),
    )
    email_receipt_template = models.TextField(blank=True)

    maintenance_mode = models.BooleanField(default=False)
    backup_note = models.CharField(max_length=220, blank=True)
    last_backup_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_system_settings",
    )

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "System Settings"
