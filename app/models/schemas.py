from typing import Dict, List, Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

T = TypeVar('T')


class GradeLevel(str, Enum):
    EXCELLENT = "Giỏi"
    GOOD = "Khá"
    AVERAGE = "Trung bình"
    WEAK = "Yếu"


class Grade(BaseModel):
    subject: str = Field(..., description="Tên môn học")
    score: float = Field(..., ge=0, le=10, description="Điểm số (0-10)")


class Student(BaseModel):
    id: str = Field(..., description="Mã học sinh (auto-generated)")
    name: str = Field(..., description="Tên học sinh")
    class_name: str = Field(..., description="Lớp")
    grades: List[Grade] = Field(default_factory=list, description="Danh sách điểm")


class StudentSummary(BaseModel):
    student: Student
    average_score: float = Field(..., description="Điểm trung bình")
    rank: int = Field(..., description="Thứ hạng trong lớp")
    grade_level: GradeLevel = Field(..., description="Xếp loại học lực")
    weak_subjects: List[str] = Field(default_factory=list, description="Môn học yếu")
    strong_subjects: List[str] = Field(default_factory=list, description="Môn học mạnh")


class TopStudent(BaseModel):
    name: str = Field(..., description="Tên học sinh")
    score: float = Field(..., description="Điểm số")

class SubjectStatistics(BaseModel):
    subject: str = Field(..., description="Tên môn học")
    average_score: float = Field(..., description="Điểm trung bình môn")
    highest_score: float = Field(..., description="Điểm cao nhất")
    lowest_score: float = Field(..., description="Điểm thấp nhất")
    highest_score_student: str = Field(..., description="Học sinh đạt điểm cao nhất")
    lowest_score_student: str = Field(..., description="Học sinh đạt điểm thấp nhất")
    total_students: int = Field(..., description="Tổng số học sinh")
    pass_rate: float = Field(..., description="Tỉ lệ đạt (%) học sinh trên trung bình (>=5.0)")
    excellent_count: int = Field(0, description="Số học sinh giỏi")
    good_count: int = Field(0, description="Số học sinh khá")
    average_count: int = Field(0, description="Số học sinh trung bình")
    weak_count: int = Field(0, description="Số học sinh yếu")


class ClassStatistics(BaseModel):
    class_name: str = Field(..., description="Tên lớp")
    total_students: int = Field(..., description="Tổng số học sinh")
    overall_average: float = Field(..., description="Điểm trung bình chung")
    highest_score: float = Field(..., description="Điểm cao nhất lớp")
    lowest_score: float = Field(..., description="Điểm thấp nhất lớp")
    grade_distribution: Dict[str, int] = Field(..., description="Phân bố xếp loại")
    top_students: List[TopStudent] = Field(..., description="Top học sinh giỏi nhất")
    weak_students: List[TopStudent] = Field(..., description="Học sinh cần hỗ trợ")
    subject_statistics: List[SubjectStatistics] = Field(..., description="Thống kê theo môn")


class AnalysisResult(BaseModel):
    file_id: str = Field(..., description="ID file đã xử lý")
    class_statistics: ClassStatistics
    student_summaries: List[StudentSummary]
    recommendations: List[str] = Field(default_factory=list, description="Gợi ý cải thiện")


class DataResponseDTO(BaseModel, Generic[T]):
    """
    Standard response format cho tất cả API endpoints
    Tương tự như DataResponseDTO trong Java Spring Boot
    """
    success: bool = Field(..., description="Trạng thái thành công/thất bại")
    data: Optional[T] = Field(None, description="Dữ liệu response")
    message: str = Field(..., description="Thông báo kết quả")
    tool_log_id: Optional[str] = Field(None, description="ID để tracking log")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Thời gian response")
    client_id: Optional[str] = Field(None, description="ID client thực hiện request")
    error: Optional[str] = Field(None, description="Chi tiết lỗi nếu có")


class AnalysisResponseData(BaseModel):
    """Data structure cho analysis response"""
    file_id: str
    class_statistics: ClassStatistics
    student_summaries: List[StudentSummary]
    recommendations: List[str]



