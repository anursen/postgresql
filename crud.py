import psycopg2
from contextlib import contextmanager
from models import User, Question, Responses, ExamConfig, Exams, AdminSettings

@contextmanager
def get_db_connection():
    connection = psycopg2.connect(
        user="admin",
        password="1234",
        host="db",  # Use the service name defined in docker-compose.yaml
        port="5432",
        database="postgres"
    )
    try:
        yield connection
    finally:
        connection.close()

class QuestionCRUD:
    @staticmethod
    def create_question(question: Question):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO questions (type, text, answer, score, section) VALUES (%s, %s, %s, %s, %s)",
                (question.type, question.text, question.answer, question.score, question.section)
            )
            connection.commit()
            cursor.close()

    @staticmethod
    def fetch_questions():
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, type, text, answer, score, section FROM questions")
            questions = cursor.fetchall()
            cursor.close()
        questions_list = [
            {
                'id': question[0],
                'type': question[1],
                'text': question[2],
                'answer': question[3],
                'score': question[4],
                'section': question[5]
            }
            for question in questions
        ]
        return questions_list

    @staticmethod
    def fetch_questions_by_section(section):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, type, text, answer, score, section FROM questions WHERE section = %s", (section,))
            questions = cursor.fetchall()
            cursor.close()
        questions_list = [
            {
                'id': question[0],
                'type': question[1],
                'text': question[2],
                'answer': question[3],
                'score': question[4],
                'section': question[5]
            }
            for question in questions
        ]
        return questions_list

    @staticmethod
    def delete_question(question_id: int):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM questions WHERE id = %s",
                (question_id,)
            )
            connection.commit()
            cursor.close()

class UserCRUD:
    @staticmethod
    def create_user(user: User):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (name, surname, email, teacher, admin, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (user.name, user.surname, user.email, user.teacher, user.admin, user.password)
            )
            connection.commit()
            cursor.close()

    @staticmethod
    def fetch_users():
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, surname, email, teacher, admin FROM users")
            users = cursor.fetchall()
            cursor.close()
        users_list = [
            {
                'id': user[0],
                'name': user[1],
                'surname': user[2],
                'email': user[3],
                'teacher': user[4],
                'admin': user[5]
            }
            for user in users
        ]
        return users_list

    @staticmethod
    def fetch_non_admin_users():
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, surname FROM users WHERE admin = FALSE")
            users = cursor.fetchall()
            cursor.close()
        users_list = [
            {
                'id': user[0],
                'name': user[1],
                'surname': user[2]
            }
            for user in users
        ]
        return users_list

    @staticmethod
    def validate_user(user_id, password):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT id, name, surname, email 
                FROM users 
                WHERE id = %s AND password = %s AND admin = FALSE
                """, 
                (user_id, password)
            )
            user = cursor.fetchone()
            cursor.close()
            if user:
                return {
                    'id': user[0],
                    'name': user[1],
                    'surname': user[2],
                    'email': user[3]
                }
            return None

    @staticmethod
    def delete_user(user_id: int):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )
            connection.commit()
            cursor.close()

class ExamCRUD:
    @staticmethod
    def create_exam(exam: Exams):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO exams (
                    user_id, start_time, end_time, 
                    config, 
                    completed, total_score
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING exam_id
                """,
                (
                    exam.user_id,
                    exam.start_time,
                    exam.end_time,
                    exam.config.json(),  # Store config as JSON
                    exam.completed,
                    exam.total_score
                )
            )
            exam_id = cursor.fetchone()[0]
            connection.commit()
            cursor.close()
            return exam_id

    @staticmethod
    def create_exam_entry(user_id, question_id, answer, correct, score, exam_id=None):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            if exam_id is None:
                cursor.execute(
                    "INSERT INTO exams (user_id, question_id, answer, correct, score) VALUES (%s, %s, %s, %s, %s) RETURNING exam_id",
                    (user_id, question_id, answer, correct, score)
                )
                exam_id = cursor.fetchone()[0]
            else:
                cursor.execute(
                    "INSERT INTO exams (exam_id, user_id, question_id, answer, correct, score) VALUES (%s, %s, %s, %s, %s, %s)",
                    (exam_id, user_id, question_id, answer, correct, score)
                )
            connection.commit()
            cursor.close()
        return exam_id

    @staticmethod
    def save_response(user_id: int, question_id: int, response: str, exam_id: int):
        correct = ExamCRUD.check_response_correctness(question_id, response)
        score = ExamCRUD.calculate_score(question_id, correct)
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO exams (exam_id, user_id, question_id, answer, correct, score) VALUES (%s, %s, %s, %s, %s, %s)",
                (exam_id, user_id, question_id, response, correct, score)
            )
            connection.commit()
            cursor.close()

    @staticmethod
    def check_response_correctness(question_id: int, response: str) -> bool:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT answer FROM questions WHERE id = %s", (question_id,))
            correct_answer = cursor.fetchone()[0]
            cursor.close()
        return response.strip().lower() == correct_answer.strip().lower()

    @staticmethod
    def calculate_score(question_id: int, correct: bool) -> int:
        if correct:
            with get_db_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT score FROM questions WHERE id = %s", (question_id,))
                score = cursor.fetchone()[0]
                cursor.close()
            return score
        return 0

    @staticmethod
    def update_exam_score(exam_id: int, total_score: int):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE exams SET total_score = %s WHERE exam_id = %s",
                (total_score, exam_id)
            )
            connection.commit()
            cursor.close()

