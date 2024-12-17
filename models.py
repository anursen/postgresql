from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    id: int
    text: str
    choices: List[str]
    correct_choice: int

class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str

class Exam(BaseModel):
    id: int
    title: str
    questions: List[Question]
    user_id: int
