"""Form helpers for Hotel Booking project."""

from typing import Any, Dict, List
from django import forms


def form_errors(form: forms.BaseForm) -> Dict[str, List[str]]:
    """
    Extract validation errors from a Django form into a clean dictionary.

    Returns:
        Dict[str, List[str]]: Mapping field names (or '__all__') to lists of error messages.
        Example: {"email": ["Enter a valid email address."], "__all__": ["Password mismatch."]}
    """
    return {
        field: [str(error) for error in error_list]
        for field, error_list in form.errors.items()
    }
