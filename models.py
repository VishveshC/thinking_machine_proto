"""
Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pyotp

db = SQLAlchemy()

# ============================================================================
# User Model
# ============================================================================

class User(db.Model, UserMixin):
    """
    Enhanced user model with 2FA and dummy money balance.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # 2FA
    totp_secret = db.Column(db.String(32), nullable=True)  # Google Authenticator secret
    two_fa_enabled = db.Column(db.Boolean, default=False)
    
    # Dummy money balance
    balance = db.Column(db.Float, default=10000.00, nullable=False)
    
    # Face ID (dummy implementation - just stores a flag)
    face_id_enabled = db.Column(db.Boolean, default=False)
    face_id_data = db.Column(db.String(500), nullable=True)  # Placeholder
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    sent_transactions = db.relationship('Transaction', foreign_keys='Transaction.sender_id', backref='sender', lazy='dynamic')
    received_transactions = db.relationship('Transaction', foreign_keys='Transaction.receiver_id', backref='receiver', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password."""
        return check_password_hash(self.password_hash, password)
    
    def generate_totp_secret(self):
        """Generate a new TOTP secret for 2FA."""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self):
        """Get the provisioning URI for QR code generation."""
        if self.totp_secret:
            return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
                name=self.username,
                issuer_name='FraudGuard API'
            )
        return None
    
    def verify_totp(self, token):
        """Verify a TOTP token."""
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)
    
    def __repr__(self):
        return f'<User {self.username}>'


# ============================================================================
# Transaction Model
# ============================================================================

class Transaction(db.Model):
    """
    Money transfer transactions between users.
    """
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    # Transaction status
    status = db.Column(db.String(20), default='pending')  # pending, completed, flagged, cancelled
    
    # Fraud detection
    fraud_score = db.Column(db.Float, nullable=True)  # 0-1 score from AI
    fraud_reason = db.Column(db.Text, nullable=True)
    requires_review = db.Column(db.Boolean, default=False)
    
    # Face auth
    face_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Description
    description = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.amount} from {self.sender_id} to {self.receiver_id}>'


# ============================================================================
# Fraud Pattern Model
# ============================================================================

class FraudPattern(db.Model):
    """
    Known fraud patterns for detection.
    """
    __tablename__ = 'fraud_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(db.String(50), nullable=False)  # email, sms, phone
    pattern = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Source
    source = db.Column(db.String(50), default='manual')  # manual, gemini_api, ml_model
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FraudPattern {self.id}: {self.pattern_type}>'


# ============================================================================
# Simulation Log Model
# ============================================================================

class SimulationLog(db.Model):
    """
    Logs for simulation sessions with conversation data.
    """
    __tablename__ = 'simulation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Simulation details
    simulation_type = db.Column(db.String(50), nullable=False)  # email, sms, phone
    input_data = db.Column(db.Text, nullable=False)
    
    # Conversation log (JSON)
    conversation = db.Column(db.Text, nullable=True)  # Stored as JSON string
    
    # Results
    fraud_detected = db.Column(db.Boolean, default=False)
    fraud_score = db.Column(db.Float, nullable=True)
    fraud_details = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SimulationLog {self.id}: {self.simulation_type}>'


# ============================================================================
# Contact Message Model
# ============================================================================

class ContactMessage(db.Model):
    """
    Contact form submissions.
    """
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Status tracking
    status = db.Column(db.String(20), default='new')  # new, in_progress, resolved
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage {self.id}: {self.subject}>'


# ============================================================================
# API Token Model
# ============================================================================

class APIToken(db.Model):
    """
    API tokens for authentication.
    """
    __tablename__ = 'api_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=True)  # Optional token name
    
    # Token status
    is_active = db.Column(db.Boolean, default=True)
    
    # Usage tracking
    last_used = db.Column(db.DateTime, nullable=True)
    usage_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<APIToken {self.id}: {self.token[:8]}...>'
