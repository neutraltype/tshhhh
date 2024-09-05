from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Определение моделей базы данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # teacher or student
    classroom_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    students = db.relationship('User', backref='classroom', lazy=True)

# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Регистрация учителя
@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_teacher = User(username=username, email=email, role='teacher')
        new_teacher.set_password(password)
        try:
            db.session.add(new_teacher)
            db.session.commit()
            flash('Реєстрація пройшла успішно!', 'success')
            return redirect(url_for('login'))
        except:
            flash('Помилка під час реєстрації. Спробуйте іншу електронну пошту.', 'error')
    return render_template('register_teacher.html')

# Регистрация студента
@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_student = User(username=username, email=email, role='student')
        new_student.set_password(password)
        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Реєстрація пройшла успішно!', 'success')
            return redirect(url_for('login'))
        except:
            flash('Помилка під час реєстрації. Спробуйте іншу електронну пошту.', 'error')
    return render_template('register_student.html')

# Логин
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неправильна електронна пошта або пароль', 'error')
    return render_template('login.html')

# Логаут
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('index'))

# Создание класса (только для учителей)
@app.route('/create_class', methods=['GET', 'POST'])
@login_required
def create_class():
    if current_user.role != 'teacher':
        flash('Тільки вчитель може створювати класи', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        class_name = request.form['class_name']
        new_class = Class(name=class_name, teacher_id=current_user.id)
        db.session.add(new_class)
        db.session.commit()
        flash('Клас успішно створено!', 'success')
        return redirect(url_for('index'))

    return render_template('create_class.html')

# Присоединение к классу (только для студентов)
@app.route('/join_class', methods=['GET', 'POST'])
@login_required
def join_class():
    if current_user.role != 'student':
        flash('Тільки студент може приєднуватися до класів', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        class_id = request.form['class_id']
        student = User.query.get(current_user.id)
        student.classroom_id = class_id
        db.session.commit()
        flash('Ви приєдналися до класу!', 'success')
        return redirect(url_for('index'))

    return render_template('join_class.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
