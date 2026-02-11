# FraudGuard - AI-Powered Fraud Detection System
https://proto.vishvesh.dns.army/

A comprehensive fraud detection platform with user authentication, transaction monitoring, and AI-powered analysis using Google's Gemini API.

## ✨ Features

### 🔐 Security & Authentication
- **Two-Factor Authentication (2FA)**: Google Authenticator integration
- **Face Recognition**: Biometric verification for transactions (demo implementation)
- **Password Hashing**: Werkzeug secure password storage
- **API Token Authentication**: Secure RESTful API access
- **Username Normalization**: Case-insensitive usernames

### 💰 Transaction System
- **Dummy Money Balance**: Each user starts with ₹10,000
- **Peer-to-Peer Transfers**: Send money between users
- **AI Fraud Detection**: Automatic analysis of large transactions
- **Transaction Holds**: Suspicious transactions flagged for review
- **Face Verification**: Required for transaction authorization
- **Real-time Balance Updates**: Instant balance adjustments

### 🤖 AI-Powered Fraud Detection
- **Multiple Data Types**:
  - Email (phishing detection)
  - SMS (smishing identification)
  - Phone numbers (scam caller detection)
  - Transactions (payment fraud analysis)
- **Gemini AI Integration**: Powered by Google's generative AI
- **Fraud Score Calculation**: 0-1 confidence scoring
- **Pattern Recognition**: Continuously updated fraud database
- **Conversation Simulation**: Demo fraud scenarios with chat logs

### 📊 Dashboard & Analytics
- **Balance Overview**: Current dummy money balance
- **Transaction History**: Recent sent/received payments
- **Flagged Activities**: Review suspicious transactions
- **Financial Insights**: AI-generated spending analysis
- **Quick Actions**: Easy access to key features

### 📖 Documentation Pages
1. **API Documentation**: Complete endpoint reference
2. **User Guide**: Step-by-step integration instructions
3. **FAQ**: Common questions and answers
4. **Simulations**: Interactive fraud detection testing
5. **Contact Us**: Support request form

### 🎨 Design
- **Responsive Layout**: Bootstrap 5 mobile-first design
- **Minimalistic UI**: Clean, user-friendly interface
- **Consistent Styling**: Unified header/footer across pages
- **Interactive Components**: Modals, accordions, dynamic forms

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation (Windows PowerShell)

```powershell
# Clone or navigate to project directory
cd "c:\Users\vishvesh\Downloads\Vishvesh\AADAPT (NMIMS)"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Set environment variable for Gemini API (optional)
$env:GEMINI_API_KEY="your-api-key-here"

# Run the application
python app.py
```

### First Run Setup

1. **Database Initialization**: Automatically creates SQLite database on first run
2. **Navigate to**: http://127.0.0.1:5000
3. **Register an Account**: Create your first user
4. **Enable 2FA** (optional): Set up Google Authenticator
5. **Start Using**: Access dashboard and try features

## 📁 Project Structure

```
├── app.py                  # Main application with routes
├── config.py               # Configuration settings
├── models.py               # Database models (User, Transaction, etc.)
├── forms.py                # WTForms form definitions
├── fraud_service.py        # Gemini AI fraud detection service
├── requirements.txt        # Python dependencies
├── templates/              # Jinja2 HTML templates
│   ├── base.html          # Base layout with header/footer
│   ├── index.html         # Homepage
│   ├── register.html      # Registration form
│   ├── login.html         # Login form (with 2FA)
│   ├── setup_2fa.html     # 2FA setup with QR code
│   ├── new_dashboard.html # User dashboard
│   ├── api_docs.html      # API documentation
│   ├── user_guide.html    # Integration guide
│   ├── faq.html           # FAQ page
│   ├── simulations.html   # Fraud detection simulator
│   └── contact.html       # Contact form
└── static/
    └── styles.css         # Custom CSS styling
```

## 🔑 Configuration

Edit `config.py` or set environment variables:

```python
# Security
SECRET_KEY = 'your-secret-key-here'

# Gemini API
GEMINI_API_KEY = 'your-gemini-api-key'

# Transaction Settings
INITIAL_BALANCE = 10000.00  # Starting balance
LARGE_TRANSACTION_THRESHOLD = 0.3  # 30% triggers fraud check
```

## 📝 Database Models