class AdminSettingsCRUD:
    @staticmethod
    def get_admin_settings():
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT question_time, question_count, exam_duration, passing_score, max_attempts, shuffle_questions, enable_notifications FROM admin_settings LIMIT 1")
            row = cursor.fetchone()
            cursor.close()
        if row:
            return {
                'question_time': int(row[0]),
                'question_count': int(row[1]),
                'exam_duration': int(row[2]),
                'passing_score': int(row[3]),
                'max_attempts': int(row[4]),
                'shuffle_questions': bool(row[5]),  # Explicitly convert to boolean
                'enable_notifications': bool(row[6])  # Explicitly convert to boolean
            }
        return None

    @staticmethod
    def update_admin_settings(settings):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO admin_settings (question_time, question_count, exam_duration, passing_score, max_attempts, shuffle_questions, enable_notifications)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                question_time = EXCLUDED.question_time,
                question_count = EXCLUDED.question_count,
                exam_duration = EXCLUDED.exam_duration,
                passing_score = EXCLUDED.passing_score,
                max_attempts = EXCLUDED.max_attempts,
                shuffle_questions = EXCLUDED.shuffle_questions,
                enable_notifications = EXCLUDED.enable_notifications
            """, (
                settings['question_time'],
                settings['question_count'],
                settings['exam_duration'],
                settings['passing_score'],
                settings['max_attempts'],
                settings['shuffle_questions'],
                settings['enable_notifications']
            ))
            connection.commit()
            cursor.close()

class ResponseCRUD:
    @staticmethod
    def create_response(response: Responses):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO responses (exam_id, user_id, question_id, answer, result, score, submit_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (response.exam_id, response.user_id, response.question_id, response.answer, response.result, response.score, response.submit_time)
            )
            connection.commit()
            cursor.close()

    @staticmethod
    def fetch_responses_by_exam(exam_id: int):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM responses WHERE exam_id = %s", (exam_id,))
            responses = cursor.fetchall()
            cursor.close()
        return [
            {
                'id': response[0],
                'exam_id': response[1],
                'user_id': response[2],
                'question_id': response[3],
                'answer': response[4],
                'result': response[5],
                'score': response[6],
                'submit_time': response[7]
            }
            for response in responses
        ]

    @staticmethod
    def update_response(response: Responses):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE responses
                SET result = %s, score = %s
                WHERE id = %s
                """,
                (response['result'], response['score'], response['id'])
            )
            connection.commit()
            cursor.close()
