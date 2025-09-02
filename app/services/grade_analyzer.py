from typing import List, Dict
from app.models.schemas import (
    Student, StudentSummary, ClassStatistics, SubjectStatistics,
    GradeLevel, AnalysisResult, TopStudent
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

    def _get_student_grade_data(self, student: Student) -> Dict:
        """Helper method để lấy dữ liệu điểm của học sinh (tránh tính toán lặp lại)"""
        if not student.grades:
            return {
                'average_score': 0.0,
                'subject_scores': {},
                'all_scores': [],
                'math_score': 0.0,
                'literature_score': 0.0
            }

        average_score = self.calculate_student_average(student)
        subject_scores = {grade.subject.lower(): grade.score for grade in student.grades}
        all_scores = [grade.score for grade in student.grades]
        math_score = self._get_math_score(subject_scores)
        literature_score = self._get_literature_score(subject_scores)

        return {
            'average_score': average_score,
            'subject_scores': subject_scores,
            'all_scores': all_scores,
            'math_score': math_score,
            'literature_score': literature_score
        }
    
    def determine_grade_level(self, student: Student) -> GradeLevel:
        """
        Xác định xếp loại học lực theo tiêu chuẩn mới:

        Học sinh giỏi:
        - Điểm trung bình chung (TBC) >= 8.0
        - Không môn nào dưới 6.5
        - Ít nhất một trong hai môn Toán hoặc Ngữ văn >= 8.0

        Học sinh khá:
        - Điểm trung bình chung >= 6.5
        - Không môn nào dưới 5.0

        Học sinh trung bình:
        - Điểm trung bình chung >= 5.0
        - Không môn nào dưới 3.5

        Học sinh yếu: Các trường hợp còn lại
        """
        if not student.grades:
            return GradeLevel.WEAK

        # Sử dụng helper method để tránh tính toán lặp lại
        grade_data = self._get_student_grade_data(student)
        average_score = grade_data['average_score']
        all_scores = grade_data['all_scores']
        math_score = grade_data['math_score']
        literature_score = grade_data['literature_score']

        # Kiểm tra điều kiện học sinh giỏi
        if (average_score >= 8.0 and
            all(score >= 6.5 for score in all_scores) and
            (math_score >= 8.0 or literature_score >= 8.0)):
            return GradeLevel.EXCELLENT

        # Kiểm tra điều kiện học sinh khá
        elif (average_score >= 6.5 and
              all(score >= 5.0 for score in all_scores)):
            return GradeLevel.GOOD

        # Kiểm tra điều kiện học sinh trung bình
        elif (average_score >= 5.0 and
              all(score >= 3.5 for score in all_scores)):
            return GradeLevel.AVERAGE

        # Các trường hợp còn lại
        else:
            return GradeLevel.WEAK

    def _get_math_score(self, subject_scores: dict) -> float:
        """Lấy điểm môn Toán (có thể có nhiều tên khác nhau)"""
        math_names = ['toán', 'toan', 'math', 'mathematics', 'toán học', 'toan hoc']
        for name in math_names:
            if name in subject_scores:
                return subject_scores[name]
        return 0.0

    def _get_literature_score(self, subject_scores: dict) -> float:
        """Lấy điểm môn Ngữ văn (có thể có nhiều tên khác nhau)"""
        literature_names = ['ngữ văn', 'ngu van', 'văn', 'van', 'literature', 'vietnamese', 'tiếng việt', 'tieng viet']
        for name in literature_names:
            if name in subject_scores:
                return subject_scores[name]
        return 0.0

    def _determine_grade_level_by_score(self, score: float) -> GradeLevel:
        """Xác định xếp loại chỉ dựa trên điểm số (dùng cho thống kê môn học)"""
        if score >= self.grade_thresholds[GradeLevel.EXCELLENT]:
            return GradeLevel.EXCELLENT
        elif score >= self.grade_thresholds[GradeLevel.GOOD]:
            return GradeLevel.GOOD
        elif score >= self.grade_thresholds[GradeLevel.AVERAGE]:
            return GradeLevel.AVERAGE
        else:
            return GradeLevel.WEAK

    def check_excellent_student_conditions(self, student: Student) -> dict:
        """
        Kiểm tra chi tiết các điều kiện để được xếp loại học sinh giỏi
        Trả về dict với thông tin chi tiết về từng điều kiện
        """
        if not student.grades:
            return {
                'is_excellent': False,
                'average_score': 0.0,
                'average_condition': False,
                'min_score_condition': False,
                'math_literature_condition': False,
                'details': 'Không có điểm số'
            }

        # Sử dụng helper method để tránh tính toán lặp lại
        grade_data = self._get_student_grade_data(student)
        average_score = grade_data['average_score']
        all_scores = grade_data['all_scores']
        math_score = grade_data['math_score']
        literature_score = grade_data['literature_score']

        # Kiểm tra từng điều kiện
        average_condition = average_score >= 8.0
        min_score_condition = all(score >= 6.5 for score in all_scores)
        math_literature_condition = math_score >= 8.0 or literature_score >= 8.0

        is_excellent = average_condition and min_score_condition and math_literature_condition

        # Tạo thông tin chi tiết
        details = []
        if not average_condition:
            details.append(f"Điểm TB chung {average_score:.2f} < 8.0")
        if not min_score_condition:
            low_scores = [f"{grade.subject}: {grade.score}" for grade in student.grades if grade.score < 6.5]
            details.append(f"Có môn dưới 6.5: {', '.join(low_scores)}")
        if not math_literature_condition:
            details.append(f"Toán: {math_score:.1f}, Văn: {literature_score:.1f} (cần ít nhất 1 môn ≥ 8.0)")

        return {
            'is_excellent': is_excellent,
            'average_score': average_score,
            'average_condition': average_condition,
            'min_score_condition': min_score_condition,
            'math_literature_condition': math_literature_condition,
            'math_score': math_score,
            'literature_score': literature_score,
            'details': '; '.join(details) if details else 'Đạt tất cả điều kiện học sinh giỏi'
        }
    
    def identify_weak_subjects(self, student: Student, threshold: float = 5.0) -> List[str]:
        """Xác định các môn học yếu"""
        return [grade.subject for grade in student.grades if grade.score < threshold]
    
    def identify_strong_subjects(self, student: Student, threshold: float = 8.0) -> List[str]:
        """Xác định các môn học mạnh"""
        return [grade.subject for grade in student.grades if grade.score >= threshold]
    
    def analyze_student(self, student: Student, rank: int = 0) -> StudentSummary:
        """Phân tích chi tiết một học sinh"""
        average_score = self.calculate_student_average(student)
        grade_level = self.determine_grade_level(student)  # Truyền student thay vì average_score
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
                    grade_level = self._determine_grade_level_by_score(grade.score)
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

        # Lấy tên lớp (giả sử tất cả học sinh cùng lớp)
        class_name = students[0].class_name

        # Tính điểm trung bình một lần cho tất cả học sinh
        student_scores = [(student.name, self.calculate_student_average(student)) for student in students]
        student_averages = [score for _, score in student_scores]

        overall_average = round(sum(student_averages) / len(student_averages), 2)
        highest_score = max(student_averages)
        lowest_score = min(student_averages)

        # Phân bố xếp loại
        grade_distribution = {level.value: 0 for level in GradeLevel}
        for student in students:
            grade_level = self.determine_grade_level(student)
            grade_distribution[grade_level.value] += 1

        # Sắp xếp học sinh theo điểm
        student_scores.sort(key=lambda x: x[1], reverse=True)

        # Top 5 học sinh giỏi nhất
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
        students = [summary.student for summary in student_summaries]

        # Gọi các phương thức con để tạo gợi ý
        recommendations.extend(self._get_weak_subject_recommendations(class_stats))
        recommendations.extend(self._get_weak_student_recommendations(student_summaries))
        recommendations.extend(self._get_study_group_recommendations(student_summaries))
        recommendations.extend(self._get_strong_subject_recommendations(class_stats))
        recommendations.extend(self._get_critical_student_warnings(student_summaries))
        recommendations.extend(self._get_class_quality_assessment(class_stats))
        recommendations.extend(self._get_excellent_potential_analysis(students))
        recommendations.extend(self._get_excellent_conditions_statistics(students))

        return recommendations

    def _get_weak_subject_recommendations(self, class_stats: ClassStatistics) -> List[str]:
        """Gợi ý về môn học cần phụ đạo"""
        recommendations = []
        for subject_stat in class_stats.subject_statistics:
            weak_percentage = (subject_stat.weak_count / subject_stat.total_students) * 100
            if weak_percentage > 25:  # Nếu >25% học sinh yếu môn này
                recommendations.append(
                    f"📚 Môn {subject_stat.subject}: {weak_percentage:.1f}% học sinh yếu "
                    f"({subject_stat.weak_count}/{subject_stat.total_students}). "
                    f"Cần tổ chức lớp phụ đạo."
                )
        return recommendations

    def _get_weak_student_recommendations(self, student_summaries: List[StudentSummary]) -> List[str]:
        """Gợi ý cá nhân hóa cho học sinh yếu"""
        recommendations = []
        weak_students = [s for s in student_summaries if s.grade_level == GradeLevel.WEAK]
        if weak_students:
            recommendations.append(f"👥 Học sinh cần hỗ trợ cá nhân ({len(weak_students)} em):")
            for student in weak_students[:3]:  # Chỉ hiển thị 3 em đầu
                weak_subjects_str = ", ".join(student.weak_subjects[:3])
                recommendations.append(
                    f"   • {student.student.name} (TB: {student.average_score}) - "
                    f"Yếu: {weak_subjects_str}"
                )
            if len(weak_students) > 3:
                recommendations.append(f"   • ... và {len(weak_students) - 3} học sinh khác")
        return recommendations

    def _get_study_group_recommendations(self, student_summaries: List[StudentSummary]) -> List[str]:
        """Gợi ý nhóm học tập"""
        recommendations = []
        excellent_students = [s for s in student_summaries if s.grade_level == GradeLevel.EXCELLENT]
        weak_students = [s for s in student_summaries if s.grade_level == GradeLevel.WEAK]

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
        return recommendations

    def _get_strong_subject_recommendations(self, class_stats: ClassStatistics) -> List[str]:
        """Gợi ý về môn học mạnh"""
        recommendations = []
        strong_subjects = [subject_stat.subject for subject_stat in class_stats.subject_statistics
                          if subject_stat.average_score >= 7.5]

        if strong_subjects:
            recommendations.append(
                f"⭐ Môn học mạnh của lớp: {', '.join(strong_subjects)}. "
                f"Có thể áp dụng phương pháp giảng dạy tương tự cho các môn khác."
            )
        return recommendations

    def _get_critical_student_warnings(self, student_summaries: List[StudentSummary]) -> List[str]:
        """Cảnh báo khẩn cấp cho học sinh có điểm quá thấp"""
        recommendations = []
        critical_students = [s for s in student_summaries if s.average_score < 4.0]
        if critical_students:
            recommendations.append(
                f"🚨 CẢNH BÁO: {len(critical_students)} học sinh có điểm TB < 4.0, "
                f"cần can thiệp khẩn cấp để tránh bỏ học."
            )
        return recommendations

    def _get_class_quality_assessment(self, class_stats: ClassStatistics) -> List[str]:
        """Đánh giá chất lượng tổng quan của lớp"""
        recommendations = []
        total_students = class_stats.total_students
        good_students = (class_stats.grade_distribution.get(GradeLevel.EXCELLENT.value, 0) +
                        class_stats.grade_distribution.get(GradeLevel.GOOD.value, 0))

        if good_students / total_students >= 0.6:
            recommendations.append(
                f"✅ Lớp học có chất lượng tốt với {good_students}/{total_students} "
                f"học sinh đạt từ khá trở lên ({good_students/total_students*100:.1f}%)."
            )
        return recommendations

    def _get_excellent_potential_analysis(self, students: List[Student]) -> List[str]:
        """Phân tích học sinh có tiềm năng đạt loại giỏi"""
        recommendations = []
        near_excellent_students = []

        for student in students:
            conditions = self.check_excellent_student_conditions(student)
            if not conditions['is_excellent'] and conditions['average_score'] >= 7.5:
                near_excellent_students.append((student.name, conditions))

        if near_excellent_students:
            recommendations.append("🎯 **Học sinh có tiềm năng đạt loại giỏi:**")
            for name, conditions in near_excellent_students[:3]:  # Top 3
                recommendations.append(f"   • {name}: {conditions['details']}")
        return recommendations

    def _get_excellent_conditions_statistics(self, students: List[Student]) -> List[str]:
        """Thống kê về điều kiện học sinh giỏi"""
        recommendations = []
        excellent_analysis = self._analyze_excellent_conditions(students)
        if excellent_analysis['total_students'] > 0:
            recommendations.append(
                f"📊 **Phân tích điều kiện học sinh giỏi:** "
                f"{excellent_analysis['students_with_good_average']}/{excellent_analysis['total_students']} "
                f"có TB ≥ 8.0, "
                f"{excellent_analysis['students_no_low_scores']}/{excellent_analysis['total_students']} "
                f"không có môn < 6.5, "
                f"{excellent_analysis['students_math_lit_good']}/{excellent_analysis['total_students']} "
                f"có Toán hoặc Văn ≥ 8.0"
            )
        return recommendations

    def _analyze_excellent_conditions(self, students: List[Student]) -> dict:
        """Phân tích chi tiết các điều kiện học sinh giỏi trong lớp"""
        total_students = len(students)
        students_with_good_average = 0
        students_no_low_scores = 0
        students_math_lit_good = 0

        for student in students:
            conditions = self.check_excellent_student_conditions(student)
            if conditions['average_condition']:
                students_with_good_average += 1
            if conditions['min_score_condition']:
                students_no_low_scores += 1
            if conditions['math_literature_condition']:
                students_math_lit_good += 1

        return {
            'total_students': total_students,
            'students_with_good_average': students_with_good_average,
            'students_no_low_scores': students_no_low_scores,
            'students_math_lit_good': students_math_lit_good
        }
    
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
        for rank, (student, _) in enumerate(student_scores, 1):  # Use _ for unused score
            summary = self.analyze_student(student, rank)
            summaries.append(summary)

        return summaries
