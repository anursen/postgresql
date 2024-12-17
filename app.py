from flask import Flask, render_template, jsonify, request
import random
import psycopg2
from .models import Question

app = Flask(__name__)

def create_connection():
    return psycopg2.connect(
        user="user",
        password="password",
        host="localhost",
        port="5432",
        database="mydatabase"
    )

@app.route('/')
def index():
    return render_template('index.html')

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
    # Here you would save the response to the database
    return jsonify({'message': 'Response recorded'})

if __name__ == "__main__":
    app.run(debug=True)
