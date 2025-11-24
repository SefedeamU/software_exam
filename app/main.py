from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import engine, Base, get_db, StudentDB, EvaluationDB
from app.models.domain import Student, Evaluation, GradeCalculator, AttendancePolicy, ExtraPointsPolicy, GradeCalculationResult
from pydantic import BaseModel

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CS-GradeCalculator", description="API for calculating student grades")

# Dependency injection for domain services
attendance_policy = AttendancePolicy()
extra_points_policy = ExtraPointsPolicy()
calculator = GradeCalculator(attendance_policy, extra_points_policy)

class CreateEvaluationRequest(BaseModel):
    name: str
    score: float
    weight: float

class UpdateAttendanceRequest(BaseModel):
    has_reached_minimum_classes: bool

class CalculateRequest(BaseModel):
    all_years_teachers: bool

@app.post("/students/{student_id}", response_model=Student)
def create_student(student_id: str, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Student already exists")
    
    new_student = StudentDB(id=student_id, has_reached_minimum_classes=True)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return Student(id=new_student.id, has_reached_minimum_classes=new_student.has_reached_minimum_classes, evaluations=[])

@app.post("/students/{student_id}/evaluations", response_model=Evaluation)
def add_evaluation(student_id: str, evaluation: CreateEvaluationRequest, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check constraint RNF01
    if len(db_student.evaluations) >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 evaluations allowed")

    new_eval = EvaluationDB(
        name=evaluation.name,
        score=evaluation.score,
        weight=evaluation.weight,
        student_id=student_id
    )
    db.add(new_eval)
    db.commit()
    db.refresh(new_eval)
    return Evaluation(name=new_eval.name, score=new_eval.score, weight=new_eval.weight)

@app.put("/students/{student_id}/attendance", response_model=Student)
def update_attendance(student_id: str, request: UpdateAttendanceRequest, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_student.has_reached_minimum_classes = request.has_reached_minimum_classes
    db.commit()
    db.refresh(db_student)
    
    # Convert DB model to Domain model
    evals = [Evaluation(name=e.name, score=e.score, weight=e.weight) for e in db_student.evaluations]
    return Student(id=db_student.id, evaluations=evals, has_reached_minimum_classes=db_student.has_reached_minimum_classes)

@app.post("/calculate/{student_id}", response_model=GradeCalculationResult)
def calculate_grade(student_id: str, request: CalculateRequest, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Map DB to Domain
    domain_evals = [Evaluation(name=e.name, score=e.score, weight=e.weight) for e in db_student.evaluations]
    domain_student = Student(
        id=db_student.id,
        evaluations=domain_evals,
        has_reached_minimum_classes=db_student.has_reached_minimum_classes
    )
    
    result = calculator.calculate(domain_student, request.all_years_teachers)
    return result
