from fastapi import APIRouter, UploadFile, File, HTTPException
import os

from app.models.schemas import AnalysisResult
from app.services.excel_processor import ExcelProcessor
from app.services.grade_analyzer import GradeAnalyzer

router = APIRouter()

# Khởi tạo services
excel_processor = ExcelProcessor()
grade_analyzer = GradeAnalyzer()





@router.post("/upload-and-analyze", response_model=AnalysisResult)
async def upload_and_analyze_immediately(file: UploadFile = File(...)):
    """Upload file Excel và phân tích ngay lập tức, không lưu file"""

    # Kiểm tra định dạng file
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
        )

    try:
        # Đọc nội dung file
        file_content = await file.read()

        # Xử lý file Excel trực tiếp trong memory (không lưu file)
        students = excel_processor.process_excel_in_memory(file_content, file.filename)

        # Phân tích ngay lập tức
        analysis_result = grade_analyzer.analyze_complete("temp_analysis", students)

        return analysis_result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))








@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Student Grade Analyzer API is running"}
