from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def extract_emails_safe(raw_emails):
    emails = [e.strip() for e in str(raw_emails).split(',') if e.strip()]
    return [e for e in emails if is_valid_email(e)]

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
