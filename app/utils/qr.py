"""
QR Code Token Generation and Verification Utility

This module provides secure JWT-based QR token generation and verification
for booking check-in functionality with 8-character alphanumeric codes.
"""

from datetime import datetime, timedelta, timezone
from typing import Tuple
import jwt
import random
import string

from app.core.config import settings
from app.utils.exceptions import InvalidQRTokenError, ExpiredQRTokenError


def generate_booking_code() -> str:
    """
    Generate a unique 8-character alphanumeric booking code.
    
    Returns:
        8-character uppercase alphanumeric string (e.g., "A1B2C3D4")
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def generate_booking_qr_token(booking) -> Tuple[str, str, datetime]:
    """
    Generate a secure JWT-based QR token and 8-character code for a booking.
    
    Args:
        booking: Booking model instance
        
    Returns:
        Tuple of (booking_code, qr_token, expiry_datetime)
        
    Token Payload:
        - sub: booking_id (UUID as string)
        - ven: venue_id (UUID as string)
        - code: 8-character booking code
        - typ: "booking_qr" (token type identifier)
        - exp: expiry timestamp (booking start_time + 6 hours)
    """
    # Generate 8-character booking code
    booking_code = generate_booking_code()
    
    # Calculate expiry: booking start_time + 6 hours
    # Combine booking_date and start_time to get full datetime
    booking_datetime = datetime.combine(
        booking.booking_date,
        booking.start_time
    )
    
    # Make timezone-aware (UTC)
    if booking_datetime.tzinfo is None:
        booking_datetime = booking_datetime.replace(tzinfo=timezone.utc)
    
    expiry = booking_datetime + timedelta(hours=6)
    
    # Create JWT payload
    payload = {
        "sub": str(booking.id),  # booking_id
        "ven": str(booking.venue_id),  # venue_id
        "code": booking_code,  # 8-character booking code
        "typ": "booking_qr",  # token type
        "exp": int(expiry.timestamp()),  # expiry as unix timestamp
        "iat": int(datetime.now(timezone.utc).timestamp())  # issued at
    }
    
    # Generate JWT token
    token = jwt.encode(
        payload,
        settings.QR_SECRET_KEY,
        algorithm="HS256"
    )
    
    return booking_code, token, expiry


def verify_booking_qr_token(token: str) -> dict:
    """
    Verify and decode a QR token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        InvalidQRTokenError: If token is malformed or signature is invalid
        ExpiredQRTokenError: If token has expired
    """
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            settings.QR_SECRET_KEY,
            algorithms=["HS256"]
        )
        
        # Validate token type
        if payload.get("typ") != "booking_qr":
            raise InvalidQRTokenError("Invalid token type")
        
        # Validate required fields
        if not payload.get("sub") or not payload.get("ven") or not payload.get("code"):
            raise InvalidQRTokenError("Missing required token fields")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise ExpiredQRTokenError("QR code has expired")
    except jwt.InvalidTokenError as e:
        raise InvalidQRTokenError(f"Invalid QR token: {str(e)}")
    except Exception as e:
        raise InvalidQRTokenError(f"QR token verification failed: {str(e)}")


def generate_qr_code_image(data: str) -> bytes:
    """
    Generate a QR code image from string data.
    
    Args:
        data: The string to encode in the QR code.
        
    Returns:
        PNG image data as bytes.
    """
    import qrcode
    import io
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()
