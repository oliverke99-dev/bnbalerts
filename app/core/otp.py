import random
import string
from app.core.constants import OTP_LENGTH


def generate_otp(length: int = OTP_LENGTH) -> str:
    """
    Generate a random numeric OTP code.
    
    Args:
        length: Length of the OTP code (default: from constants)
        
    Returns:
        String containing random digits
        
    Example:
        >>> otp = generate_otp()
        >>> len(otp)
        6
        >>> otp.isdigit()
        True
    """
    return ''.join(random.choices(string.digits, k=length))