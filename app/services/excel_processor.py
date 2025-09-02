import pandas as pd
import os
from typing import List, Dict, Tuple
from app.models.schemas import Student, Grade
import uuid


class ExcelProcessor:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.processed_files: Dict[str, Dict] = {}
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Lưu file upload và trả về file_id"""
        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_dir, f"{file_id}_{filename}")
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_id
    
    def read_excel_file(self, file_id: str, filename: str) -> pd.DataFrame:
        """Đọc file Excel và trả về DataFrame"""
        file_path = os.path.join(self.upload_dir, f"{file_id}_{filename}")
        
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                df = pd.read_excel(file_path)
            
            return df
        except Exception as e:
            raise ValueError(f"Không thể đọc file: {str(e)}")
    
    def detect_format_and_convert(self, df: pd.DataFrame) -> pd.DataFrame:
        """Phát hiện định dạng Excel (ngang/dọc) và chuyển đổi về định dạng chuẩn"""

        # Kiểm tra định dạng dọc trước (có 4 cột: Tên, Lớp, Môn học, Điểm)
        if len(df.columns) == 4 and any('môn học' in str(col).lower() for col in df.columns):
            return df

        # Nếu có nhiều cột (>5) thì là định dạng ngang
        if len(df.columns) > 5:
            return self.convert_horizontal_to_vertical(df)

        return df

    def convert_horizontal_to_vertical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Chuyển đổi từ định dạng ngang sang dọc"""

        # Xóa các hàng và cột trống
        df = df.dropna(how='all').dropna(axis=1, how='all')

        # Tìm cột tên học sinh (thường là cột đầu tiên có chữ "Tên")
        name_column = None
        for col in df.columns:
            if 'tên' in str(col).lower() or col == df.columns[0]:
                name_column = col
                break

        if name_column is None:
            name_column = df.columns[0]



        # Tìm các cột môn học (bỏ qua cột tên và điểm TB)
        subject_columns = []
        for col in df.columns:
            col_str = str(col).strip()
            if (col != name_column and
                'tb' not in col_str.lower() and
                'điểm tb' not in col_str.lower() and
                col_str != ''):
                subject_columns.append(col)

        # Chuyển đổi sang định dạng dọc
        vertical_data = []

        for _, row in df.iterrows():
            student_name = row[name_column]

            # Bỏ qua hàng không có tên học sinh hợp lệ
            if (pd.isna(student_name) or
                str(student_name).strip() == '' or
                str(student_name).isdigit()):
                continue

            for subject_col in subject_columns:
                score = row[subject_col]
                if pd.notna(score):
                    try:
                        score_float = float(score)
                        if 0 <= score_float <= 10:  # Điểm hợp lệ
                            vertical_data.append({
                                'Tên học sinh': str(student_name).strip(),
                                'Lớp': '7A',
                                'Môn học': str(subject_col).strip(),
                                'Điểm': score_float
                            })
                    except (ValueError, TypeError):
                        continue

        return pd.DataFrame(vertical_data)

    def validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate và làm sạch dữ liệu"""

        # Phát hiện và chuyển đổi định dạng nếu cần
        df = self.detect_format_and_convert(df)

        # Chuẩn hóa tên cột
        df.columns = df.columns.str.strip().str.lower()

        # Mapping các tên cột có thể có
        column_mapping = {
            'tên học sinh': 'student_name',
            'ten hoc sinh': 'student_name',
            'họ tên': 'student_name',
            'ho ten': 'student_name',
            'lớp': 'class_name',
            'lop': 'class_name',
            'môn học': 'subject',
            'mon hoc': 'subject',
            'điểm': 'score',
            'diem': 'score'
        }

        # Đổi tên cột
        df = df.rename(columns=column_mapping)

        # Kiểm tra các cột bắt buộc
        required_columns = ['student_name', 'class_name', 'subject', 'score']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Thiếu các cột bắt buộc: {missing_columns}")

        # Làm sạch dữ liệu
        df = df.dropna(subset=required_columns)

        # Validate điểm số
        df['score'] = pd.to_numeric(df['score'], errors='coerce')
        df = df.dropna(subset=['score'])
        df = df[(df['score'] >= 0) & (df['score'] <= 10)]

        # Chuẩn hóa tên
        df['student_name'] = df['student_name'].str.strip().str.title()
        df['class_name'] = df['class_name'].str.strip().str.upper()
        df['subject'] = df['subject'].str.strip().str.title()

        return df
    
    def convert_to_students(self, df: pd.DataFrame) -> List[Student]:
        """Chuyển đổi DataFrame thành danh sách Student objects"""
        students_dict = {}
        student_counter = 1

        for _, row in df.iterrows():
            student_key = (row['student_name'], row['class_name'])

            if student_key not in students_dict:
                # Tạo ID tự động: HS001, HS002, ...
                student_id = f"HS{student_counter:03d}"
                students_dict[student_key] = Student(
                    id=student_id,
                    name=row['student_name'],
                    class_name=row['class_name'],
                    grades=[]
                )
                student_counter += 1

            grade = Grade(
                subject=row['subject'],
                score=row['score']
            )

            students_dict[student_key].grades.append(grade)

        return list(students_dict.values())
    
    def process_excel_file(self, file_content: bytes, filename: str) -> Tuple[str, List[Student], Dict]:
        """Xử lý file Excel hoàn chỉnh"""
        # Lưu file
        file_id = self.save_uploaded_file(file_content, filename)
        
        try:
            # Đọc file
            df = self.read_excel_file(file_id, filename)
            
            # Validate và làm sạch
            df_clean = self.validate_and_clean_data(df)
            
            # Chuyển đổi thành Student objects
            students = self.convert_to_students(df_clean)
            
            # Thống kê cơ bản
            stats = {
                'total_students': len(students),
                'total_subjects': len(df_clean['subject'].unique()),
                'total_records': len(df_clean),
                'subjects': df_clean['subject'].unique().tolist(),
                'classes': df_clean['class_name'].unique().tolist()
            }
            
            # Lưu thông tin đã xử lý
            self.processed_files[file_id] = {
                'filename': filename,
                'students': students,
                'stats': stats
            }
            
            return file_id, students, stats
            
        except Exception as e:
            # Xóa file nếu xử lý thất bại
            file_path = os.path.join(self.upload_dir, f"{file_id}_{filename}")
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
    
    def get_processed_data(self, file_id: str) -> Tuple[List[Student], Dict]:
        """Lấy dữ liệu đã xử lý theo file_id"""
        if file_id not in self.processed_files:
            raise ValueError(f"File ID {file_id} không tồn tại hoặc chưa được xử lý")

        data = self.processed_files[file_id]
        return data['students'], data['stats']

    def process_excel_in_memory(self, file_content: bytes, filename: str) -> List[Student]:
        """Xử lý file Excel trong memory mà không lưu file"""
        import io

        try:
            # Tạo BytesIO object từ file content
            file_buffer = io.BytesIO(file_content)

            # Đọc file từ memory
            if filename.endswith('.csv'):
                df = pd.read_csv(file_buffer, encoding='utf-8')
            else:
                df = pd.read_excel(file_buffer)

            # Validate và làm sạch dữ liệu
            df_clean = self.validate_and_clean_data(df)

            # Chuyển đổi thành Student objects
            students = self.convert_to_students(df_clean)

            return students

        except Exception as e:
            raise ValueError(f"Không thể xử lý file: {str(e)}")
