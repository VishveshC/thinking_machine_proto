"""
FraudGuard - Comprehensive Fraud Detection System
Main Application File
"""

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
import secrets
import json
import io
import qrcode
import base64
import traceback

from config import Config
from models import db, User, Transaction, FraudPattern, SimulationLog, ContactMessage, APIToken
from forms import RegistrationForm, LoginForm, Enable2FAForm, TransactionForm, SimulationForm, ContactForm
from fraud_service import fraud_service

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.lower(),
            email=form.email.data.lower(),
            balance=Config.INITIAL_BALANCE
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! You have been credited with ₹10,000.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(db.func.lower(User.username) == form.username.data.lower()).first()
        if user and user.check_password(form.password.data):
            if user.two_fa_enabled:
                if not form.totp_token.data:
                    flash("Please enter your 2FA code.", "warning")
                    return render_template("login.html", form=form)
                if not user.verify_totp(form.totp_token.data):
                    flash("Invalid 2FA code. Please try again.", "danger")
                    return render_template("login.html", form=form)
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("index"))


@app.route("/setup-2fa", methods=["GET", "POST"])
@login_required
def setup_2fa():
    if current_user.two_fa_enabled:
        flash("2FA is already enabled on your account.", "info")
        return redirect(url_for("dashboard"))
    form = Enable2FAForm()
    if not current_user.totp_secret:
        current_user.generate_totp_secret()
        db.session.commit()
    if form.validate_on_submit():
        if current_user.verify_totp(form.totp_token.data):
            current_user.two_fa_enabled = True
            db.session.commit()
            flash("Two-Factor Authentication enabled successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid code. Please try again.", "danger")
    qr_uri = current_user.get_totp_uri()
    qr = qrcode.make(qr_uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    qr_code_base64 = base64.b64encode(buf.getvalue()).decode()
    return render_template("setup_2fa.html", form=form, qr_code=qr_code_base64, secret=current_user.totp_secret)


@app.route("/dashboard")
@login_required
def dashboard():
    recent_transactions = Transaction.query.filter(
        (Transaction.sender_id == current_user.id) | (Transaction.receiver_id == current_user.id)
    ).order_by(Transaction.created_at.desc()).limit(5).all()
    flagged_transactions = Transaction.query.filter(
        Transaction.sender_id == current_user.id,
        Transaction.requires_review == True,
        Transaction.status == "flagged"
    ).all()
    sent_transactions = Transaction.query.filter(
        Transaction.sender_id == current_user.id,
        Transaction.status == "completed"
    ).all()
    received_transactions = Transaction.query.filter(
        Transaction.receiver_id == current_user.id,
        Transaction.status == "completed"
    ).all()
    total_sent = sum(t.amount for t in sent_transactions)
    total_received = sum(t.amount for t in received_transactions)
    safe_transactions = Transaction.query.filter(
        (Transaction.sender_id == current_user.id) | (Transaction.receiver_id == current_user.id),
        Transaction.status == "completed",
        Transaction.fraud_score < 0.3
    ).count()
    ai_insight = None
    if len(sent_transactions) > 0:
        avg_transaction = total_sent / len(sent_transactions)
        if avg_transaction > current_user.balance * 0.2:
            ai_insight = f"You're sending large transactions averaging ₹{avg_transaction:.2f}. Consider spreading payments for better security."
    
    # Calculate credit score (dummy algorithm based on account activity)
    credit_score = 300 + min(550, int(current_user.balance / 10))  # Base score
    credit_score += min(100, len(sent_transactions) * 5)  # Activity bonus
    credit_score += min(50, safe_transactions * 2)  # Safe transaction bonus
    credit_score = min(850, credit_score)  # Cap at 850
    
    # Determine credit rating
    if credit_score >= 750:
        credit_rating = "excellent"
    elif credit_score >= 650:
        credit_rating = "good"
    elif credit_score >= 550:
        credit_rating = "fair"
    else:
        credit_rating = "poor"
    
    # Get AI-powered credit tips
    credit_tips = []
    try:
        tips_text = fraud_service.generate_credit_tips(
            credit_score=credit_score,
            balance=current_user.balance,
            transaction_count=len(sent_transactions) + len(received_transactions)
        )
        # Split tips by newlines or bullet points
        credit_tips = [tip.strip().lstrip('•-*').strip() for tip in tips_text.split('\n') if tip.strip() and len(tip.strip()) > 10]
    except Exception as e:
        print(f"Credit tips error: {e}")
        credit_tips = ["Maintain a healthy balance", "Keep making transactions", "Monitor for fraud regularly"]
    
    transaction_form = TransactionForm()
    return render_template("new_dashboard.html",
                         recent_transactions=recent_transactions,
                         flagged_transactions=flagged_transactions,
                         recent_count=len(recent_transactions),
                         flagged_count=len(flagged_transactions),
                         total_sent=total_sent,
                         total_received=total_received,
                         transaction_count=len(sent_transactions) + len(received_transactions),
                         safe_transactions=safe_transactions,
                         ai_insight=ai_insight,
                         credit_score=credit_score,
                         credit_rating=credit_rating,
                         credit_tips=credit_tips[:5],
                         transaction_form=transaction_form)


@app.route("/financial-advisor")
@login_required
def financial_advisor():
    return render_template("financial_advisor.html")


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        conversation_history = data.get("history", [])
        
        if not user_message:
            return jsonify({"success": False, "error": "Message is required"}), 400
        
        # Get user context for personalized advice
        user_context = {
            "balance": float(current_user.balance),
            "total_transactions": Transaction.query.filter(
                (Transaction.sender_id == current_user.id) | (Transaction.receiver_id == current_user.id)
            ).count(),
            "recent_spending": sum(
                t.amount for t in Transaction.query.filter(
                    Transaction.sender_id == current_user.id,
                    Transaction.status == "completed"
                ).order_by(Transaction.created_at.desc()).limit(10).all()
            )
        }
        
        # Get AI response from Gemini
        response = fraud_service.get_financial_advice(
            user_message, 
            user_context, 
            conversation_history
        )
        
        # Get YouTube video recommendation
        youtube_video = fraud_service.get_youtube_recommendation(user_message)
        
        return jsonify({
            "success": True,
            "response": response,
            "youtube_video": youtube_video
        })
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "Sorry, I encountered an error. Please try again."
        }), 500


