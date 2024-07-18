from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User
import re

app = Flask(__name__)
app.secret_key = 'mykey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def check_password_requirements(password):
    errors = []
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain a lowercase letter.")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain an uppercase letter.")
    if not re.search(r'[0-9]$', password):
        errors.append("Password must end in a number.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    return errors

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('signup'))

        errors = check_password_requirements(password)
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash("Email is already registered!")
            return redirect(url_for('signup'))

        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('thankyou'))
    return render_template('signup.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('secretPage'))
        else:
            flash("Invalid credentials!")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/secretPage')
def secretPage():
    if 'user_id' in session:
        return render_template('secretPage.html')
    else:
        flash("You must be logged in to access this page!")
        return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
