from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Login fields
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Role & Credits
    role = db.Column(db.String(20), default="client")
    credits = db.Column(db.Integer, default=0)

    # WhatsApp Settings
    whatsapp_token = db.Column(db.Text, nullable=True)
    whatsapp_phone_id = db.Column(db.String(100), nullable=True)

    # SMS Settings
    sms_api_url = db.Column(db.Text, nullable=True)
    sms_api_key = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------- PASSWORD FUNCTIONS ---------------- #

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"
