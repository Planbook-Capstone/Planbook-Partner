# 🎓 Grade Analysis API

API phân tích kết quả học tập học sinh với FastAPI và pandas.

## ✨ Tính năng chính

- 📊 **Upload & Phân tích**: Upload file Excel và phân tích ngay lập tức
- 🏆 **Xếp hạng**: Thứ hạng tự động từ #1 đến #N
- 📈 **Pass Rate**: Tỉ lệ đạt (%) cho từng môn học
- 👥 **ID tự động**: Mã học sinh HS001, HS002, HS003...
- 🎯 **Thống kê chi tiết**: Điểm cao/thấp nhất, ai đạt điểm đó
- 💡 **Gợi ý thông minh**: Đề xuất cá nhân hóa và nhóm học tập
- 🌐 **API RESTful**: Swagger UI đầy đủ

## Cài đặt

1. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

2. Chạy server:

```bash
python -m app.main
```

Hoặc:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Truy cập API docs: http://localhost:8000/docs

## Cấu trúc file Excel

File Excel cần có các cột:

- **Tên học sinh** (bắt buộc)
- **Lớp** (bắt buộc)
- **Môn học** (bắt buộc)
- **Điểm** (bắt buộc, từ 0-10)
- Mã học sinh (tùy chọn)
- Học kỳ (tùy chọn)

## API Endpoints

### 1. Upload file Excel

```
POST /api/v1/upload-excel
```

### 2. Phân tích toàn diện

```
GET /api/v1/analyze/{file_id}
```

### 3. Tóm tắt từng học sinh

```
GET /api/v1/student-summary/{file_id}
```

### 4. Thống kê lớp học

```
GET /api/v1/class-statistics/{file_id}
```

### 5. Phân tích theo môn học

```
GET /api/v1/subject-analysis/{file_id}
```

### 6. Danh sách học sinh yếu

```
GET /api/v1/weak-students/{file_id}?threshold=5.0
```

### 7. Top học sinh giỏi

```
GET /api/v1/top-students/{file_id}?limit=10
```

### 8. Gợi ý cải thiện

```
GET /api/v1/recommendations/{file_id}
```

## Xếp loại học lực

- **Giỏi**: ≥ 8.0 điểm
- **Khá**: 6.5 - 7.9 điểm
- **Trung bình**: 5.0 - 6.4 điểm
- **Yếu**: < 5.0 điểm

## Cấu trúc dự án

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app chính
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── excel_processor.py  # Xử lý Excel
│   │   └── grade_analyzer.py   # Phân tích điểm
│   └── api/
│       ├── __init__.py
│       └── endpoints.py     # API endpoints
├── uploads/                 # Thư mục lưu file upload
├── requirements.txt
└── README.md
```
