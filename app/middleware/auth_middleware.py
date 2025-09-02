"""
Middleware xác thực cho API endpoints
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def verify_api_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency để xác thực token cho các protected endpoints
    
    Returns:
        client_id: ID của client nếu token hợp lệ
        
    Raises:
        HTTPException: Nếu token không hợp lệ
    """
    try:
        # Xác thực token
        verification = await auth_service.verify_token(credentials.credentials)
        
        if not verification.valid:
            logger.warning(f"Token verification failed: {verification.message}")
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "invalid_token",
                    "error_description": verification.message,
                    "message": "Token không hợp lệ hoặc đã hết hạn"
                }
            )
        
        logger.info(f"Token verified successfully for client: {verification.client_id}")
        return verification.client_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "verification_error",
                "error_description": "Internal server error during token verification",
                "message": "Lỗi hệ thống khi xác thực token"
            }
        )


async def get_optional_client_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """
    Dependency để lấy client_id từ token (không bắt buộc)
    
    Returns:
        client_id: ID của client nếu có token hợp lệ, None nếu không có token
    """
    if not credentials:
        return None
        
    try:
        verification = await auth_service.verify_token(credentials.credentials)
        return verification.client_id if verification.valid else None
    except Exception:
        return None
