from pydantic import BaseModel
from typing import List, Optional

class Question(BaseModel):
    id: int
    type: str
    text: str
    answer: str
    score: int
    section: str

class User(BaseModel):
    id: int
    name: str
    surname: str
    teacher: bool
    password: str

class Answer(BaseModel):
    question_id: int
    answer: str

class Exam(BaseModel):
    exam_id: int
    user_id: int
    question_id: int
    answer: str
    correct: bool
    score: int
    timestamp: str
