from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

    # Database configuration

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'reflexion_journal')
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail configuration

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your_email@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your_password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', 'your_email@example.com')

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
    UPLOAD_URL = '/static/uploads/'

    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')