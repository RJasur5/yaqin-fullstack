import re

def mask_phone(phone: str) -> str:
    """Masks a phone number, e.g., +998901234567 -> +998******67"""
    if not phone:
        return ""
    if len(phone) < 6:
        return "******"
    if len(phone) < 10:
        return f"{phone[:2]}******{phone[-1:]}"
    # Masking for +998991234567 -> +998******67 (keep 4 at start, 2 at end)
    # If it's a 12 digit number like 998901234567, 4 at start = 9989, 2 at end = 67.
    # The user example: 558******88 -> 3 at start, 2 at end.
    return f"{phone[:3]}******{phone[-2:]}"

def filter_description(text: str) -> str:
    """Replaces phone numbers in text with [номер скрыт]."""
    if not text:
        return text
    
    # Pattern to match various formats of phone numbers
    # Matches: +998901234567, 998901234567, 901234567, (90)1234567, 90-123-45-67 etc.
    phone_pattern = r'(\+?\d{1,3}[\s-]?\(?\d{2,3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2})|(\d{9,12})'
    
    return re.sub(phone_pattern, '[номер скрыт]', text)
