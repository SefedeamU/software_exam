from typing import List
from pydantic import BaseModel, Field, field_validator

class Evaluation(BaseModel):
    """
    Represents a single evaluation with a score and a weight.
    """
    name: str
    score: float = Field(..., ge=0, le=20, description="Score between 0 and 20")
    weight: float = Field(..., gt=0, le=100, description="Weight percentage")

class Student(BaseModel):
    """
    Represents a student and their academic records.
    """
    id: str
    evaluations: List[Evaluation] = []
    has_reached_minimum_classes: bool = True

    @field_validator('evaluations')
    @classmethod
    def check_max_evaluations(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 evaluations allowed per student')
        return v

class GradeCalculationResult(BaseModel):
    """
    Output of the grade calculation process.
    """
    final_grade: float
    average: float
    penalty_applied: bool
    extra_points_applied: bool
    details: str

class AttendancePolicy:
    """
    Encapsulates the logic for attendance requirements.
    """
    @staticmethod
    def apply_penalty(grade: float, has_reached_min: bool) -> float:
        """
        If minimum attendance is not reached, the student fails automatically or gets a penalty.
        Assumption: If attendance is not met, the max grade is capped at 10 or reduced.
        For this implementation: If not met, grade is reduced by 30% as a penalty example,
        or we could fail them. Let's apply a 30% penalty for flexibility.
        """
        if not has_reached_min:
            return grade * 0.7
        return grade

class ExtraPointsPolicy:
    """
    Encapsulates the logic for extra points.
    """
    @staticmethod
    def apply_extra(grade: float, all_years_teachers: bool) -> float:
        """
        If teachers agree (all_years_teachers is True), add 1 point (up to 20).
        """
        if all_years_teachers:
            return min(20.0, grade + 1.0)
        return grade

class GradeCalculator:
    """
    Main domain service for calculating grades.
    """
    def __init__(self, attendance_policy: AttendancePolicy, extra_policy: ExtraPointsPolicy):
        self.attendance_policy = attendance_policy
        self.extra_policy = extra_policy

    def calculate(self, student: Student, all_years_teachers: bool) -> GradeCalculationResult:
        if not student.evaluations:
            return GradeCalculationResult(
                final_grade=0.0,
                average=0.0,
                penalty_applied=not student.has_reached_minimum_classes,
                extra_points_applied=False,
                details="No evaluations registered."
            )

        # Calculate weighted average
        total_weight = sum(e.weight for e in student.evaluations)
        if total_weight == 0:
             return GradeCalculationResult(
                final_grade=0.0,
                average=0.0,
                penalty_applied=False,
                extra_points_applied=False,
                details="Total weight is zero."
            )
        
        # Normalize weights if they don't sum to 100? 
        # Requirement says "percentage of weight on final note". 
        # Usually we assume they sum to 100, or we calculate based on what's there.
        # Let's calculate weighted sum / total_weight to be safe.
        weighted_sum = sum(e.score * e.weight for e in student.evaluations)
        average = weighted_sum / total_weight

        current_grade = average

        # Apply Attendance Policy
        grade_after_attendance = self.attendance_policy.apply_penalty(current_grade, student.has_reached_minimum_classes)
        penalty_applied = grade_after_attendance < current_grade
        current_grade = grade_after_attendance

        # Apply Extra Points Policy
        grade_after_extra = self.extra_policy.apply_extra(current_grade, all_years_teachers)
        extra_applied = grade_after_extra > current_grade
        final_grade = grade_after_extra

        details = (
            f"Average: {average:.2f}. "
            f"Penalty: {'Yes' if penalty_applied else 'No'}. "
            f"Extra Points: {'Yes' if extra_applied else 'No'}."
        )

        return GradeCalculationResult(
            final_grade=round(final_grade, 2),
            average=round(average, 2),
            penalty_applied=penalty_applied,
            extra_points_applied=extra_applied,
            details=details
        )
