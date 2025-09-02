from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os
import logging
from typing import Dict, Any
import uuid
from datetime import datetime

from app.models.schemas import AnalysisResult, DataResponseDTO, AnalysisResponseData
from app.services.excel_processor import ExcelProcessor
from app.services.grade_analyzer import GradeAnalyzer
from app.middleware.auth_middleware import verify_api_token

router = APIRouter()
logger = logging.getLogger(__name__)

# Khởi tạo services
excel_processor = ExcelProcessor()
grade_analyzer = GradeAnalyzer()





@router.post("/upload-and-analyze", response_model=Dict[str, Any])
async def upload_and_analyze_immediately(
    file: UploadFile = File(...),
    client_id: str = Depends(verify_api_token)
):
    """
    Upload file Excel và phân tích ngay lập tức, không lưu file

    **Yêu cầu xác thực**: Endpoint này yêu cầu Bearer token hợp lệ trong header Authorization.

    Để sử dụng endpoint này:
    1. Đăng ký client tại `/auth/register-client`
    2. Lấy access token tại `/auth/token`
    3. Sử dụng token trong header: `Authorization: Bearer <your_token>`
    """

    # Kiểm tra định dạng file
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
        )

    # Tạo tool_log_id để tracking
    tool_log_id = str(uuid.uuid4())

    try:
        logger.info(f"File upload and analysis request from client: {client_id}, filename: {file.filename}, tool_log_id: {tool_log_id}")

        # Đọc nội dung file
        file_content = await file.read()

        # Xử lý file Excel trực tiếp trong memory (không lưu file)
        students = excel_processor.process_excel_in_memory(file_content, file.filename)

        # Phân tích ngay lập tức
        analysis_result = grade_analyzer.analyze_complete(f"analysis_{client_id}", students)

        logger.info(f"Analysis completed successfully for client: {client_id}, tool_log_id: {tool_log_id}")

        # Chuyển đổi analysis_result thành dict để phù hợp với format response
        analysis_data = analysis_result.dict()

        # Trả về theo format chuẩn mà Java code expect
        return {
            "success": True,
            "data": analysis_data,
            "message": "Phân tích file Excel thành công"
        }

    except Exception as e:
        logger.error(f"Analysis failed for client {client_id}, tool_log_id: {tool_log_id}: {str(e)}")

        # Trả về error response theo format chuẩn mà Java code expect
        return {
            "success": False,
            "data": None,
            "message": f"Lỗi khi phân tích file: {str(e)}"
        }








@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Student Grade Analyzer API is running"}
