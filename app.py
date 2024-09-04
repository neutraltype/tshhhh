from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

app = Flask(__name__)

# Настройка приложения
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Определение моделей базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # teacher or student
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)  # добавлено

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    students = db.relationship('User', backref='classroom', lazy=True)

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        new_teacher = User(username=username, email=email, role='teacher')
        db.session.add(new_teacher)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register_teacher.html')

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_student = User(username=username, email=email, role='student')
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register_student.html')

@app.route('/create_class', methods=['GET', 'POST'])
def create_class():
    if request.method == 'POST':
        class_name = request.form['class_name']
        teacher_id = request.form['teacher_id']
        new_class = Class(name=class_name, teacher_id=teacher_id)
        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_class.html')

@app.route('/join_class', methods=['GET', 'POST'])
def join_class():
    if request.method == 'POST':
        student_email = request.form['student_email']
        class_id = request.form['class_id']
        student = User.query.filter_by(email=student_email).first()
        if student:
            student.class_id = class_id
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return "Студент не найден", 404
    return render_template('join_class.html')

if __name__ == "__main__":
    app.run()
