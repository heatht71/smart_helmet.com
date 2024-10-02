from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from itsdangerous import URLSafeTimedSerializer
import re
from MySQLdb import IntegrityError
from config import Config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Set the secret key for session management
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Load MySQL configuration from Config class
app.config['MYSQL_HOST'] = Config.config['host']
app.config['MYSQL_USER'] = Config.config['user']
app.config['MYSQL_PASSWORD'] = Config.config['password']
app.config['MYSQL_DB'] = Config.config['database']

# Initialize MySQL and Bcrypt
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Serializer for generating token
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Function to send password reset email
def send_password_reset_email(email, token):
    reset_url = url_for('reset_password', token=token, _external=True)

    # Set up the email parameters
    from_email = 'smart.helmet90@gmail.com'  # Replace with your email
    password = 'jcuk rybc ywlh carh'        # Replace with your email password it used be user input 
    to_email = email

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Password Reset Request'

    body = f"Click this link to reset your password: {reset_url}. This link will expire in 30 minutes."
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Replace with your SMTP server and port
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Route to handle forgot password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Fetch user data from the database
        cursor = mysql.connection.cursor()
        result = cursor.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cursor.fetchone()
            username = data[1]
            user_id = data[0]

            # Generate a password reset token
            token = serializer.dumps(user_id, salt='password-reset-salt')

            # Send a password reset email with the token included in the URL
            send_password_reset_email(email, token)

            flash('Password reset email sent. Check your inbox.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email not found', 'danger')

        cursor.close()

    return render_template('forgot_password.html')

# Route to handle password reset

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Validate the token (expires in 30 minutes)
        user_id = serializer.loads(token, salt='password-reset-salt', max_age=1800)
    except Exception:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        # Update the user's password in the database using email
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
        mysql.connection.commit()
        cursor.close()

        flash('Your password has been updated. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


# Route to render dashboard
@app.route('/dashboard.html')
def dashboard():
    if 'logged_in' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

# Route for login
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        # Fetch user data from database
        cursor = mysql.connection.cursor()
        result = cursor.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cursor.fetchone()
            password = data[4]

            # Check hashed password
            if bcrypt.check_password_hash(password, password_candidate):
                session['logged_in'] = True
                session['username'] = data[1]

                flash(f'Successfully logged in! Welcome {session["username"]}', 'success')
                return redirect(url_for('home'))  # Redirect to home page after login
            else:
                flash('Invalid login credentials', 'danger')
        else:
            flash('Email not found', 'danger')

        cursor.close()

    return render_template('login.html')

# Route for signup
@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Validate input
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            flash('Username must contain only letters and numbers', 'danger')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (username, email, phone, password) VALUES (%s, %s, %s, %s)",
                           (username, email, phone, hashed_password))
            mysql.connection.commit()
            cursor.close()

            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                flash('Email already registered. Please try logging in.', 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')

# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Route for home
@app.route('/')
def home():
    return render_template('home.html')

# Route for features
@app.route('/features.html')
def features():
    return render_template('features.html')

if __name__ == '__main__':
    app.run(debug=True)

