"""
Application Configuration
"""
import os

class Config:
    """Base configuration"""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-me-to-a-secret-in-prod'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = 3600  # 1 hour
    
    # Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'AIzaSyD1Pyd1JoI31_05OTA87o_B1-SktU2gcMU'
    
    # YouTube Data API (for video recommendations)
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY') or 'your-youtube-api-key-here'
    
    # Transaction Settings
    INITIAL_BALANCE = 10000.00  # Starting dummy money for new users
    LARGE_TRANSACTION_THRESHOLD = 0.3  # 30% of balance triggers additional checks
    
    # Email Settings (for contact form)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL') or 'support@frauddetection.com'
