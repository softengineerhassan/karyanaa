"""
Perk Redemption QR Code Token Generation and Verification Utility

This module provides secure JWT-based QR token generation and verification
for perk redemption functionality.
"""

from datetime import datetime, timedelta, timezone
from typing import Tuple
import jwt

from app.core.config import settings
from app.utils.exceptions import InvalidQRTokenError, ExpiredQRTokenError


def generate_perk_redemption_qr_token(redemption_code: str, expiry: datetime) -> str:
    """
    Generate a secure JWT-based QR token for a perk redemption.
    
    Args:
        redemption_code: 8-character alphanumeric redemption code
        expiry: Expiry datetime for the QR code
        
    Returns:
        JWT token string
        
    Token Payload:
        - sub: redemption_code (8-char string)
        - typ: "perk_redemption_qr" (token type identifier)
        - exp: expiry timestamp
    """
    # Create JWT payload
    payload = {
        "sub": redemption_code,  # redemption code
        "typ": "perk_redemption_qr",  # token type
        "exp": int(expiry.timestamp()),  # expiry as unix timestamp
        "iat": int(datetime.now(timezone.utc).timestamp())  # issued at
    }
    
    # Generate JWT token
    token = jwt.encode(
        payload,
        settings.QR_SECRET_KEY,
        algorithm="HS256"
    )
    
    return token


def verify_perk_redemption_qr_token(token: str) -> dict:
    """
    Verify and decode a perk redemption QR token.
    
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
        if payload.get("typ") != "perk_redemption_qr":
            raise InvalidQRTokenError("Invalid token type")
        
        # Validate required fields
        if not payload.get("sub"):
            raise InvalidQRTokenError("Missing redemption code in token")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise ExpiredQRTokenError("QR code has expired")
    except jwt.InvalidTokenError as e:
        raise InvalidQRTokenError(f"Invalid QR token: {str(e)}")
    except Exception as e:
        raise InvalidQRTokenError(f"QR token verification failed: {str(e)}")
