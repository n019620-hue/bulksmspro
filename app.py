import os
import csv
import time
import requests
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# ---------------- LOGIN MANAGER ---------------- #
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- HOME ---------------- #
@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------------- LOGIN ---------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------- DASHBOARD ---------------- #
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("client/dashboard.html")

# ---------------- SEND TEXT FUNCTION ---------------- #
def send_whatsapp_text(phone, message):

    if not current_user.whatsapp_token or not current_user.whatsapp_phone_id:
        return {"error": "Token or Phone ID missing"}

    url = f"https://graph.facebook.com/v17.0/{current_user.whatsapp_phone_id}/messages"

    headers = {
        "Authorization": f"Bearer {current_user.whatsapp_token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

# ---------------- SEND MEDIA FUNCTION ---------------- #
def send_whatsapp_media(phone, media_url):

    url = f"https://graph.facebook.com/v17.0/{current_user.whatsapp_phone_id}/messages"

    headers = {
        "Authorization": f"Bearer {current_user.whatsapp_token}",
        "Content-Type": "application/json"
    }

    if media_url.lower().endswith(".pdf"):
        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "document",
            "document": {
                "link": media_url,
                "filename": "document.pdf"
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "image",
            "image": {
                "link": media_url
            }
        }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

# ---------------- BULK TEXT ROUTE ---------------- #
@app.route("/send-bulk-text", methods=["POST"])
@login_required
def send_bulk_text():

    csv_file = request.files.get("csv_file")
    message = request.form.get("message")

    if not csv_file or not message:
        flash("Upload CSV and enter message", "danger")
        return redirect(url_for("dashboard"))

    numbers = []
    csv_reader = csv.reader(csv_file.stream.read().decode("utf-8").splitlines())

    for row in csv_reader:
        if row:
            numbers.append(row[0].strip())

    for number in numbers:
        send_whatsapp_text(number, message)
        time.sleep(1)

    flash("Bulk Text Sent Successfully!", "success")
    return redirect(url_for("dashboard"))

# ---------------- BULK MEDIA ROUTE ---------------- #
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/send-bulk-media", methods=["POST"])
@login_required
def send_bulk_media():

    csv_file = request.files.get("csv_file")
    media_file = request.files.get("media_file")

    if not csv_file or not media_file:
        flash("Upload CSV and Media file", "danger")
        return redirect(url_for("dashboard"))

    filename = secure_filename(media_file.filename)
    media_path = os.path.join(UPLOAD_FOLDER, filename)
    media_file.save(media_path)

    media_url = request.host_url + media_path

    numbers = []
    csv_reader = csv.reader(csv_file.stream.read().decode("utf-8").splitlines())

    for row in csv_reader:
        if row:
            numbers.append(row[0].strip())

    for number in numbers:
        send_whatsapp_media(number, media_url)
        time.sleep(1)

    flash("Bulk Media Sent Successfully!", "success")
    return redirect(url_for("dashboard"))

# ---------------- RUN ---------------- #