### User
- Username (unique, normalized)
- Email (unique)
- Password (hashed)
- 2FA secret (TOTP)
- Balance (dummy money)
- Face ID flag

### Transaction
- Sender/Receiver
- Amount
- Status (pending/completed/flagged/cancelled)
- Fraud score & reason
- Face verification flag

### SimulationLog
- User ID
- Data type (email/sms/phone)
- Input data
- Conversation (JSON)
- Fraud analysis results

### ContactMessage
- Name, email, subject, message
- Status tracking

### APIToken
- User ID
- Token string
- Usage tracking

## 🌐 API Endpoints

### Authentication
```
POST /api/auth/token
```
Generate API token with username/password

### Fraud Detection
```
POST /api/fraud-check
Authorization: Bearer <token>

{
    "data_type": "email|sms|phone",
    "content": "content to analyze"
}
```

### Transactions
```
POST /api/transactions/submit
Authorization: Bearer <token>

{
    "sender_id": "user123",
    "receiver_id": "user456",
    "amount": 150.00
}
```

### Tokenization
```
POST /api/tokenize
Authorization: Bearer <token>

{
    "data": "sensitive_data",
    "type": "email|phone|custom"
}
```

## 🎯 Key Features Explained

### 1. Two-Factor Authentication (2FA)
- Uses `pyotp` library for TOTP generation
- QR code generated with `qrcode` library
- Compatible with Google Authenticator, Authy, etc.
- Required during login if enabled

### 2. Transaction Fraud Detection
- Threshold: 30% of user balance triggers AI check
- Gemini AI analyzes transaction context
- Fraud score > 0.7 flags for review
- Users can approve/cancel flagged transactions

### 3. Face Verification
- Dummy implementation for demo
- Checkbox confirmation required
- Shows animated face icon
- In production: integrate with face recognition API

### 4. Simulations
- Test fraud detection with sample data
- Generates conversation between users
- Stores simulation history
- Displays fraud score and indicators

### 5. Financial Insights
- AI-generated spending recommendations
- Transaction pattern analysis
- Balance monitoring
- Fraud prevention tips

## 🔒 Security Best Practices

1. **Change SECRET_KEY**: Use a strong random value in production
2. **Set GEMINI_API_KEY**: Store in environment variable, not code
3. **Use HTTPS**: Always use SSL/TLS in production
4. **Database**: Switch from SQLite to PostgreSQL for production
5. **Rate Limiting**: Implement API rate limiting
6. **Input Validation**: All forms have CSRF protection

## 🐛 Troubleshooting

### Import Errors
```powershell
# Make sure all dependencies are installed
pip install -r requirements.txt
```

### Database Issues
```powershell
# Delete database and restart
Remove-Item app.db
python app.py
```

### Gemini API Errors
- Check API key is set correctly
- Verify API quota isn't exceeded
- Ensure internet connection is active

### 2FA Not Working
- Ensure system time is synchronized
- Check 6-digit code is current (refreshes every 30 seconds)
- Try manual entry of secret key

## 📚 Dependencies

- **Flask**: Web framework
- **Flask-Login**: Session management
- **Flask-WTF**: Form handling with CSRF protection
- **Flask-SQLAlchemy**: ORM for database
- **pyotp**: TOTP for 2FA
- **qrcode**: QR code generation
- **google-generativeai**: Gemini AI API
- **Werkzeug**: Password hashing & security

## 🚧 Future Enhancements

- [ ] Email verification on registration
- [ ] Password reset functionality
- [ ] Real face recognition integration
- [ ] Machine learning model for fraud patterns
- [ ] Webhook notifications
- [ ] Rate limiting implementation
- [ ] Admin panel for fraud review
- [ ] Export transaction history
- [ ] Multi-currency support
- [ ] Mobile app integration

## 📄 License

This is a demonstration project for educational purposes.

## 🤝 Support

- **Contact Form**: Available at `/contact`
- **Documentation**: Full guide at `/user-guide`
- **FAQ**: Common questions at `/faq`

## 👥 Credits

- **AI Model**: Google Gemini API
- **Framework**: Flask
- **UI**: Bootstrap 5
- **Icons**: Font Awesome

---

**Demo System**: This is a demonstration fraud detection system. Transaction amounts are dummy values and no real money is involved.


