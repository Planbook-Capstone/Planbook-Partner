from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os

from app.models.schemas import (
    UploadResponse, AnalysisResult, StudentSummary, ClassStatistics,
    SubjectStatistics, ErrorResponse
)
from app.services.excel_processor import ExcelProcessor
from app.services.grade_analyzer import GradeAnalyzer

router = APIRouter()

# Khởi tạo services
excel_processor = ExcelProcessor()
grade_analyzer = GradeAnalyzer()


@router.post("/upload-excel", response_model=UploadResponse)
async def upload_excel_file(file: UploadFile = File(...)):
    """Upload và xử lý file Excel kết quả học tập"""

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

        # Xử lý file Excel
        file_id, students, stats = excel_processor.process_excel_file(
            file_content, file.filename
        )

        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            total_students=stats['total_students'],
            total_subjects=stats['total_subjects'],
            message=f"Đã xử lý thành công {stats['total_students']} học sinh, {stats['total_subjects']} môn học"
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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


@router.get("/analyze/{file_id}", response_model=AnalysisResult)
async def analyze_grades(file_id: str):
    """Phân tích toàn diện kết quả học tập"""
    
    try:
        # Lấy dữ liệu đã xử lý
        students, stats = excel_processor.get_processed_data(file_id)
        
        # Phân tích hoàn chỉnh
        analysis_result = grade_analyzer.analyze_complete(file_id, students)
        
        return analysis_result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student-summary/{file_id}", response_model=List[StudentSummary])
async def get_student_summaries(file_id: str):
    """Lấy tóm tắt kết quả từng học sinh"""
    
    try:
        students, _ = excel_processor.get_processed_data(file_id)
        
        student_summaries = [
            grade_analyzer.analyze_student(student) 
            for student in students
        ]
        
        return student_summaries
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/class-statistics/{file_id}", response_model=ClassStatistics)
async def get_class_statistics(file_id: str):
    """Lấy thống kê tổng quan lớp học"""
    
    try:
        students, _ = excel_processor.get_processed_data(file_id)
        
        class_stats = grade_analyzer.analyze_class_statistics(students)
        
        return class_stats
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subject-analysis/{file_id}", response_model=List[SubjectStatistics])
async def get_subject_analysis(file_id: str):
    """Phân tích chi tiết theo từng môn học"""
    
    try:
        students, _ = excel_processor.get_processed_data(file_id)
        
        # Lấy danh sách môn học
        all_subjects = set()
        for student in students:
            for grade in student.grades:
                all_subjects.add(grade.subject)
        
        # Phân tích từng môn
        subject_stats = []
        for subject in sorted(all_subjects):
            stats = grade_analyzer.analyze_subject_statistics(students, subject)
            subject_stats.append(stats)
        
        return subject_stats
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weak-students/{file_id}", response_model=List[StudentSummary])
async def get_weak_students(file_id: str, threshold: float = 5.0):
    """Lấy danh sách học sinh yếu (điểm trung bình < threshold)"""
    
    try:
        students, _ = excel_processor.get_processed_data(file_id)
        
        weak_students = []
        for student in students:
            summary = grade_analyzer.analyze_student(student)
            if summary.average_score < threshold:
                weak_students.append(summary)
        
        # Sắp xếp theo điểm tăng dần (yếu nhất trước)
        weak_students.sort(key=lambda x: x.average_score)
        
        return weak_students
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-students/{file_id}", response_model=List[StudentSummary])
async def get_top_students(file_id: str, limit: int = 10):
    """Lấy danh sách top học sinh giỏi nhất"""
    
    try:
        students, _ = excel_processor.get_processed_data(file_id)
        
        student_summaries = [
            grade_analyzer.analyze_student(student) 
            for student in students
        ]
        
        # Sắp xếp theo điểm giảm dần và lấy top
        top_students = sorted(
            student_summaries, 
            key=lambda x: x.average_score, 
            reverse=True
        )[:limit]
        
        return top_students
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/{file_id}", response_model=List[str])
async def get_recommendations(file_id: str):
    """Lấy gợi ý cải thiện kết quả học tập"""
    
    try:
        students, _ = excel_processor.get_processed_data(file_id)
        
        # Phân tích và tạo gợi ý
        student_summaries = [
            grade_analyzer.analyze_student(student) 
            for student in students
        ]
        class_stats = grade_analyzer.analyze_class_statistics(students)
        recommendations = grade_analyzer.generate_recommendations(
            class_stats, student_summaries
        )
        
        return recommendations
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Student Grade Analyzer API is running"}
