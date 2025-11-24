from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/grade_calculator")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class StudentDB(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, index=True)
    has_reached_minimum_classes = Column(Boolean, default=True)
    
    evaluations = relationship("EvaluationDB", back_populates="student")

class EvaluationDB(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    score = Column(Float)
    weight = Column(Float)
    student_id = Column(String, ForeignKey("students.id"))

    student = relationship("StudentDB", back_populates="evaluations")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
