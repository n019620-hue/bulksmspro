import os
import csv
import requests
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

# ----------------------------
# Initialize Database
# ----------------------------
db.init_app(app)

# ----------------------------
# Login Manager
# ----------------------------
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------------------
# Helper Functions
# ----------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


def send_whatsapp_message(phone, message):
    if not current_user.whatsapp_token or not current_user.whatsapp_phone_id:
        return False

    url = f"https://graph.facebook.com/v17.0/{current_user.whatsapp_phone_id}/messages"

    headers = {
        "Authorization": f"Bearer {current_user.whatsapp_token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message}
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(response.text)
        return response.status_code == 200
    except Exception as e:
        print("WhatsApp Error:", e)
        return False


def send_sms_message(phone, message):
    if not current_user.sms_api_url:
        return False

    url = current_user.sms_api_url.format(to=phone, message=message)

    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        print("SMS Error:", e)
        return False


# ----------------------------
# Main Routes
# ----------------------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('client_dashboard'))
    return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.whatsapp_token = request.form.get('whatsapp_token')
        current_user.whatsapp_phone_id = request.form.get('whatsapp_phone_id')
        current_user.sms_api_url = request.form.get('sms_api_url')
        db.session.commit()
        flash("Settings updated successfully!", "success")
        return redirect(url_for('settings'))

    return render_template('settings.html')


# ----------------------------
# Authentication
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))

        flash("Invalid username or password", "danger")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ----------------------------
# Admin Routes
# ----------------------------
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    users = User.query.filter(User.role != 'admin').all()
    return render_template('admin/dashboard.html', users=users)


@app.route('/admin/create_user', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    username = request.form.get('username')
    password = request.form.get('password')
    credits = int(request.form.get('credits', 0))

    if User.query.filter_by(username=username).first():
        flash("Username already exists", "danger")
    else:
        new_user = User(username=username, role='client', credits=credits)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("User created successfully", "success")

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/add_credits', methods=['POST'])
@login_required
def add_credits():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    user_id = request.form.get('user_id')
    amount = int(request.form.get('amount'))

    user = User.query.get(user_id)
    if user:
        user.credits += amount
        db.session.commit()
        flash(f"{amount} credits added to {user.username}", "success")

    return redirect(url_for('admin_dashboard'))


# ----------------------------
# Client Routes
# ----------------------------
@app.route('/client/dashboard')
@login_required
def client_dashboard():
    if current_user.role != 'client':
        return redirect(url_for('index'))

    return render_template('client/dashboard.html')


@app.route('/client/send_bulk', methods=['POST'])
@login_required
def send_bulk():
    if current_user.role != 'client':
        return redirect(url_for('index'))

    msg_type = request.form.get('msg_type')
    message = request.form.get('message')
    file = request.files.get('file')

    if not file or not allowed_file(file.filename):
        flash("Please upload a valid CSV file", "danger")
        return redirect(url_for('client_dashboard'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    numbers = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                numbers.append(row[0].strip())

    total = len(numbers)

    if current_user.credits < total:
        flash(f"Insufficient credits. Required: {total}, Available: {current_user.credits}", "danger")
        return redirect(url_for('client_dashboard'))

    success = 0
    failed = 0

    for number in numbers:
        if msg_type == 'whatsapp':
            status = send_whatsapp_message(number, message)
        else:
            status = send_sms_message(number, message)

        if status:
            success += 1
            current_user.credits -= 1
        else:
            failed += 1

    db.session.commit()

    flash(f"Total: {total} | Success: {success} | Failed: {failed}", "info")

    return redirect(url_for('client_dashboard'))


# ----------------------------
# Database Initialization
# ----------------------------
def init_db():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin', credits=999999)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin created: admin / admin123")


# ----------------------------
# Run App
# ----------------------------
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
