"""Forms for hotels search and filtering."""

from django import forms
from django.utils import timezone


class SearchForm(forms.Form):
    """Validate query parameters for public hotel search."""

    city = forms.CharField(required=False, max_length=100)
    check_in = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    check_out = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    guests = forms.IntegerField(required=False, min_value=1, initial=1)
    min_price = forms.IntegerField(required=False, min_value=0)
    max_price = forms.IntegerField(required=False, min_value=0)
    q = forms.CharField(required=False, max_length=255)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")

        # Either both check_in and check_out are provided or neither
        if bool(check_in) ^ bool(check_out):
            self.add_error(
                "check_out" if check_in else "check_in",
                "Both check_in and check_out are required when filtering by dates.",
            )

        if check_in and check_out:
            today = timezone.localdate()
            if check_in < today:
                self.add_error("check_in", "Check-in date cannot be in the past.")
            if check_out <= check_in:
                self.add_error("check_out", "Check-out date must be after check-in date.")

        if min_price is not None and max_price is not None:
            if min_price > max_price:
                self.add_error("min_price", "min_price cannot exceed max_price.")

        return cleaned_data


class RoomSearchForm(forms.Form):
    """Validate query parameters for hotel room types availability check."""

    check_in = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    check_out = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    guests = forms.IntegerField(required=False, min_value=1, initial=1)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")

        if bool(check_in) ^ bool(check_out):
            self.add_error(
                "check_out" if check_in else "check_in",
                "Both check_in and check_out are required when checking availability.",
            )

        if check_in and check_out:
            today = timezone.localdate()
            if check_in < today:
                self.add_error("check_in", "Check-in date cannot be in the past.")
            if check_out <= check_in:
                self.add_error("check_out", "Check-out date must be after check-in date.")

        return cleaned_data
