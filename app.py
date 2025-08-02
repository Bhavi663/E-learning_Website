from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import json
import os
import bcrypt
import re
import uuid
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='templates')  # Explicitly set template folder
app.secret_key = os.getenv('SECRET_KEY', 'your_secure_secret_key')  # Load from .env or use default

# Configure Flask-Mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('EMAIL_USER'),  # Your email address from .env
    MAIL_PASSWORD=os.getenv('EMAIL_PASS'),  # Your email app-specific password from .env
    MAIL_DEFAULT_SENDER=os.getenv('EMAIL_USER')
)
mail = Mail(app)

# Load or initialize users.json in JSONL format
USERS_FILE = 'users.json'
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        f.write('[]\n')  # Initialize as empty array

def load_users():
    users = []
    try:
        with open(USERS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        user = json.loads(line)
                        if isinstance(user, dict) and 'email' in user:
                            users.append(user)
                        else:
                            logger.warning(f"Invalid user data in line: {line}")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error for line: {line}, error: {e}")
    except Exception as e:
        logger.error(f"Error reading users.json: {e}")
    logger.debug(f"Loaded users: {users}")
    return users

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        for user in users:
            f.write(json.dumps(user) + '\n')

# Password validation function
def is_valid_password(password):
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in '@$!%*?&' for c in password):
        return False
    return True

@app.route('/')
def home():
    print(f"Rendering index.html from: {app.template_folder}")  # Debug print
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        users = load_users()
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm-password')

        if any(user['email'] == email for user in users):
            return jsonify({'error': 'Email already registered'}), 400
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        if not is_valid_password(password):
            return jsonify({'error': 'Password must be at least 8 characters with one uppercase, one lowercase, one number, and one special character (@$!%*?&)'}), 400

        # Hash the password and initialize premium status
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.append({
            'email': email,
            'full_name': data.get('full-name'),
            'password': hashed_password.decode('utf-8'),
            'premium': False,
            'reset_token': None,
            'reset_token_expiry': None
        })
        save_users(users)
        return redirect(url_for('login'))
    print(f"Rendering signup.html from: {app.template_folder}")  # Debug print
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        users = load_users()
        email = data.get('email')
        password = data.get('password')
        user = next((u for u in users if u.get('email') == email), None)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['email'] = email
            return redirect(url_for('course'))
        return jsonify({'error': 'Invalid email or password'}), 401
    print(f"Rendering login.html from: {app.template_folder}")  # Debug print
    return render_template('login.html')

@app.route('/course')
def course():
    if 'email' not in session:
        return redirect(url_for('login'))
    users = load_users()
    email = session['email']
    premium = next((u['premium'] for u in users if u.get('email') == email), False)
    print(f"Rendering course.html from: {app.template_folder}")  # Debug print
    return render_template('course.html', premium=premium)

@app.route('/about')
def about():
    print(f"Rendering about.html from: {app.template_folder}")  # Debug print
    return render_template('about.html')

@app.route('/contact')
def contact():
    print(f"Rendering contact.html from: {app.template_folder}")  # Debug print
    return render_template('contact.html')

@app.route('/gkquiz', methods=['GET', 'POST'])
def gkquiz():
    if request.method == 'POST':
        username = request.form.get('username')
        score = request.form.get('score', 0)
        if username:
            print(f"Score saved: {username} - {score}")
            return jsonify({'message': 'Score saved successfully'}), 200
        return jsonify({'error': 'Username is required'}), 400
    print(f"Rendering gkquiz.html from: {app.template_folder}")  # Debug print
    return render_template('gkquiz.html')

@app.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        users = load_users()
        logger.debug(f"Checking email: {email}, Users: {users}")
        user = next((u for u in users if u.get('email') == email), None)
        if not user:
            return jsonify({'error': 'Email not found'}), 404

        # Generate a unique reset token
        reset_token = str(uuid.uuid4())
        reset_token_expiry = (datetime.now() + timedelta(hours=1)).isoformat()

        # Update the user's reset token and expiry
        user['reset_token'] = reset_token
        user['reset_token_expiry'] = reset_token_expiry
        save_users(users)

        # Create the reset link
        reset_link = url_for('reset_password', token=reset_token, _external=True)

        # Send the reset email
        try:
            msg = Message(
                subject='Password Reset Request - Smart Scholars',
                recipients=[email],
                html=f"""
                    <h2>Password Reset Request</h2>
                    <p>You requested a password reset for your Smart Scholars account.</p>
                    <p>Click the link below to reset your password:</p>
                    <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 5px;">Reset Password</a>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you did not request a password reset, please ignore this email.</p>
                """
            )
            mail.send(msg)
            return jsonify({'message': 'Password reset link sent to your email. Please check your inbox.'}), 200
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return jsonify({'error': 'Failed to send reset link. Please try again later.'}), 500

    print(f"Rendering resetpassword.html from: {app.template_folder}")  # Debug print
    return render_template('resetpassword.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    users = load_users()
    user = next((u for u in users if u.get('reset_token') == token and u.get('reset_token_expiry')), None)
    if not user or datetime.fromisoformat(user['reset_token_expiry']) < datetime.now():
        return render_template('reset.html', error='Invalid or expired reset link'), 400

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if password != confirm_password:
            return render_template('reset.html', error='Passwords do not match', token=token), 400
        if not is_valid_password(password):
            return render_template('reset.html', error='Password must be at least 8 characters with one uppercase, one lowercase, one number, and one special character (@$!%*?&)', token=token), 400

        # Update the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user['password'] = hashed_password.decode('utf-8')
        user.pop('reset_token', None)
        user.pop('reset_token_expiry', None)
        save_users(users)
        return redirect(url_for('login'))

    return render_template('reset.html', token=token)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'email' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        gender = data.get('gender')
        email = data.get('email')
        pincode = data.get('pincode')
        card_type = data.get('card-type')
        card_number = data.get('card-number')
        expiry_date = data.get('expiry-date')
        cvv = data.get('cvv')

        if not all([name, gender, email, pincode, card_type, card_number, expiry_date, cvv]):
            return jsonify({'error': 'All required fields must be filled'}), 400
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
            return jsonify({'error': 'Invalid email format'}), 400
        if not re.match(r"^\d{6}$", pincode):
            return jsonify({'error': 'Pincode must be 6 digits'}), 400
        if not re.match(r"^\d{16}$", card_number):
            return jsonify({'error': 'Card number must be 16 digits'}), 400
        if not re.match(r"^(0[1-9]|1[0-2])\/[0-9]{2}$", expiry_date):
            return jsonify({'error': 'Expiry date must be in MM/YY format'}), 400
        if not re.match(r"^\d{3}$", cvv):
            return jsonify({'error': 'CVV must be 3 digits'}), 400

        users = load_users()
        user = next((u for u in users if u.get('email') == session['email']), None)
        if user:
            user['premium'] = True
            save_users(users)
            print(f"Payment processed for {name}: Card {card_type} ending in {card_number[-4:]}")
            return redirect(url_for('course'))
        return jsonify({'error': 'User not found'}), 404

    print(f"Rendering payment.html from: {app.template_folder}")  # Debug print
    return render_template('payment.html', success=False)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/faqs')
def faqs():
    print(f"Rendering faqs.html from: {app.template_folder}")  # Debug print
    return render_template('faqs.html')

@app.route('/terms')
def terms():
    print(f"Rendering termsofuse.html from: {app.template_folder}")  # Debug print
    return render_template('termsofuse.html')

@app.route('/privacy')
def privacy():
    print(f"Rendering privacypolicy.html from: {app.template_folder}")  # Debug print
    return render_template('privacypolicy.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)