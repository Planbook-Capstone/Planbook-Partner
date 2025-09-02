from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uvicorn

from app.api.endpoints import router
from app.api.auth_endpoints import router as auth_router

# Tạo thư mục uploads nếu chưa tồn tại
os.makedirs("uploads", exist_ok=True)

# Khởi tạo FastAPI app
app = FastAPI(
    title="Student Grade Analyzer API",
    description="API để phân tích kết quả học tập từ file Excel",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên chỉ định cụ thể domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api/v1", tags=["Grade Analysis"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "details": f"Request: {request.method} {request.url}"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "details": str(exc)
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Student Grade Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/info")
async def app_info():
    """Thông tin ứng dụng"""
    return {
        "name": "Student Grade Analyzer",
        "version": "1.0.0",
        "description": "API để phân tích kết quả học tập từ file Excel",
        "features": [
            "Upload file Excel (.xlsx, .xls, .csv)",
            "Phân tích điểm trung bình và xếp loại học sinh",
            "Thống kê theo lớp và môn học",
            "Xác định học sinh yếu và giỏi",
            "Đưa ra gợi ý cải thiện"
        ],
        "endpoints": {
            "upload_and_analyze": "/api/v1/upload-and-analyze"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
