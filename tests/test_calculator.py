import pytest
from app.models.domain import Student, Evaluation, GradeCalculator, AttendancePolicy, ExtraPointsPolicy

@pytest.fixture
def calculator():
    return GradeCalculator(AttendancePolicy(), ExtraPointsPolicy())

def test_calculate_simple_average(calculator):
    student = Student(
        id="1",
        evaluations=[
            Evaluation(name="Exam 1", score=15, weight=50),
            Evaluation(name="Exam 2", score=17, weight=50)
        ],
        has_reached_minimum_classes=True
    )
    result = calculator.calculate(student, all_years_teachers=False)
    assert result.final_grade == 16.0
    assert result.penalty_applied is False
    assert result.extra_points_applied is False

def test_calculate_with_attendance_penalty(calculator):
    student = Student(
        id="2",
        evaluations=[
            Evaluation(name="Exam 1", score=20, weight=100)
        ],
        has_reached_minimum_classes=False
    )
    # Penalty is 30% reduction -> 20 * 0.7 = 14
    result = calculator.calculate(student, all_years_teachers=False)
    assert result.final_grade == 14.0
    assert result.penalty_applied is True

def test_calculate_with_extra_points(calculator):
    student = Student(
        id="3",
        evaluations=[
            Evaluation(name="Exam 1", score=15, weight=100)
        ],
        has_reached_minimum_classes=True
    )
    # Extra point +1 -> 16
    result = calculator.calculate(student, all_years_teachers=True)
    assert result.final_grade == 16.0
    assert result.extra_points_applied is True

def test_calculate_max_grade_cap(calculator):
    student = Student(
        id="4",
        evaluations=[
            Evaluation(name="Exam 1", score=20, weight=100)
        ],
        has_reached_minimum_classes=True
    )
    # Extra point +1 -> 21, but capped at 20
    result = calculator.calculate(student, all_years_teachers=True)
    assert result.final_grade == 20.0

def test_calculate_zero_evaluations(calculator):
    student = Student(id="5", evaluations=[], has_reached_minimum_classes=True)
    result = calculator.calculate(student, all_years_teachers=False)
    assert result.final_grade == 0.0

def test_calculate_uneven_weights(calculator):
    # Weights don't sum to 100, but logic handles it by dividing by sum
    student = Student(
        id="6",
        evaluations=[
            Evaluation(name="Exam 1", score=10, weight=20), # 200
            Evaluation(name="Exam 2", score=20, weight=20)  # 400
        ], # Total weight 40. Sum 600. Avg = 600/40 = 15.
        has_reached_minimum_classes=True
    )
    result = calculator.calculate(student, all_years_teachers=False)
    assert result.final_grade == 15.0