@app.route("/api-docs")
def api_docs():
    return render_template("api_docs.html")


@app.route("/user-guide")
def user_guide():
    return render_template("user_guide.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/simulations", methods=["GET"])
@login_required
def simulations():
    form = SimulationForm()
    simulation_history = SimulationLog.query.filter_by(
        user_id=current_user.id
    ).order_by(SimulationLog.created_at.desc()).limit(10).all()
    return render_template("simulations.html", form=form, simulation_history=simulation_history, simulation_result=None, conversation=None)


@app.route("/run-simulation", methods=["POST"])
@login_required
def run_simulation():
    form = SimulationForm()
    if form.validate_on_submit():
        data_type = form.data_type.data
        input_data = form.input_data.data
        sender_name = form.sender_name.data
        receiver_name = form.receiver_name.data
        if data_type == "email":
            result = fraud_service.analyze_email(input_data)
        elif data_type == "sms":
            result = fraud_service.analyze_sms(input_data)
        elif data_type == "phone":
            result = fraud_service.analyze_phone(input_data)
        else:
            result = {"is_fraud": False, "score": 0, "reason": "Unknown type", "patterns": []}
        conversation_data = fraud_service.generate_conversation_simulation(data_type, input_data, sender_name, receiver_name)
        conversation = conversation_data.get("conversation", [])
        sim_log = SimulationLog(
            user_id=current_user.id,
            simulation_type=data_type,
            input_data=input_data,
            conversation=json.dumps(conversation),
            fraud_detected=result["is_fraud"],
            fraud_score=result["score"],
            fraud_details=result["reason"]
        )
        db.session.add(sim_log)
        db.session.commit()
        simulation_history = SimulationLog.query.filter_by(user_id=current_user.id).order_by(SimulationLog.created_at.desc()).limit(10).all()
        return render_template("simulations.html", form=form, simulation_history=simulation_history, simulation_result=result, conversation=conversation)
    return redirect(url_for("simulations"))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    success = False
    if form.validate_on_submit():
        message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        flash("Message sent successfully! We will respond within 24 hours.", "success")
        success = True
    return render_template("contact.html", form=form, success=success)


@app.route("/send-money", methods=["POST"])
@login_required
def send_money():
    form = TransactionForm()
    if form.validate_on_submit():
        recipient_username = form.recipient_username.data.lower()
        amount = form.amount.data
        description = form.description.data
        recipient = User.query.filter(db.func.lower(User.username) == recipient_username).first()
        if not recipient:
            flash("Recipient user not found.", "danger")
            return redirect(url_for("dashboard"))
        if recipient.id == current_user.id:
            flash("You cannot send money to yourself.", "warning")
            return redirect(url_for("dashboard"))
        if current_user.balance < amount:
            flash(f"Insufficient funds. Your balance: ₹{current_user.balance:.2f}", "danger")
            return redirect(url_for("dashboard"))
        transaction = Transaction(
            sender_id=current_user.id,
            receiver_id=recipient.id,
            amount=amount,
            description=description,
            face_verified=form.face_verification.data
        )
        if amount > current_user.balance * Config.LARGE_TRANSACTION_THRESHOLD:
            fraud_result = fraud_service.analyze_transaction({
                "amount": amount,
                "sender": current_user.username,
                "receiver": recipient.username,
                "description": description,
                "sender_balance": current_user.balance
            })
            transaction.fraud_score = fraud_result["score"]
            transaction.fraud_reason = fraud_result["reason"]
            if fraud_result["is_fraud"] or fraud_result["score"] > 0.7:
                transaction.status = "flagged"
                transaction.requires_review = True
                db.session.add(transaction)
                db.session.commit()
                flash("Transaction flagged for review due to suspicious activity. Please check your dashboard.", "warning")
                return redirect(url_for("dashboard"))
        current_user.balance -= amount
        recipient.balance += amount
        transaction.status = "completed"
        transaction.completed_at = datetime.utcnow()
        db.session.add(transaction)
        db.session.commit()
        flash(f"Successfully sent ₹{amount:.2f} to {recipient.username}!", "success")
        return redirect(url_for("dashboard"))
    flash("Invalid transaction data.", "danger")
    return redirect(url_for("dashboard"))


