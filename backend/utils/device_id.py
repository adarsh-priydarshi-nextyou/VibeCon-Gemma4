"""
Device ID generation and management.
Creates unique, persistent user IDs based on device fingerprint.
"""
import hashlib
import uuid
from typing import Optional
from logger import get_logger

logger = get_logger(__name__)


def generate_device_id(
    ip_address: str,
    user_agent: Optional[str] = None,
    device_info: Optional[dict] = None
) -> str:
    """
    Generate unique device ID based on device fingerprint.
    
    Uses combination of:
    - IP address
    - User agent
    - Device info (platform, model, etc.)
    
    Args:
        ip_address: Client IP address
        user_agent: Browser/app user agent string
        device_info: Additional device information
        
    Returns:
        Unique device ID (persistent across sessions)
        
    Example:
        device_id = generate_device_id("192.168.1.100", "Mozilla/5.0...")
        # Returns: "device_a1b2c3d4e5f6"
    """
    # Create fingerprint from available data
    fingerprint_parts = [ip_address]
    
    if user_agent:
        fingerprint_parts.append(user_agent)
    
    if device_info:
        # Add device-specific info
        if 'platform' in device_info:
            fingerprint_parts.append(device_info['platform'])
        if 'model' in device_info:
            fingerprint_parts.append(device_info['model'])
        if 'os_version' in device_info:
            fingerprint_parts.append(device_info['os_version'])
    
    # Create hash of fingerprint
    fingerprint = "|".join(fingerprint_parts)
    hash_object = hashlib.sha256(fingerprint.encode())
    hash_hex = hash_object.hexdigest()
    
    # Create readable device ID
    device_id = f"device_{hash_hex[:16]}"
    
    logger.debug(
        "Generated device ID",
        device_id=device_id,
        ip_address=ip_address,
        has_user_agent=user_agent is not None,
        has_device_info=device_info is not None
    )
    
    return device_id


def generate_fallback_device_id() -> str:
    """
    Generate fallback device ID when fingerprinting fails.
    Uses UUID4 for random unique ID.
    
    Returns:
        Random unique device ID
    """
    device_id = f"device_{uuid.uuid4().hex[:16]}"
    logger.warning("Generated fallback device ID", device_id=device_id)
    return device_id


def extract_client_ip(request) -> str:
    """
    Extract client IP address from request.
    Handles proxies and load balancers.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take first IP in chain
        return forwarded.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


def get_or_create_device_id(request) -> str:
    """
    Get existing device ID from header or create new one.
    
    Priority:
    1. X-Device-ID header (if provided by client)
    2. Generate from device fingerprint
    3. Fallback to random UUID
    
    Args:
        request: FastAPI request object
        
    Returns:
        Device ID (persistent across sessions)
    """
    # Check if client already has device ID
    existing_device_id = request.headers.get("X-Device-ID")
    if existing_device_id and existing_device_id.startswith("device_"):
        logger.debug("Using existing device ID", device_id=existing_device_id)
        return existing_device_id
    
    # Extract device information
    ip_address = extract_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    
    # Extract device info from custom header (mobile apps)
    device_info = None
    device_info_header = request.headers.get("X-Device-Info")
    if device_info_header:
        try:
            import json
            device_info = json.loads(device_info_header)
        except:
            pass
    
    # Generate device ID
    if ip_address != "unknown":
        device_id = generate_device_id(ip_address, user_agent, device_info)
    else:
        device_id = generate_fallback_device_id()
    
    logger.info(
        "Created new device ID",
        device_id=device_id,
        ip_address=ip_address,
        has_user_agent=user_agent is not None
    )
    
    return device_id
