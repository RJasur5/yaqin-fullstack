import re

def format_phone(phone: str) -> str:
    """
    Normalizes any Uzbekistan phone number to '+998 (99) 123-45-67' format.
    Input can be '+998991234567', '998991234567', '991234567', etc.
    """
    if not phone:
        return phone
        
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If it starts with 998, keep the last 9 digits
    if len(digits) >= 12 and digits.startswith('998'):
        main_part = digits[3:12]
    elif len(digits) == 9:
        main_part = digits
    else:
        # Fallback if it's some other length (return as is or try to extract last 9)
        if len(digits) > 9:
            main_part = digits[-9:]
        else:
            return phone # Can't format properly

    # Reconstruct in desired format: +998 (99) 858-56-88
    # main_part is '998585688'
    return f"+998 ({main_part[0:2]}) {main_part[2:5]}-{main_part[5:7]}-{main_part[7:9]}"
