import psycopg2
from models import Question, User, Exam

def create_connection():
    return psycopg2.connect(
        user="admin",
        password="1234",
        host="db",  # Use the service name defined in docker-compose.yaml
        port="5432",
        database="postgres"
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
        "INSERT INTO users (name, surname, email, teacher, admin, password) VALUES (%s, %s, %s, %s, %s, %s)",
        (user.name, user.surname, user.email, user.teacher, user.admin, user.password)
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

def check_response_correctness(question_id: int, response: str) -> bool:
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT answer FROM questions WHERE id = %s", (question_id,))
    correct_answer = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return response.strip().lower() == correct_answer.strip().lower()

def calculate_score(question_id: int, correct: bool) -> int:
    if correct:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT score FROM questions WHERE id = %s", (question_id,))
        score = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return score
    return 0

def save_response(user_id: int, question_id: int, response: str, exam_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    correct = check_response_correctness(question_id, response)
    score = calculate_score(question_id, correct)
    cursor.execute(
        "INSERT INTO exams (exam_id, user_id, question_id, answer, correct, score) VALUES (%s, %s, %s, %s, %s, %s)",
        (exam_id, user_id, question_id, response, correct, score)
    )
    connection.commit()
    cursor.close()
    connection.close()

def delete_question(question_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM questions WHERE id = %s",
        (question_id,)
    )
    connection.commit()
    cursor.close()
    connection.close()

def delete_user(user_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM users WHERE id = %s",
        (user_id,)
    )
    connection.commit()
    cursor.close()
    connection.close()
