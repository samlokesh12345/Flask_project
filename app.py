from flask import Flask, render_template, request, url_for, flash, redirect, session
import sqlite3
from flask_session import Session
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'sam'  
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ADMIN_CREDENTIALS = {
    'Admin': 'admin123',
    'sam': '123'
}


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   mail TEXT NOT NULL,
                   date TEXT NOT NULL
                   )''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['mail']
        date_str = request.form['date'] 

        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash("Error: Invalid date format. Please use YYYY-MM-DD.")
            return redirect(url_for('index'))

        current_date = datetime.now()

        if appointment_date < current_date:
            flash("Error: The appointment date cannot be in the past.")
            return redirect(url_for('index'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (name, mail, date) VALUES (?, ?, ?)',
            (name, email, date_str)
        )
        flash(" Booked successfully!")
        conn.commit()
        conn.close()
        return redirect(url_for('register'))  

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('Successfully logged in!')
            return redirect(url_for('result')) 
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    session.pop('username',None)
    flash('you have been logged out.')
    return redirect(url_for('login'))

@app.route('/result')
def result():
    if not session.get('logged_in'):
        flash('you need to log in to access this page')
        return redirect(url_for('login'))
    username=session.get('username')
    conn=sqlite3.connect('database.db')
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM users')
    data=cursor.fetchall()
    conn.close()

    return render_template("result.html",username=username,data=data)

    return render_template('result.html')



@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    init_db() 
    app.run(debug=True)