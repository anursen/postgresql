import psycopg2

def create_connection():
    return psycopg2.connect(
        user="admin",
        password="1234",
        host="db",  # Use the service name defined in docker-compose.yaml
        port="5432",
        database="postgres"
    )

def fetch_questions():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, type, text, answer, score, section FROM questions")
    questions = cursor.fetchall()
    cursor.close()
    connection.close()
    # Convert the fetched data to a list of dictionaries
    questions_list = []
    for question in questions:
        questions_list.append({
            'id': question[0],
            'type': question[1],
            'text': question[2],
            'answer': question[3],  # Handle as a single string
            'score': question[4],
            'section': question[5]
        })
    return questions_list

def fetch_questions_by_section(section):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, type, text, answer, score, section FROM questions WHERE section = %s", (section,))
    questions = cursor.fetchall()
    cursor.close()
    connection.close()
    # Convert the fetched data to a list of dictionaries
    questions_list = []
    for question in questions:
        questions_list.append({
            'id': question[0],
            'type': question[1],
            'text': question[2],
            'answer': question[3],  # Handle as a single string
            'score': question[4],
            'section': question[5]
        })
    return questions_list

def fetch_responses():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM responses")
    responses = cursor.fetchall()
    cursor.close()
    connection.close()
    return responses

def fetch_users():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, surname, email, teacher, admin FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    # Convert the fetched data to a list of dictionaries
    users_list = []
    for user in users:
        users_list.append({
            'id': user[0],
            'name': user[1],
            'surname': user[2],
            'email': user[3],
            'teacher': user[4],
            'admin': user[5]
        })
    return users_list

def fetch_non_admin_users():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, surname FROM users WHERE admin = FALSE")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    # Convert the fetched data to a list of dictionaries
    users_list = []
    for user in users:
        users_list.append({
            'id': user[0],
            'name': user[1],
            'surname': user[2]
        })
    return users_list

def validate_user(user_id, password):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s AND password = %s", (user_id, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

def create_exam_entry(user_id, question_id, answer, correct, score, exam_id=None):
    connection = create_connection()
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
    connection.close()
    return exam_id

def fetch_unique_sections():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT section FROM questions")
    sections = cursor.fetchall()
    cursor.close()
    connection.close()
    # Convert the fetched data to a list of sections
    sections_list = [section[0] for section in sections]
    return sections_list

def fetch_first_question_id(section=None):
    connection = create_connection()
    cursor = connection.cursor()
    if section:
        cursor.execute("SELECT id FROM questions WHERE section = %s ORDER BY id LIMIT 1", (section,))
    else:
        cursor.execute("SELECT id FROM questions ORDER BY id LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0] if result else None
