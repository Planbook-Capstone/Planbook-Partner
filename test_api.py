#!/usr/bin/env python3
"""
Unified API Testing Script
Gộp tất cả các test và demo vào 1 file duy nhất
"""

import requests
import webbrowser
import sys

API_URL = "http://localhost:8000/api/v1/upload-and-analyze"
EXCEL_FILE = "bang_diem_format_ngang.xlsx"

def test_basic():
    """Test cơ bản API upload và phân tích"""
    print("🚀 Test cơ bản API...")
    
    with open(EXCEL_FILE, "rb") as f:
        files = {"file": (EXCEL_FILE, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = requests.post(API_URL, files=files)
    
    if response.status_code == 200:
        result = response.json()
        class_stats = result['class_statistics']
        
        print("✅ Phân tích thành công!")
        print(f"📊 Lớp {class_stats['class_name']}: {class_stats['total_students']} học sinh")
        print(f"📈 Điểm TB: {class_stats['overall_average']} | Cao nhất: {class_stats['highest_score']} | Thấp nhất: {class_stats['lowest_score']}")
        
        print("\n🏅 TOP 5 HỌC SINH:")
        for student in result['student_summaries'][:5]:
            print(f"   #{student['rank']}. {student['student']['name']}: {student['average_score']} ({student['grade_level']})")
        
        print(f"\n📚 PASS RATE TOP 3 MÔN:")
        top_subjects = sorted(class_stats['subject_statistics'], key=lambda x: x['pass_rate'], reverse=True)[:3]
        for subject in top_subjects:
            print(f"   📈 {subject['subject']}: {subject['pass_rate']}%")
        
        return True
    else:
        print(f"❌ Lỗi: {response.status_code} - {response.text}")
        return False

def test_detailed():
    """Test chi tiết với tất cả thông tin"""
    print("\n" + "="*60)
    print("🎯 TEST CHI TIẾT - TẤT CẢ TÍNH NĂNG")
    print("="*60)
    
    with open(EXCEL_FILE, "rb") as f:
        files = {"file": (EXCEL_FILE, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = requests.post(API_URL, files=files)
    
    if response.status_code == 200:
        result = response.json()
        class_stats = result['class_statistics']
        
        # 1. Thông tin học sinh với ID và rank
        print("\n👥 HỌC SINH (ID + RANK):")
        for student in result['student_summaries']:
            s = student['student']
            print(f"   #{student['rank']:2d}. {s['id']} | {s['name']:<20} | TB: {student['average_score']:5.2f} | {student['grade_level']}")
        
        # 2. Thống kê lớp đầy đủ
        print(f"\n📊 THỐNG KÊ LỚP {class_stats['class_name']}:")
        print(f"   👨‍🎓 Tổng: {class_stats['total_students']} | TB: {class_stats['overall_average']}")
        print(f"   🏆 Cao nhất: {class_stats['highest_score']} | ⚠️ Thấp nhất: {class_stats['lowest_score']}")
        
        # 3. Phân bố xếp loại
        print(f"\n🏆 PHÂN BỐ XẾP LOẠI:")
        for grade, count in class_stats['grade_distribution'].items():
            percentage = (count / class_stats['total_students']) * 100
            print(f"   {grade}: {count} học sinh ({percentage:.1f}%)")
        
        # 4. Thống kê môn học với pass rate
        print(f"\n📚 THỐNG KÊ 12 MÔN HỌC:")
        for subject in class_stats['subject_statistics']:
            print(f"   📖 {subject['subject']}:")
            print(f"      TB: {subject['average_score']} | Pass rate: {subject['pass_rate']}%")
            print(f"      Cao nhất: {subject['highest_score']} ({subject['highest_score_student']})")
            print(f"      Thấp nhất: {subject['lowest_score']} ({subject['lowest_score_student']})")
        
        # 5. Gợi ý cải thiện
        print(f"\n💡 GỢI Ý CẢI THIỆN:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # 6. Tóm tắt pass rate
        total_pass = sum(s['pass_rate'] for s in class_stats['subject_statistics'])
        avg_pass_rate = total_pass / len(class_stats['subject_statistics'])
        print(f"\n📈 PASS RATE TRUNG BÌNH: {avg_pass_rate:.1f}%")
        
        return True
    else:
        print(f"❌ Lỗi: {response.status_code} - {response.text}")
        return False

def open_swagger():
    """Mở Swagger UI"""
    print("\n🌐 Mở Swagger UI...")
    webbrowser.open("http://localhost:8000/docs")
    print("✅ Đã mở Swagger UI!")
    print("\n📋 HƯỚNG DẪN:")
    print("1. Tìm endpoint: POST /api/v1/upload-and-analyze")
    print("2. Click 'Try it out'")
    print(f"3. Upload file: {EXCEL_FILE}")
    print("4. Click 'Execute'")

def show_summary():
    """Hiển thị tóm tắt tính năng"""
    print("\n" + "="*50)
    print("🎉 TÓM TẮT TÍNH NĂNG")
    print("="*50)
    print("✅ ID tự động: HS001, HS002, HS003...")
    print("✅ Rank: #1, #2, #3... theo điểm TB")
    print("✅ Pass rate: % học sinh đạt ≥5.0 từng môn")
    print("✅ Highest/Lowest score student")
    print("✅ Top/Weak students")
    print("✅ Gợi ý cá nhân hóa")
    print("✅ Bảng xếp hạng đầy đủ")
    print("✅ Thống kê chi tiết 12 môn học")

def main():
    """Menu chính"""
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("🎯 CHỌN CHẾ ĐỘ TEST:")
        print("1. Test cơ bản")
        print("2. Test chi tiết")
        print("3. Mở Swagger UI")
        print("4. Tóm tắt tính năng")
        choice = input("Nhập lựa chọn (1-4): ").strip()
        mode = {"1": "basic", "2": "detailed", "3": "swagger", "4": "summary"}.get(choice, "basic")
    
    if mode == "basic":
        test_basic()
    elif mode == "detailed":
        test_detailed()
    elif mode == "swagger":
        open_swagger()
    elif mode == "summary":
        show_summary()
    else:
        print("❌ Chế độ không hợp lệ. Sử dụng: basic, detailed, swagger, summary")

if __name__ == "__main__":
    main()
