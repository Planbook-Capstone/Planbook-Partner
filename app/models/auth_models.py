"""
Models cho hệ thống xác thực API
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class TokenRequest(BaseModel):
    """Request để tạo token"""
    client_id: str = Field(..., description="Client ID")
    client_secret: str = Field(..., description="Client Secret")


class TokenResponse(BaseModel):
    """Response khi tạo token thành công"""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Loại token")
    expires_in: int = Field(..., description="Thời gian hết hạn (giây)")
    created_at: datetime = Field(..., description="Thời gian tạo token")


class TokenVerificationRequest(BaseModel):
    """Request để xác thực token"""
    token: str = Field(..., description="Token cần xác thực")


class TokenVerificationResponse(BaseModel):
    """Response khi xác thực token"""
    valid: bool = Field(..., description="Token có hợp lệ không")
    client_id: Optional[str] = Field(None, description="Client ID nếu token hợp lệ")
    expires_at: Optional[datetime] = Field(None, description="Thời gian hết hạn")
    message: str = Field(..., description="Thông báo chi tiết")


class ClientRegistrationRequest(BaseModel):
    """Request để đăng ký client mới"""
    client_name: str = Field(..., min_length=3, max_length=100, description="Tên client")
    description: Optional[str] = Field(None, max_length=500, description="Mô tả client")
    contact_email: Optional[EmailStr] = Field(None, description="Email liên hệ")


class ClientRegistrationResponse(BaseModel):
    """Response khi đăng ký client thành công"""
    client_id: str = Field(..., description="Client ID")
    client_secret: str = Field(..., description="Client Secret (chỉ hiển thị 1 lần)")
    client_name: str = Field(..., description="Tên client")
    created_at: datetime = Field(..., description="Thời gian tạo")
    message: str = Field(..., description="Thông báo quan trọng")


class ClientInfo(BaseModel):
    """Thông tin client"""
    client_id: str = Field(..., description="Client ID")
    client_name: str = Field(..., description="Tên client")
    description: Optional[str] = Field(None, description="Mô tả")
    contact_email: Optional[str] = Field(None, description="Email liên hệ")
    created_at: datetime = Field(..., description="Thời gian tạo")
    is_active: bool = Field(..., description="Trạng thái hoạt động")
    last_used: Optional[datetime] = Field(None, description="Lần sử dụng cuối")


class ClientCredentials(BaseModel):
    """Client credentials để lưu trong database"""
    client_id: str
    client_secret_hash: str
    client_name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    created_at: datetime
    is_active: bool = True
    last_used: Optional[datetime] = None


class AuthError(BaseModel):
    """Error response cho authentication"""
    error: str = Field(..., description="Mã lỗi")
    error_description: str = Field(..., description="Mô tả lỗi")
    message: str = Field(..., description="Thông báo lỗi")
