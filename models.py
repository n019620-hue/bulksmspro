from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # WhatsApp Settings
    whatsapp_token = db.Column(db.Text, nullable=True)
    whatsapp_phone_id = db.Column(db.String(200), nullable=True)

    # 💰 CREDIT SYSTEM
    credits = db.Column(db.Integer, default=0)

    # Password Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
