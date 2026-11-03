import re
from datetime import date

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError

from .models import QuoteRequest

MAX_LOGIN_FAILURES = 5
LOCKOUT_SECONDS = 15 * 60


class QuoteRequestForm(forms.ModelForm):
    # Honeypot: humans never see this field; many bots fill it in.
    website = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = QuoteRequest
        fields = ["name", "email", "phone", "address", "zip_code", "service", "bedrooms",
                  "bathrooms", "frequency", "preferred_date", "preferred_time", "has_pets",
                  "inside_oven", "inside_fridge", "interior_windows", "laundry", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel"}),
            "address": forms.TextInput(attrs={"autocomplete": "street-address"}),
            "zip_code": forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "postal-code"}),
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        if len(re.sub(r"\D", "", value)) < 10:
            raise ValidationError("Enter a phone number with area code, for example (281) 555-0123.")
        return value

    def clean_zip_code(self):
        value = self.cleaned_data["zip_code"].strip()
        if not re.fullmatch(r"\d{5}(-\d{4})?", value):
            raise ValidationError("Enter a 5-digit ZIP code.")
        return value

    def clean_preferred_date(self):
        value = self.cleaned_data.get("preferred_date")
        if value and value < date.today():
            raise ValidationError("Choose a date that is today or later.")
        return value


class ResponseUpdateForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ["status", "staff_notes"]
        widgets = {"staff_notes": forms.Textarea(attrs={"rows": 6})}


class StaffAuthenticationForm(AuthenticationForm):
    """Login form that admits staff accounts only and slows down password guessing."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "That username and password did not match a staff account.",
        "locked": "Too many failed attempts. Wait 15 minutes and try again.",
    }

    def _key(self, username):
        ip = self.request.META.get("REMOTE_ADDR", "unknown") if self.request else "unknown"
        return f"staff-login-fail:{ip}:{username.lower()}"

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            # Same message as a wrong password, so the page never reveals which accounts exist.
            raise self.get_invalid_login_error()

    def clean(self):
        username = self.cleaned_data.get("username") or ""
        key = self._key(username)
        if cache.get(key, 0) >= MAX_LOGIN_FAILURES:
            raise ValidationError(self.error_messages["locked"], code="locked")
        try:
            cleaned = super().clean()
        except ValidationError:
            cache.set(key, cache.get(key, 0) + 1, LOCKOUT_SECONDS)
            raise
        cache.delete(key)
        return cleaned
