import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pr-tech-connect-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    
    # WhatsApp Cloud API Config
    WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN') or 'YOUR_WHATSAPP_TOKEN'
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID') or 'YOUR_PHONE_NUMBER_ID'
    
    # SMS API Config
    SMS_API_URL = os.environ.get('SMS_API_URL') or 'https://api.smsprovider.com/send?api_key=YOUR_KEY&to={to}&message={message}'
