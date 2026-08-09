from django import forms
from django.utils import timezone

from .models import AdminProfile, CollectionRecord, Customer, Ticket


class DailyCollectionEntryForm(forms.ModelForm):
    use_manual_collected_at = forms.BooleanField(
        required=False,
        label="Set different collection date/time",
        help_text="Leave unchecked to use the current date and time automatically.",
    )
    manual_collected_at = forms.DateTimeField(
        required=False,
        label="Manual collection date/time",
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = CollectionRecord
        fields = (
            "amount",
            "visit_type",
            "payment_method",
            "payment_reference",
            "payment_receipt",
            "use_manual_collected_at",
            "manual_collected_at",
            "note",
        )
        labels = {
            "amount": "New amount collected",
            "visit_type": "Collection location",
            "payment_method": "Payment method",
            "payment_reference": "Online reference / transaction ID",
            "payment_receipt": "Payment receipt upload",
            "note": "Remarks (optional)",
        }
        widgets = {
            "amount": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_method"].required = False
        self.fields["payment_method"].initial = CollectionRecord.PaymentMethod.CASH

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Collected amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method") or CollectionRecord.PaymentMethod.CASH
        cleaned_data["payment_method"] = payment_method
        payment_reference = cleaned_data.get("payment_reference", "").strip()
        use_manual_collected_at = cleaned_data.get("use_manual_collected_at")
        manual_collected_at = cleaned_data.get("manual_collected_at")
        if payment_method == CollectionRecord.PaymentMethod.ONLINE and not payment_reference:
            self.add_error("payment_reference", "Enter the online reference number or transaction ID.")
        if use_manual_collected_at and not manual_collected_at:
            self.add_error("manual_collected_at", "Enter the manual collection date and time.")
        return cleaned_data

    def get_collection_datetime(self):
        if self.cleaned_data.get("use_manual_collected_at"):
            collected_at = self.cleaned_data["manual_collected_at"]
            if timezone.is_naive(collected_at):
                collected_at = timezone.make_aware(collected_at, timezone.get_current_timezone())
            return collected_at, True
        return timezone.now(), False


class CustomerTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ("title", "description", "priority")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class CustomerProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("profile_photo",)
        labels = {
            "profile_photo": "Profile photo",
        }

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if not photo:
            return photo

        allowed_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp")
        if not photo.name.lower().endswith(allowed_extensions):
            raise forms.ValidationError("Upload a JPG, PNG, GIF, or WebP image.")
        return photo


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ("phone_number", "address", "photo")
        labels = {
            "phone_number": "Phone number",
            "address": "Address",
            "photo": "Profile photo",
        }
        widgets = {
            "address": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if not photo:
            return photo

        allowed_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp")
        if not photo.name.lower().endswith(allowed_extensions):
            raise forms.ValidationError("Upload a JPG, PNG, GIF, or WebP image.")
        return photo
