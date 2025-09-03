# 🎓 Grade Analysis API

API phân tích kết quả học tập học sinh với FastAPI và pandas, được bảo vệ bằng hệ thống xác thực JWT.

## ✨ Tính năng chính

- 📊 **Upload & Phân tích**: Upload file Excel và phân tích ngay lập tức
- 🏆 **Xếp hạng**: Thứ hạng tự động từ #1 đến #N
- 📈 **Pass Rate**: Tỉ lệ đạt (%) cho từng môn học
- 👥 **ID tự động**: Mã học sinh HS001, HS002, HS003...
- 🎯 **Thống kê chi tiết**: Điểm cao/thấp nhất, ai đạt điểm đó
- 💡 **Gợi ý thông minh**: Đề xuất cá nhân hóa và nhóm học tập
- 🌐 **API RESTful**: Swagger UI đầy đủ
- 🔐 **Authentication**: Hệ thống xác thực JWT với ClientID/ClientSecret

## Cài đặt

1. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

2. Cấu hình MongoDB (tùy chọn):

```bash
# Sử dụng Docker (khuyến nghị)
docker-compose up -d mongodb

# Hoặc cài đặt MongoDB local
# Xem hướng dẫn tại: https://docs.mongodb.com/manual/installation/
```

3. Cấu hình environment variables:

```bash
# Copy file cấu hình mẫu
cp .env.example .env

# Chỉnh sửa .env theo môi trường của bạn
```

4. Chạy server:

```bash
python -m app.main
```

Hoặc:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Truy cập API docs: http://localhost:8000/docs

## Cấu trúc file Excel

File Excel cần có các cột:

- **Tên học sinh** (bắt buộc)
- **Lớp** (bắt buộc)
- **Môn học** (bắt buộc)
- **Điểm** (bắt buộc, từ 0-10)
- Mã học sinh (tùy chọn)
- Học kỳ (tùy chọn)

## API Endpoints

### 🔐 Authentication Endpoints (`/auth`)

#### 1. Đăng ký Client

```http
POST /auth/register-client
```

Đăng ký client mới và nhận ClientID/ClientSecret

#### 2. Tạo Access Token

```http
POST /auth/token
```

Tạo JWT token từ ClientID/ClientSecret

#### 3. Xác thực Token

```http
POST /auth/verify-token
```

Kiểm tra tính hợp lệ của token

#### 4. Thông tin Client

```http
GET /auth/client-info
Authorization: Bearer <token>
```

Lấy thông tin client từ token

#### 5. Thu hồi Token

```http
POST /auth/revoke-token
Authorization: Bearer <token>
```

Vô hiệu hóa token hiện tại

### 📊 Grade Analysis Endpoints (`/api/v1`)

#### 1. Upload và Phân tích (🔒 Protected)

```http
POST /api/v1/upload-and-analyze
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

Upload file Excel và phân tích ngay lập tức

#### 2. Phân tích từ Supabase Link (🔒 Protected)

```http
POST /api/v1/analyze-from-link
Authorization: Bearer <token>
Content-Type: application/json
```

Download file Excel từ Supabase link và phân tích ngay lập tức

**Request Body:**

```json
{
  "link": "https://your-supabase-project.supabase.co/storage/v1/object/public/bucket/file.xlsx"
}
```

## 🚀 Cách sử dụng nhanh

### Bước 1: Đăng ký Client

```bash
curl -X POST "http://localhost:8000/auth/register-client" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "My Grade Analyzer",
    "description": "Application for analyzing student grades",
    "contact_email": "admin@school.edu"
  }'
```

### Bước 2: Lấy Access Token

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_abc123...",
    "client_secret": "secret_xyz789..."
  }'
```

### Bước 3: Upload và Phân tích

#### Option 1: Upload file trực tiếp

```bash
curl -X POST "http://localhost:8000/api/v1/upload-and-analyze" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -F "file=@bang_diem_format_ngang.xlsx"
```

#### Option 2: Phân tích từ Supabase link

```bash
curl -X POST "http://localhost:8000/api/v1/analyze-from-link" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "link": "https://your-supabase-project.supabase.co/storage/v1/object/public/bucket/file.xlsx"
  }'
```

## 🧪 Testing

### Test với Authentication:

```bash
python test_auth_api.py
```

### Test API cũ (không cần authentication):

```bash
python test_api.py
```

Chọn option 3 để test endpoint analyze-from-link

### Test riêng endpoint Supabase link:

```bash
python test_supabase_link_api.py
```

**Lưu ý**: Cần thay thế `SAMPLE_SUPABASE_LINK` trong file test bằng link Supabase thực tế

## 🔐 Authentication Details

Xem chi tiết về hệ thống xác thực tại: [AUTH_README.md](AUTH_README.md)

### Security Features:

- ✅ JWT Tokens với expiration
- ✅ Client Secret hashing
- ✅ Token revocation
- ✅ Automatic cleanup expired tokens
- ✅ Database indexing for performance

## 📁 Cấu trúc dự án

```
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app chính
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Cấu hình ứng dụng
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py             # Pydantic models cho grade analysis
│   │   └── auth_models.py         # Pydantic models cho authentication
│   ├── services/
│   │   ├── __init__.py
│   │   ├── excel_processor.py     # Xử lý Excel
│   │   ├── grade_analyzer.py      # Phân tích điểm
│   │   └── auth_service.py        # Service xác thực
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth_middleware.py     # Middleware xác thực
│   └── api/
│       ├── __init__.py
│       ├── endpoints.py           # API endpoints chính
│       └── auth_endpoints.py      # Authentication endpoints
├── uploads/                       # Thư mục lưu file upload (tạm thời)
├── requirements.txt               # Dependencies
├── docker-compose.yml             # MongoDB setup
├── .env.example                   # Environment variables mẫu
├── test_api.py                    # Test script cũ
├── test_auth_api.py              # Test script authentication
├── README.md                      # Documentation chính
├── AUTH_README.md                 # Documentation authentication
└── bang_diem_format_ngang.xlsx    # File test mẫu
```

## 🔧 Environment Variables

Tạo file `.env` từ `.env.example` và cấu hình:

```bash
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=grade_analyzer_auth

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# App
ENVIRONMENT=development
DEBUG=true
```

## Xếp loại học lực

### Học sinh giỏi

- Điểm trung bình chung (TBC) ≥ 8.0
- Không môn nào dưới 6.5
- Ít nhất một trong hai môn Toán hoặc Ngữ văn ≥ 8.0

### Học sinh khá

- Điểm trung bình chung ≥ 6.5
- Không môn nào dưới 5.0

### Học sinh trung bình

- Điểm trung bình chung ≥ 5.0
- Không môn nào dưới 3.5

### Học sinh yếu

- Các trường hợp còn lại

## Cấu trúc dự án

```

├── app/
│ ├── **init**.py
│ ├── main.py # FastAPI app chính
│ ├── models/
│ │ ├── **init**.py
│ │ └── schemas.py # Pydantic models
│ ├── services/
│ │ ├── **init**.py
│ │ ├── excel_processor.py # Xử lý Excel
│ │ └── grade_analyzer.py # Phân tích điểm
│ └── api/
│ ├── **init**.py
│ └── endpoints.py # API endpoints
├── uploads/ # Thư mục lưu file upload
├── requirements.txt
└── README.md

```

```

```
