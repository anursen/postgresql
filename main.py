from flask import Flask, render_template, jsonify, request, url_for
from crud import QuestionCRUD, UserCRUD, ExamCRUD, AdminSettingsCRUD, ResponseCRUD  
from database import fetch_responses, fetch_unique_sections, fetch_first_question_id
from models import User, Question, Exams, ExamConfig, AdminSettings, Responses
from datetime import datetime, timedelta

app = Flask(__name__, static_url_path='/static')

@app.route('/admin-settings', methods=['GET', 'POST'])
def admin_settings_route():
    if request.method == 'POST':
        data = request.get_json()
        AdminSettingsCRUD.update_admin_settings(data)
        return jsonify({'message': 'Settings updated successfully'})
    else:
        settings = AdminSettingsCRUD.get_admin_settings()
        return jsonify(settings)

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions', methods=['GET'])
def get_questions():
    return render_template('questions.html')

@app.route('/questions-data', methods=['GET'])
def get_questions_data():
    questions = QuestionCRUD.fetch_questions()
    return jsonify(questions)

@app.route('/questions', methods=['POST'])
def add_question():
    try:
        data = request.get_json()
        print("Received data:", data)
        question_type = data['question_type']
        question_text = data['question_text']
        answer = data['answer']
        score = data['score']
        section = data['section']
        
        question = Question(
            type=question_type,
            text=question_text,
            answer=answer,
            score=score,
            section=section
        )
        
        QuestionCRUD.create_question(question)
        
        return jsonify({'message': 'Question added successfully'})
    except Exception as e:
        print(f"Error adding question: {str(e)}")
        return jsonify({'message': f'Error adding question: {str(e)}'}), 500

@app.route('/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
    try:
        print(f"Received request to delete question with id: {id}")
        QuestionCRUD.delete_question(id)
        return jsonify({'message': 'Question deleted successfully'})
    except Exception as e:
        print(f"Error deleting question: {str(e)}")
        return jsonify({'message': f'Error deleting question: {str(e)}'}), 500

@app.route('/questions-by-section/<section>', methods=['GET'])
def get_questions_by_section(section):
    questions = QuestionCRUD.fetch_questions_by_section(section)
    return jsonify(questions)

@app.route('/responses', methods=['GET'])
def get_responses():
    responses = fetch_responses()
    return jsonify(responses)

@app.route('/users', methods=['GET'])
def get_users():
    return render_template('users.html')

@app.route('/users-data', methods=['GET'])
def get_users_data():
    users = UserCRUD.fetch_users()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    teacher = request.form.get('teacher') == 'on'
    admin = request.form.get('admin') == 'on'
    password = request.form['password']
    
    user = User(
        name=name,
        surname=surname,
        email=email,
        teacher=teacher,
        admin=admin,
        password=password
    )
    
    UserCRUD.create_user(user)
    
    return jsonify({'message': 'User added successfully'})

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    UserCRUD.delete_user(id)
    return jsonify({'message': 'User deleted successfully'})

@app.route('/non-admin-users', methods=['GET'])
def get_non_admin_users():
    users = UserCRUD.fetch_non_admin_users()
    return jsonify(users)

@app.route('/non-admin-users-data', methods=['GET'])
def get_non_admin_users_data():
    users = UserCRUD.fetch_non_admin_users()
    return jsonify(users)

@app.route('/unique-sections', methods=['GET'])
def get_unique_sections():
    sections = fetch_unique_sections()
    return jsonify(sections)

@app.route('/submit-response', methods=['POST'])
def submit_response():
    try:
        data = request.get_json()
        response = Responses(
            exam_id=data['exam_id'],
            user_id=data['user_id'],
            question_id=data['question_id'],
            answer=data['answer'],
            submit_time=datetime.now()
        )
        ResponseCRUD.create_response(response)
        return '', 204  # No content response
    except Exception as e:
        print(f"Error submitting response: {str(e)}")
        return jsonify({'message': f'Error submitting response: {str(e)}'}), 500

@app.route('/start-exam', methods=['POST'])
def start_exam():
    try:
        user_id = request.form['user']
        password = request.form['password']
        section = request.form['section']
        
        user = UserCRUD.validate_user(user_id, password)
        
        if user:
            settings = AdminSettingsCRUD.get_admin_settings()
            if not settings:
                return jsonify({'success': False, 'message': 'Exam settings not configured'})

            # Ensure boolean values are properly converted
            config = ExamConfig(
                question_time=int(settings['question_time']),
                question_count=int(settings['question_count']),
                exam_duration=int(settings['exam_duration']),
                passing_score=int(settings['passing_score']),
                shuffle_questions=bool(settings['shuffle_questions'])
            )
             

            # Get first question from the selected section
            question_id = fetch_first_question_id(section)
            if not question_id:
                return jsonify({'success': False, 'message': 'No questions available for this section'})

            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=settings['exam_duration'])
            
            exam = Exams(
                user_id=int(user_id),
                start_time=start_time,
                end_time=end_time,
                config=config
            )
            
            exam_id = ExamCRUD.create_exam(exam)
            
            return jsonify({
                'success': True, 
                'exam_id': exam_id,
                'config': config.dict()
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid user or password'})
    except Exception as e:
        print(f"Error in start_exam: {str(e)}")  # Add logging
        return jsonify({'success': False, 'message': f'Error starting exam: {str(e)}'})

@app.route('/start-exam', methods=['GET'])
def show_start_exam():
    return render_template('start_exam.html')

@app.route('/exam/<int:exam_id>', methods=['GET'])
def get_exam(exam_id):
    section = request.args.get('section')
    user_id = request.args.get('user_id')  # Get user_id from query parameters
    return render_template('exam.html', exam_id=exam_id, section=section, user_id=user_id)

@app.route('/evaluate-exam/<int:exam_id>', methods=['POST'])
def evaluate_exam(exam_id):
    try:
        responses = ResponseCRUD.fetch_responses_by_exam(exam_id)
        total_score = 0
        for response in responses:
            correct = ExamCRUD.check_response_correctness(response['question_id'], response['answer'])
            score = ExamCRUD.calculate_score(response['question_id'], correct)
            response['result'] = correct
            response['score'] = score
            total_score += score
            ResponseCRUD.update_response(response)
        
        ExamCRUD.update_exam_score(exam_id, total_score)
        return jsonify({'message': 'Exam evaluated successfully'})
    except Exception as e:
        print(f"Error evaluating exam: {str(e)}")
        return jsonify({'message': f'Error evaluating exam: {str(e)}'}), 500

@app.route('/results/<int:exam_id>', methods=['GET'])
def show_results(exam_id):
    responses = ResponseCRUD.fetch_responses_by_exam(exam_id)
    return render_template('results.html', responses=responses)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')