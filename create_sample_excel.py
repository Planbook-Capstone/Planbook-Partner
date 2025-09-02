import pandas as pd

# Dữ liệu theo đúng format bạn yêu cầu
data = {
    'Tên học sinh': [
        'Lê Thị Huyền', 'Lê Thị Ngọc Diệp', 'Lê Thị Thanh Bình',
        'Nguyễn Quang Chí', 'Nguyễn Thị Lan', 'Nguyễn Văn Duy',
        'Nguyễn Văn Đức', 'Phạm Như Anh', 'Trần Quốc Bình',
        'Đoàn Văn Hoàng Anh'
    ],
    'Toán': [6.5, 7.4, 8.7, 5.8, 5.7, 5.1, 5.1, 8.9, 5.7, 6],
    'Ngữ Văn': [8.1, 5.4, 7, 6.8, 6, 4.7, 3, 8.4, 7.3, 6.3],
    'Tiếng Anh': [3.9, 6, 7.1, 6.5, 7.4, 2.9, 5.1, 9, 6.2, 5.4],
    'Vật Lý': [7.3, 7.4, 8.1, 6.3, 6.8, 4.8, 4.4, 9.7, 7.5, 5.3],
    'Hóa Học': [6.6, 7.9, 7.7, 5.1, 6, 4.9, 4.1, 8.3, 6.7, 7.3],
    'Sinh Học': [6.2, 7.4, 8.8, 6.1, 7, 7.3, 5.4, 8.3, 6.9, 7.9],
    'Lịch Sử': [6.6, 7.1, 7.8, 6.2, 6.6, 3.6, 5.8, 9.8, 6.7, 6.4],
    'Địa Lý': [4.5, 6.9, 7.4, 5.7, 7.5, 5.1, 5.7, 9.1, 8.9, 7.5],
    'GDCD': [5.3, 5.9, 9.7, 6.3, 5.8, 4.8, 4, 8.1, 7.2, 6.9],
    'Công Nghệ': [6.9, 6.6, 8.3, 6.9, 6.2, 3.6, 4.5, 8.9, 6.2, 5.9],
    'Tin Học': [8, 6.8, 8.6, 8.4, 6.1, 5.9, 5.1, 8.1, 7.9, 6.9],
    'Thể Dục': [5, 8.2, 7.4, 6.7, 5, 6, 5.8, 8.1, 6.1, 8],
    'Điểm TB': [6.4, 6.9, 8, 6.5, 6.3, 4.9, 4.8, 8.7, 7, 6.7]
}

# Tạo DataFrame
df = pd.DataFrame(data)

# Lưu file Excel theo format ngang
df.to_excel("bang_diem_format_ngang.xlsx", index=False, sheet_name="Bảng điểm")

print("✅ Đã tạo file bang_diem_format_ngang.xlsx thành công!")
print(f"📊 File chứa {len(df)} học sinh với 12 môn học")
