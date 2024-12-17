import psycopg2
from flask import Flask, render_template, jsonify, request
import random
from models import Question  # Change to absolute import
from crud import save_response, create_connection  # Import the new function

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

@app.route('/questions-data')
def questions_data():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, text FROM questions")
    questions = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify([{'id': q[0], 'text': q[1]} for q in questions])

@app.route('/responses-data')
def responses_data():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT question_id, response FROM responses")
    responses = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify([{'question_id': r[0], 'response': r[1]} for r in responses])

@app.route('/random-question')
def random_question():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, text FROM questions ORDER BY RANDOM() LIMIT 1")
    question = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify({'id': question[0], 'text': question[1]})

@app.route('/submit-response', methods=['POST'])
def submit_response():
    question_id = request.form['question_id']
    response = request.form['response']
    save_response(question_id, response)  # Save the response to the database
    return jsonify({'message': 'Response recorded'})

if __name__ == "__main__":
    app.run(debug=True)
