from chatbot import chatbot
from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from flask_recaptcha import ReCaptcha
import mysql.connector
import os
import secrets

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = secrets.token_hex(16)  # Secure random key

# Google reCAPTCHA Configuration
app.config.update({
    "RECAPTCHA_ENABLED": True,
    "RECAPTCHA_SITE_KEY": "your_site_key",   # Replace with your actual site key
    "RECAPTCHA_SECRET_KEY": "your_secret_key"  # Replace with your actual secret key
})

recaptcha = ReCaptcha(app)

# Database Connectivity with Error Handling
try:
    conn = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="Shiv@123",  # Replace with your actual password
        database="register"
    )
    cur = conn.cursor()
except mysql.connector.Error as err:
    print(f"Database Connection Error: {err}")
    exit(1)

# ---------------------------- Routes ----------------------------

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/index')
def home():
    if 'id' in session:
        return render_template('index.html')
    else:
        flash("Please log in first!", "warning")
        return redirect('/')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot.html')

# -------------------- User Authentication --------------------

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cur.execute("SELECT id FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()

    if user:
        session['id'] = user[0]
        flash('You were successfully logged in!', 'success')
        return redirect('/index')
    else:
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect('/')

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    try:
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        flash('Account created successfully! You can log in now.', 'success')
    except mysql.connector.Error as err:
        flash(f"Registration failed: {err}", 'danger')

    return redirect('/register')

@app.route('/logout')
def logout():
    session.pop('id', None)
    flash('You have been logged out.', 'info')
    return redirect('/')

# -------------------- Suggestions --------------------

@app.route('/suggestion', methods=['POST'])
def suggestion():
    email = request.form.get('uemail')
    message = request.form.get('message')

    try:
        cur.execute("INSERT INTO suggestion (email, message) VALUES (%s, %s)", (email, message))
        conn.commit()
        flash('Your suggestion has been successfully sent!', 'success')
    except mysql.connector.Error as err:
        flash(f"Error submitting suggestion: {err}", 'danger')

    return redirect('/index')

# -------------------- Chatbot --------------------

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(chatbot.get_response(userText))

# -------------------- Main --------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
