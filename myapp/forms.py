from django import forms

from .models import AdminProfile, CollectionRecord, Customer, Ticket


class DailyCollectionEntryForm(forms.ModelForm):
    class Meta:
        model = CollectionRecord
        fields = ("amount", "visit_type", "note")
        labels = {
            "amount": "New amount collected",
            "visit_type": "Collection location",
            "note": "Remarks (optional)",
        }
        widgets = {
            "amount": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Collected amount must be greater than zero.")
        return amount


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
