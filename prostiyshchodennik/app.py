from flask import Flask, render_template, request, redirect, url_for  # Импортируйте render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модели
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    classes = db.relationship('Class', backref='teacher', lazy=True)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    students = db.relationship('Student', backref='class_', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

# Создание таблиц перед первым запросом
@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        new_teacher = Teacher(email=email, password=password)
        db.session.add(new_teacher)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register_teacher.html')

@app.route('/create_class', methods=['GET', 'POST'])
def create_class():
    if request.method == 'POST':
        class_name = request.form['class_name']
        teacher_id = 1  # Установите ID учителя для тестирования
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
        student = Student(email=student_email, class_id=class_id)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('join_class.html')

if __name__ == '__main__':
    app.run(debug=True)
