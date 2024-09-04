from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Определение моделей базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # teacher or student

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    students = db.relationship('User', backref='classroom', lazy=True)

# Маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('index'))
        else:
            return 'Неверная электронная почта или пароль'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_teacher = User(username=username, email=email, role='teacher')
        new_teacher.set_password(password)
        db.session.add(new_teacher)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register_teacher.html')

@app.route('/create_class', methods=['GET', 'POST'])
def create_class():
    if 'role' in session and session['role'] == 'teacher':
        if request.method == 'POST':
            class_name = request.form['class_name']
            teacher_id = session['user_id']
            new_class = Class(name=class_name, teacher_id=teacher_id)
            db.session.add(new_class)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('create_class.html')
    else:
        return 'Доступ запрещен'

@app.route('/join_class', methods=['GET', 'POST'])
def join_class():
    if 'role' in session and session['role'] == 'student':
        if request.method == 'POST':
            student_id = session['user_id']
            class_id = request.form['class_id']
            student = User.query.get(student_id)
            student.class_id = class_id
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('join_class.html')
    else:
        return 'Доступ запрещен'

if __name__ == "__main__":
    app.run()