@app.route("/transaction/<int:txn_id>/approve", methods=["POST"])
@login_required
def approve_transaction(txn_id):
    transaction = Transaction.query.get_or_404(txn_id)
    if transaction.sender_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    if transaction.status != "flagged":
        return jsonify({"error": "Transaction not flagged"}), 400
    if current_user.balance < transaction.amount:
        return jsonify({"error": "Insufficient funds"}), 400
    recipient = User.query.get(transaction.receiver_id)
    current_user.balance -= transaction.amount
    recipient.balance += transaction.amount
    transaction.status = "completed"
    transaction.completed_at = datetime.utcnow()
    transaction.requires_review = False
    db.session.commit()
    return jsonify({"message": "Transaction approved and completed"})


@app.route("/transaction/<int:txn_id>/cancel", methods=["POST"])
@login_required
def cancel_transaction(txn_id):
    transaction = Transaction.query.get_or_404(txn_id)
    if transaction.sender_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    transaction.status = "cancelled"
    transaction.requires_review = False
    db.session.commit()
    return jsonify({"message": "Transaction cancelled"})


@app.route("/api/auth/token", methods=["POST"])
def api_auth_token():
    data = request.get_json()
    username = data.get("username", "").lower()
    password = data.get("password", "")
    user = User.query.filter(db.func.lower(User.username) == username).first()
    if not user or not user.check_password(password):
        return jsonify({"status": "error", "error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"}}), 401
    token = secrets.token_urlsafe(32)
    api_token = APIToken(user_id=user.id, token=token)
    db.session.add(api_token)
    db.session.commit()
    return jsonify({"status": "success", "token": token, "expires_at": None})


@app.route("/api/fraud-check", methods=["POST"])
def api_fraud_check():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"status": "error", "error": {"code": "INVALID_TOKEN", "message": "Missing or invalid authorization header"}}), 401
    token = auth_header.split(" ")[1]
    api_token = APIToken.query.filter_by(token=token, is_active=True).first()
    if not api_token:
        return jsonify({"status": "error", "error": {"code": "INVALID_TOKEN", "message": "Invalid or expired token"}}), 401
    api_token.last_used = datetime.utcnow()
    api_token.usage_count += 1
    db.session.commit()
    data = request.get_json()
    data_type = data.get("data_type")
    content = data.get("content")
    if not data_type or not content:
        return jsonify({"status": "error", "error": {"code": "INVALID_REQUEST", "message": "Missing required fields"}}), 400
    if data_type == "email":
        result = fraud_service.analyze_email(content)
    elif data_type == "sms":
        result = fraud_service.analyze_sms(content)
    elif data_type == "phone":
        result = fraud_service.analyze_phone(content)
    else:
        return jsonify({"status": "error", "error": {"code": "INVALID_TYPE", "message": "Invalid data_type"}}), 400
    request_id = f"req_{secrets.token_hex(8)}"
    return jsonify({
        "status": "success",
        "result": {
            "is_fraud": result["is_fraud"],
            "confidence_score": result["score"],
            "fraud_indicators": result["patterns"],
            "explanation": result["reason"],
            "severity": result.get("severity", "low")
        },
        "request_id": request_id
    })


@app.route("/api/transactions/submit", methods=["POST"])
def api_transaction_submit():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"status": "error", "error": {"code": "INVALID_TOKEN"}}), 401
    token = auth_header.split(" ")[1]
    api_token = APIToken.query.filter_by(token=token, is_active=True).first()
    if not api_token:
        return jsonify({"status": "error", "error": {"code": "INVALID_TOKEN"}}), 401
    return jsonify({"status": "success", "transaction_id": "txn_demo", "fraud_check": {"requires_review": False, "fraud_score": 0.1, "status": "approved"}})


@app.route("/api/tokenize", methods=["POST"])
def api_tokenize():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"status": "error", "error": {"code": "INVALID_TOKEN"}}), 401
    data = request.get_json()
    sensitive_data = data.get("data")
    if not sensitive_data:
        return jsonify({"status": "error", "error": {"code": "MISSING_DATA"}}), 400
    token = f"tok_{secrets.token_hex(16)}"
    return jsonify({"status": "success", "token": token, "expires_at": "2025-11-09T10:30:00Z"})


@app.errorhandler(404)
def not_found_error(error):
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash("An internal error occurred. Please try again later.", "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database initialized")
    app.run(debug=True)
