"""
Forms for the application
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FloatField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, NumberRange
from models import User, db

# ============================================================================
# Authentication Forms
# ============================================================================

class RegistrationForm(FlaskForm):
    """Enhanced registration form."""
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required.'),
            Length(min=3, max=20, message='Username must be 3-20 characters.'),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores.'
            )
        ],
        render_kw={'placeholder': 'Choose a username', 'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email address.')
        ],
        render_kw={'placeholder': 'your.email@example.com', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=8, max=128, message='Password must be at least 8 characters.')
        ],
        render_kw={'placeholder': 'Minimum 8 characters', 'class': 'form-control'}
    )
    
    confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.')
        ],
        render_kw={'placeholder': 'Re-enter password', 'class': 'form-control'}
    )
    
    submit = SubmitField('Register', render_kw={'class': 'btn btn-primary'})

    def validate_username(self, username):
        normalized_username = username.data.lower()
        user = User.query.filter(db.func.lower(User.username) == normalized_username).first()
        if user:
            raise ValidationError('Username already taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use another or log in.')


class LoginForm(FlaskForm):
    """Login form with 2FA support."""
    username = StringField(
        'Username',
        validators=[DataRequired(message='Username is required.')],
        render_kw={'placeholder': 'Your username', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Password',
        validators=[DataRequired(message='Password is required.')],
        render_kw={'placeholder': 'Your password', 'class': 'form-control'}
    )
    
    totp_token = StringField(
        '2FA Code (if enabled)',
        validators=[Length(min=0, max=6)],
        render_kw={'placeholder': '6-digit code', 'class': 'form-control'}
    )
    
    submit = SubmitField('Login', render_kw={'class': 'btn btn-primary'})


class Enable2FAForm(FlaskForm):
    """Form to enable 2FA."""
    totp_token = StringField(
        'Verification Code',
        validators=[
            DataRequired(message='Please enter the 6-digit code.'),
            Length(min=6, max=6, message='Code must be 6 digits.')
        ],
        render_kw={'placeholder': '123456', 'class': 'form-control'}
    )
    
    submit = SubmitField('Enable 2FA', render_kw={'class': 'btn btn-success'})


# ============================================================================
# Transaction Forms
# ============================================================================

class TransactionForm(FlaskForm):
    """Form for sending money to another user."""
    recipient_username = StringField(
        'Recipient Username',
        validators=[DataRequired(message='Recipient username is required.')],
        render_kw={'placeholder': 'Username of recipient', 'class': 'form-control'}
    )
    
    amount = FloatField(
        'Amount',
        validators=[
            DataRequired(message='Amount is required.'),
            NumberRange(min=0.01, message='Amount must be greater than 0.')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    description = StringField(
        'Description (optional)',
        validators=[Length(max=200)],
        render_kw={'placeholder': 'Payment for...', 'class': 'form-control'}
    )
    
    face_verification = BooleanField(
        'I authorize this transaction with my face',
        validators=[DataRequired(message='Face verification is required for transactions.')],
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField('Send Money', render_kw={'class': 'btn btn-success'})


# ============================================================================
# Simulation Forms
# ============================================================================

class SimulationForm(FlaskForm):
    """Form for fraud detection simulation."""
    data_type = SelectField(
        'Data Type',
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS Message'),
            ('phone', 'Phone Number')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    input_data = TextAreaField(
        'Input Data',
        validators=[
            DataRequired(message='Please enter data to analyze.'),
            Length(min=5, max=2000)
        ],
        render_kw={
            'placeholder': 'Enter email content, SMS text, or phone number...',
            'class': 'form-control',
            'rows': 6
        }
    )
    
    sender_name = StringField(
        'Sender Name (for simulation)',
        validators=[DataRequired()],
        render_kw={'placeholder': 'John Doe', 'class': 'form-control'}
    )
    
    receiver_name = StringField(
        'Receiver Name (for simulation)',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Jane Smith', 'class': 'form-control'}
    )
    
    submit = SubmitField('Run Simulation', render_kw={'class': 'btn btn-primary'})


# ============================================================================
# Contact Form
# ============================================================================

class ContactForm(FlaskForm):
    """Contact form for support requests."""
    name = StringField(
        'Name',
        validators=[
            DataRequired(message='Name is required.'),
            Length(min=2, max=100)
        ],
        render_kw={'placeholder': 'Your name', 'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email.')
        ],
        render_kw={'placeholder': 'your.email@example.com', 'class': 'form-control'}
    )
    
    subject = StringField(
        'Subject',
        validators=[
            DataRequired(message='Subject is required.'),
            Length(min=5, max=200)
        ],
        render_kw={'placeholder': 'How can we help?', 'class': 'form-control'}
    )
    
    message = TextAreaField(
        'Message',
        validators=[
            DataRequired(message='Message is required.'),
            Length(min=10, max=2000)
        ],
        render_kw={
            'placeholder': 'Your message...',
            'class': 'form-control',
            'rows': 6
        }
    )
    
    submit = SubmitField('Send Message', render_kw={'class': 'btn btn-primary'})
