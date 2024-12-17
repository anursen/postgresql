from flask import Flask, render_template, jsonify, request
from crud import save_response, delete_question, delete_user  # Import the new function
from database import fetch_questions, fetch_responses, fetch_users, fetch_non_admin_users, validate_user, create_exam_entry, create_connection, fetch_unique_sections, fetch_questions_by_section, fetch_first_question_id

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions')
def questions():
    return render_template('questions.html')

@app.route('/responses')
def responses():
    return render_template('responses.html')

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/start-exam')
def start_exam():
    return render_template('start_exam.html')

@app.route('/questions-data')
def questions_data():
    questions = fetch_questions()
    return jsonify(questions)

@app.route('/responses-data')
def responses_data():
    responses = fetch_responses()
    return jsonify(responses)

@app.route('/users-data')
def users_data():
    users = fetch_users()
    return jsonify(users)

@app.route('/non-admin-users-data')
def non_admin_users_data():
    users = fetch_non_admin_users()
    return jsonify(users)

@app.route('/unique-sections')
def unique_sections():
    sections = fetch_unique_sections()
    return jsonify(sections)

@app.route('/questions-by-section/<section>')
def questions_by_section(section):
    questions = fetch_questions_by_section(section)
    return jsonify(questions)

@app.route('/submit-response', methods=['POST'])
def submit_response():
    data = request.get_json()
    user_id = data['user_id']
    question_id = data['question_id']
    response = data['response']
    exam_id = data['exam_id']
    save_response(user_id, question_id, response, exam_id)  # Save the response to the database
    return jsonify({'message': 'Response recorded'})

@app.route('/add-question', methods=['POST'])
def add_question():
    question_type = request.form['question_type']
    question_text = request.form['question_text']
    answer = request.form['answer']
    score = request.form['score']
    section = request.form['section']
    
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO questions (type, text, answer, score, section) VALUES (%s, %s, %s, %s, %s)",
        (question_type, question_text, answer, score, section)
    )
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'Question added successfully'})

@app.route('/add-user', methods=['POST'])
def add_user():
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    teacher = request.form.get('teacher') == 'on'
    admin = request.form.get('admin') == 'on'
    password = request.form['password']
    
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (name, surname, email, teacher, admin, password) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, surname, email, teacher, admin, password)
    )
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'message': 'User added successfully'})

@app.route('/delete-question/<int:id>', methods=['DELETE'])
def delete_question_route(id):
    delete_question(id)
    return jsonify({'message': 'Question deleted successfully'})

@app.route('/delete-user/<int:id>', methods=['DELETE'])
def delete_user_route(id):
    delete_user(id)
    return jsonify({'message': 'User deleted successfully'})

@app.route('/start-exam', methods=['POST'])
def start_exam_post():
    user_id = request.form['user']
    password = request.form['password']
    
    user = validate_user(user_id, password)
    
    if user:
        # Create a new exam entry and return the exam ID
        question_id = fetch_first_question_id()
        answer = ""
        correct = False
        score = 0
        exam_id = create_exam_entry(user_id, question_id, answer, correct, score)
        return jsonify({'success': True, 'exam_id': exam_id})
    else:
        return jsonify({'success': False, 'message': 'Invalid user or password'})

@app.route('/exam/<int:exam_id>')
def exam(exam_id):
    section = request.args.get('section')
    user_id = request.args.get('user_id')  # Get user_id from query parameters
    return render_template('exam.html', exam_id=exam_id, section=section, user_id=user_id)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')