from typing import List, Dict
from app.models.schemas import (
    Student, StudentSummary, ClassStatistics, SubjectStatistics, 
    GradeLevel, AnalysisResult
)


class GradeAnalyzer:
    def __init__(self):
        self.grade_thresholds = {
            GradeLevel.EXCELLENT: 8.0,
            GradeLevel.GOOD: 6.5,
            GradeLevel.AVERAGE: 5.0,
            GradeLevel.WEAK: 0.0
        }
    
    def calculate_student_average(self, student: Student) -> float:
        """Tính điểm trung bình của học sinh"""
        if not student.grades:
            return 0.0
        
        total_score = sum(grade.score for grade in student.grades)
        return round(total_score / len(student.grades), 2)
    
    def determine_grade_level(self, average_score: float) -> GradeLevel:
        """Xác định xếp loại học lực"""
        if average_score >= self.grade_thresholds[GradeLevel.EXCELLENT]:
            return GradeLevel.EXCELLENT
        elif average_score >= self.grade_thresholds[GradeLevel.GOOD]:
            return GradeLevel.GOOD
        elif average_score >= self.grade_thresholds[GradeLevel.AVERAGE]:
            return GradeLevel.AVERAGE
        else:
            return GradeLevel.WEAK
    
    def identify_weak_subjects(self, student: Student, threshold: float = 5.0) -> List[str]:
        """Xác định các môn học yếu"""
        return [grade.subject for grade in student.grades if grade.score < threshold]
    
    def identify_strong_subjects(self, student: Student, threshold: float = 8.0) -> List[str]:
        """Xác định các môn học mạnh"""
        return [grade.subject for grade in student.grades if grade.score >= threshold]
    
    def analyze_student(self, student: Student, rank: int = 0) -> StudentSummary:
        """Phân tích chi tiết một học sinh"""
        average_score = self.calculate_student_average(student)
        grade_level = self.determine_grade_level(average_score)
        weak_subjects = self.identify_weak_subjects(student)
        strong_subjects = self.identify_strong_subjects(student)

        return StudentSummary(
            student=student,
            average_score=average_score,
            rank=rank,
            grade_level=grade_level,
            weak_subjects=weak_subjects,
            strong_subjects=strong_subjects
        )
    
    def analyze_subject_statistics(self, students: List[Student], subject: str) -> SubjectStatistics:
        """Phân tích thống kê theo môn học"""
        subject_data = []
        grade_counts = {level: 0 for level in GradeLevel}

        for student in students:
            for grade in student.grades:
                if grade.subject == subject:
                    subject_data.append((student.name, grade.score))
                    grade_level = self.determine_grade_level(grade.score)
                    grade_counts[grade_level] += 1

        if not subject_data:
            return SubjectStatistics(
                subject=subject,
                average_score=0.0,
                highest_score=0.0,
                lowest_score=0.0,
                highest_score_student="",
                lowest_score_student="",
                total_students=0,
                pass_rate=0.0,
                excellent_count=0,
                good_count=0,
                average_count=0,
                weak_count=0
            )

        scores = [score for _, score in subject_data]
        average_score = round(sum(scores) / len(scores), 2)
        highest_score = max(scores)
        lowest_score = min(scores)

        # Tính tỉ lệ đạt (>=5.0)
        pass_count = sum(1 for score in scores if score >= 5.0)
        pass_rate = round((pass_count / len(scores)) * 100, 1)

        # Tìm học sinh đạt điểm cao nhất và thấp nhất
        highest_student = next(name for name, score in subject_data if score == highest_score)
        lowest_student = next(name for name, score in subject_data if score == lowest_score)

        return SubjectStatistics(
            subject=subject,
            average_score=average_score,
            highest_score=highest_score,
            lowest_score=lowest_score,
            highest_score_student=highest_student,
            lowest_score_student=lowest_student,
            total_students=len(subject_data),
            pass_rate=pass_rate,
            excellent_count=grade_counts[GradeLevel.EXCELLENT],
            good_count=grade_counts[GradeLevel.GOOD],
            average_count=grade_counts[GradeLevel.AVERAGE],
            weak_count=grade_counts[GradeLevel.WEAK]
        )
    
    def analyze_class_statistics(self, students: List[Student]) -> ClassStatistics:
        """Phân tích thống kê lớp học"""
        if not students:
            from app.models.schemas import TopStudent
            return ClassStatistics(
                class_name="",
                total_students=0,
                overall_average=0.0,
                highest_score=0.0,
                lowest_score=0.0,
                grade_distribution={},
                top_students=[],
                weak_students=[],
                subject_statistics=[]
            )

        from app.models.schemas import TopStudent

        # Lấy tên lớp (giả sử tất cả học sinh cùng lớp)
        class_name = students[0].class_name

        # Tính điểm trung bình chung
        student_averages = [self.calculate_student_average(student) for student in students]
        overall_average = round(sum(student_averages) / len(student_averages), 2)
        highest_score = max(student_averages)
        lowest_score = min(student_averages)

        # Phân bố xếp loại
        grade_distribution = {level.value: 0 for level in GradeLevel}
        for avg in student_averages:
            grade_level = self.determine_grade_level(avg)
            grade_distribution[grade_level.value] += 1

        # Top 5 học sinh giỏi nhất
        student_scores = [(student.name, self.calculate_student_average(student)) for student in students]
        student_scores.sort(key=lambda x: x[1], reverse=True)
        top_students = [TopStudent(name=name, score=score) for name, score in student_scores[:5]]

        # Học sinh yếu (điểm < 5.0)
        weak_students = [TopStudent(name=name, score=score) for name, score in student_scores if score < 5.0]

        # Lấy danh sách môn học
        all_subjects = set()
        for student in students:
            for grade in student.grades:
                all_subjects.add(grade.subject)

        # Thống kê theo môn
        subject_statistics = []
        for subject in sorted(all_subjects):
            subject_stats = self.analyze_subject_statistics(students, subject)
            subject_statistics.append(subject_stats)

        return ClassStatistics(
            class_name=class_name,
            total_students=len(students),
            overall_average=overall_average,
            highest_score=highest_score,
            lowest_score=lowest_score,
            grade_distribution=grade_distribution,
            top_students=top_students,
            weak_students=weak_students,
            subject_statistics=subject_statistics
        )
    
    def generate_recommendations(self, class_stats: ClassStatistics, student_summaries: List[StudentSummary]) -> List[str]:
        """Tạo gợi ý cải thiện chi tiết"""
        recommendations = []

        # 1. Gợi ý về môn học cần phụ đạo
        weak_subjects = []
        for subject_stat in class_stats.subject_statistics:
            weak_percentage = (subject_stat.weak_count / subject_stat.total_students) * 100
            if weak_percentage > 25:  # Nếu >25% học sinh yếu môn này
                weak_subjects.append(subject_stat.subject)
                recommendations.append(
                    f"📚 Môn {subject_stat.subject}: {weak_percentage:.1f}% học sinh yếu "
                    f"({subject_stat.weak_count}/{subject_stat.total_students}). "
                    f"Cần tổ chức lớp phụ đạo."
                )

        # 2. Gợi ý cá nhân hóa cho học sinh yếu
        weak_students = [s for s in student_summaries if s.grade_level == GradeLevel.WEAK]
        if weak_students:
            recommendations.append(
                f"👥 Học sinh cần hỗ trợ cá nhân ({len(weak_students)} em):"
            )
            for student in weak_students[:3]:  # Chỉ hiển thị 3 em đầu
                weak_subjects_str = ", ".join(student.weak_subjects[:3])
                recommendations.append(
                    f"   • {student.student.name} (TB: {student.average_score}) - "
                    f"Yếu: {weak_subjects_str}"
                )
            if len(weak_students) > 3:
                recommendations.append(f"   • ... và {len(weak_students) - 3} học sinh khác")

        # 3. Gợi ý nhóm học tập
        excellent_students = [s for s in student_summaries if s.grade_level == GradeLevel.EXCELLENT]
        if excellent_students and weak_students:
            recommendations.append(
                f"🤝 Đề xuất nhóm học tập: Ghép {len(excellent_students)} học sinh giỏi "
                f"với {len(weak_students)} học sinh yếu để hỗ trợ lẫn nhau."
            )

            # Gợi ý cặp cụ thể
            for i, excellent in enumerate(excellent_students[:2]):
                if i < len(weak_students):
                    recommendations.append(
                        f"   • {excellent.student.name} (TB: {excellent.average_score}) "
                        f"hỗ trợ {weak_students[i].student.name} (TB: {weak_students[i].average_score})"
                    )

        # 4. Gợi ý về môn học mạnh
        strong_subjects = []
        for subject_stat in class_stats.subject_statistics:
            if subject_stat.average_score >= 7.5:
                strong_subjects.append(subject_stat.subject)

        if strong_subjects:
            recommendations.append(
                f"⭐ Môn học mạnh của lớp: {', '.join(strong_subjects)}. "
                f"Có thể áp dụng phương pháp giảng dạy tương tự cho các môn khác."
            )

        # 5. Cảnh báo khẩn cấp
        critical_students = [s for s in student_summaries if s.average_score < 4.0]
        if critical_students:
            recommendations.append(
                f"🚨 CẢNH BÁO: {len(critical_students)} học sinh có điểm TB < 4.0, "
                f"cần can thiệp khẩn cấp để tránh bỏ học."
            )

        # 6. Thống kê tổng quan
        total_students = class_stats.total_students
        good_students = class_stats.grade_distribution.get(GradeLevel.EXCELLENT.value, 0) + \
                       class_stats.grade_distribution.get(GradeLevel.GOOD.value, 0)

        if good_students / total_students >= 0.6:
            recommendations.append(
                f"✅ Lớp học có chất lượng tốt với {good_students}/{total_students} "
                f"học sinh đạt từ khá trở lên ({good_students/total_students*100:.1f}%)."
            )

        return recommendations
    
    def analyze_complete(self, file_id: str, students: List[Student]) -> AnalysisResult:
        """Phân tích hoàn chỉnh"""
        # Phân tích từng học sinh với thứ hạng
        student_summaries = self.analyze_students_with_rank(students)

        # Phân tích thống kê lớp
        class_statistics = self.analyze_class_statistics(students)

        # Tạo gợi ý
        recommendations = self.generate_recommendations(class_statistics, student_summaries)

        return AnalysisResult(
            file_id=file_id,
            class_statistics=class_statistics,
            student_summaries=student_summaries,
            recommendations=recommendations
        )

    def analyze_students_with_rank(self, students: List[Student]) -> List[StudentSummary]:
        """Phân tích danh sách học sinh với thứ hạng"""
        # Tính điểm trung bình cho tất cả học sinh
        student_scores = [(student, self.calculate_student_average(student)) for student in students]

        # Sắp xếp theo điểm giảm dần để tính rank
        student_scores.sort(key=lambda x: x[1], reverse=True)

        # Tạo StudentSummary với rank
        summaries = []
        for rank, (student, score) in enumerate(student_scores, 1):
            summary = self.analyze_student(student, rank)
            summaries.append(summary)

        return summaries
