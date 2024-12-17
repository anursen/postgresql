import psycopg2
from models import Question, User, Exam

def create_connection():
    return psycopg2.connect(
        user="user",
        password="password",
        host="localhost",
        port="5432",
        database="mydatabase"
    )

def create_question(question: Question):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO questions (id, text, choices, correct_choice) VALUES (%s, %s, %s, %s)",
        (question.id, question.text, question.choices, question.correct_choice)
    )
    connection.commit()
    cursor.close()
    connection.close()

def create_user(user: User):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (id, username, email, hashed_password) VALUES (%s, %s, %s, %s)",
        (user.id, user.username, user.email, user.hashed_password)
    )
    connection.commit()
    cursor.close()
    connection.close()

def create_exam(exam: Exam):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO exams (id, title, questions, user_id) VALUES (%s, %s, %s, %s)",
        (exam.id, exam.title, exam.questions, exam.user_id)
    )
    connection.commit()
    cursor.close()
    connection.close()

def save_response(question_id: int, response: str):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO responses (question_id, response) VALUES (%s, %s)",
        (question_id, response)
    )
    connection.commit()
    cursor.close()
    connection.close()
