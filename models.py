from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[int] = None
    name: str
    surname: str
    email: str
    teacher: bool
    admin: bool
    password: str

class Question(BaseModel):
    id: Optional[int] = None
    type: str
    text: str
    answer: str
    score: int
    section: str

class Responses(BaseModel):
    id: Optional[int] = None
    exam_id: int
    user_id: int
    question_id: int
    answer: str
    result: Optional[bool] = None
    score: Optional[int] = None
    submit_time: datetime

class ExamConfig(BaseModel):
    question_time: int
    question_count: int
    exam_duration: int
    passing_score: int
    shuffle_questions: bool


class Exams(BaseModel):
    exam_id: Optional[int] = None
    user_id: int
    start_time: datetime
    end_time: datetime
    config: ExamConfig
    completed: bool = False
    total_score: int = 0

class AdminSettings(BaseModel):
    question_time: int
    question_count: int
    exam_duration: int
    passing_score: int
    max_attempts: int
    shuffle_questions: bool
    enable_notifications: bool