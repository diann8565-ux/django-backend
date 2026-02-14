
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_password_strength(password):
    """
    Validates that a password meets minimum strength requirements.
    """
    if len(password) < 8:
        raise ValidationError(_("Password must be at least 8 characters long."))
    if not re.search(r'[A-Z]', password):
        raise ValidationError(_("Password must contain at least one uppercase letter."))
    if not re.search(r'[a-z]', password):
        raise ValidationError(_("Password must contain at least one lowercase letter."))
    if not re.search(r'[0-9]', password):
        raise ValidationError(_("Password must contain at least one digit."))

def validate_filename(filename):
    """
    Validates that a filename contains safe characters.
    """
    if not re.match(r'^[\w\-. ]+$', filename):
        raise ValidationError(_("Filename contains invalid characters."))

def sanitize_api_key(raw_key: str) -> str:
    """
    Returns a sanitized API key with allowed characters only.
    Keeps exact value (no enforced prefix), trims and removes invalid chars.
    """
    if not raw_key:
        return ""
    raw_key = raw_key.strip()
    # keep only allowed characters
    cleaned = re.sub(r'[^A-Za-z0-9_\-\.~]', '', raw_key)
    return cleaned
