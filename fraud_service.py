"""
Gemini API Service for Fraud Detection
"""
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google.generativeai not available. Using fallback responses.")

from config import Config
import json
import re
import traceback

# Configure Gemini if available
if GENAI_AVAILABLE and Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your-gemini-api-key-here':
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        GEMINI_CONFIGURED = True
    except Exception as e:
        GEMINI_CONFIGURED = False
        print(f"Warning: Failed to configure Gemini API: {e}")
        traceback.print_exc()
else:
    GEMINI_CONFIGURED = False
    print("Warning: Gemini API key not configured. Using fallback responses.")

class FraudDetectionService:
    """
    Wrapper for Gemini API to detect fraud in various data types.
    Falls back to rule-based detection if API is unavailable.
    """
    
    def __init__(self):
        if GEMINI_CONFIGURED:
            try:
                # Use gemini-2.0-flash-exp (latest model as of Nov 2024)
                # Falls back to other models if not available
                try:
                    self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
                except:
                    # Try gemini-1.5-flash as fallback
                    try:
                        self.model = genai.GenerativeModel('gemini-2.5-flash')
                    except:
                        # Last resort: use gemini-1.5-pro
                        self.model = genai.GenerativeModel('gemini-1.5-pro')
                self.use_api = True
                print(f"Gemini model initialized: {self.model.model_name}")
            except Exception as e:
                print(f"Failed to initialize Gemini model: {e}")
                traceback.print_exc()
                self.use_api = False
        else:
            self.use_api = False
    
    def _fallback_analysis(self, content, data_type):
        """Simple rule-based fraud detection as fallback."""
        fraud_keywords = [
            'urgent', 'verify', 'suspended', 'click here', 'confirm', 'account',
            'password', 'social security', 'ssn', 'prize', 'winner', 'lottery',
            'tax', 'irs', 'refund', 'suspended', 'unusual activity', 'verify identity',
            'click immediately', 'act now', 'limited time', 'confirm your', 'update your'
        ]
        
        content_lower = str(content).lower()
        detected_keywords = [kw for kw in fraud_keywords if kw in content_lower]
        
        fraud_score = min(len(detected_keywords) * 0.15, 0.95)
        is_fraud = fraud_score > 0.4
        
        return {
            'is_fraud': is_fraud,
            'score': fraud_score,
            'reason': f"Detected {len(detected_keywords)} fraud indicators" if is_fraud else "No significant fraud indicators detected",
            'patterns': detected_keywords[:5],
            'severity': 'high' if fraud_score > 0.7 else 'medium' if fraud_score > 0.4 else 'low'
        }
    
    def generate_credit_tips(self, user_data):
        """Generate credit improvement tips using AI or fallback."""
        credit_score = user_data.get('credit_score', 650)
        balance = user_data.get('balance', 0)
        transaction_count = user_data.get('transaction_count', 0)
        
        prompt = f"""
        Generate 3-5 personalized tips to improve a credit score for a user with:
        - Current credit score: {credit_score}
        - Account balance: ₹{balance}
        - Number of transactions: {transaction_count}
        
        Provide actionable, specific advice in a friendly tone. Return as JSON:
        {{
            "tips": ["tip1", "tip2", "tip3", "tip4", "tip5"],
            "priority_action": "Most important thing to do"
        }}
        """
        
        if self.use_api:
            try:
                response = self.model.generate_content(prompt)
                result = self._parse_gemini_response(response.text)
                if 'tips' in result:
                    return result
            except Exception as e:
                print(f"AI credit tips failed: {e}")
                traceback.print_exc()
        
        # Fallback tips
        tips = []
        if credit_score < 700:
            tips.append("Make all payments on time to build a positive payment history")
            tips.append("Keep your account balance above ₹1,000 to show financial stability")
        if transaction_count < 5:
            tips.append("Increase account activity with regular, small transactions")
        tips.append("Avoid large transactions that exceed 30% of your balance")
        tips.append("Enable 2FA for better account security - lenders value secure accounts")
        
        return {
            'tips': tips[:5],
            'priority_action': tips[0] if tips else "Continue maintaining good financial habits"
        }
    
    def analyze_email(self, email_content):
        """
        Analyze email content for fraud indicators.
        
        Returns:
            dict: {
                'is_fraud': bool,
                'score': float (0-1),
                'reason': str,
                'patterns': list
            }
        """
        if not self.use_api:
            return self._fallback_analysis(email_content, 'email')
        
        prompt = f"""
        Analyze the following email for fraud indicators. Look for:
        - Phishing attempts
        - Suspicious links or attachments
        - Urgency tactics
        - Impersonation
        - Request for sensitive information
        - Grammar/spelling issues
        - Suspicious sender information
        
        Email content:
        {email_content}
        
        Respond in JSON format:
        {{
            "is_fraud": true/false,
            "confidence_score": 0.0-1.0,
            "fraud_indicators": ["indicator1", "indicator2"],
            "explanation": "Brief explanation",
            "severity": "low/medium/high"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)
            return result
        except Exception as e:
            print(f"Gemini API error in analyze_email: {e}")
            traceback.print_exc()
            return self._fallback_analysis(email_content, 'email')
    
    def analyze_sms(self, sms_content):
        """
        Analyze SMS message for fraud indicators.
        
        Returns similar dict as analyze_email
        """
        if not self.use_api:
            return self._fallback_analysis(sms_content, 'sms')
        
        prompt = f"""
        Analyze the following SMS message for fraud indicators. Look for:
        - Smishing (SMS phishing) attempts
        - Suspicious links
        - Requests for personal/financial information
        - Impersonation of banks/companies
        - Prize/lottery scams
        - Urgency or threatening language
        - Suspicious phone numbers
        
        SMS content:
        {sms_content}
        
        Respond in JSON format:
        {{
            "is_fraud": true/false,
            "confidence_score": 0.0-1.0,
            "fraud_indicators": ["indicator1", "indicator2"],
            "explanation": "Brief explanation",
            "severity": "low/medium/high"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)
            return result
        except Exception as e:
            print(f"Gemini API error in analyze_sms: {e}")
            traceback.print_exc()
            return self._fallback_analysis(sms_content, 'sms')
    
    def analyze_phone(self, phone_number, context=''):
        """
        Analyze phone number for fraud indicators.
        
        Args:
            phone_number: Phone number to analyze
            context: Additional context about the call/usage
        
        Returns similar dict as analyze_email
        """
        prompt = f"""
        Analyze the following phone number for fraud indicators:
        
        Phone number: {phone_number}
        Context: {context if context else 'No additional context'}
        
        Look for:
        - Known spam/scam number patterns
        - Suspicious area codes
        - VoIP/temporary numbers
        - International scam patterns
        - Robocall indicators
        
        Respond in JSON format:
        {{
            "is_fraud": true/false,
            "confidence_score": 0.0-1.0,
            "fraud_indicators": ["indicator1", "indicator2"],
            "explanation": "Brief explanation",
            "severity": "low/medium/high"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)
            return result
        except Exception as e:
            print(f"Gemini API error in analyze_phone: {e}")
            traceback.print_exc()
            return {
                'is_fraud': False,
                'score': 0.0,
                'reason': f'Error analyzing phone: {str(e)}',
                'patterns': []
            }
    
    def analyze_transaction(self, transaction_data):
        """
        Analyze a transaction for fraud indicators.
        
        Args:
            transaction_data: dict with keys like amount, sender, receiver, description
        
        Returns similar dict as analyze_email
        """
        prompt = f"""
        Analyze the following transaction for fraud indicators:
        
    Amount: ₹{transaction_data.get('amount', 0)}
        Sender: {transaction_data.get('sender', 'Unknown')}
        Receiver: {transaction_data.get('receiver', 'Unknown')}
        Description: {transaction_data.get('description', 'No description')}
    Sender Balance: ₹{transaction_data.get('sender_balance', 0)}
        
        Look for:
        - Unusual transaction amounts
        - Suspicious patterns
        - High-risk receivers
        - Money laundering indicators
        - Account takeover signs
        
        Respond in JSON format:
        {{
            "is_fraud": true/false,
            "confidence_score": 0.0-1.0,
            "fraud_indicators": ["indicator1", "indicator2"],
            "explanation": "Brief explanation",
            "severity": "low/medium/high",
            "recommendation": "approve/review/block"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)
            return result
        except Exception as e:
            print(f"Gemini API error in analyze_transaction: {e}")
            traceback.print_exc()
            return {
                'is_fraud': False,
                'score': 0.0,
                'reason': f'Error analyzing transaction: {str(e)}',
                'patterns': [],
                'recommendation': 'review'
            }
    
    def generate_conversation_simulation(self, data_type, input_data, sender_name, receiver_name):
        """
        Generate a simulated conversation for demonstration.
        
        Returns:
            dict: {
                'conversation': list of messages,
                'fraud_analysis': fraud analysis result
            }
        """
        prompt = f"""
        Generate a realistic conversation simulation between {sender_name} and {receiver_name} 
        involving the following {data_type}:
        
        Content: {input_data}
        
        Create a conversation with 4-6 exchanges that demonstrates how this {data_type} 
        might be used in a fraud scenario or legitimate scenario. Then analyze it for fraud.
        
        Respond in JSON format:
        {{
            "conversation": [
                {{"speaker": "name", "message": "text", "timestamp": "time"}},
                ...
            ],
            "fraud_analysis": {{
                "is_fraud": true/false,
                "confidence_score": 0.0-1.0,
                "fraud_indicators": ["indicator1", "indicator2"],
                "explanation": "Brief explanation"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)
            return result
        except Exception as e:
            print(f"Gemini API error in generate_conversation_simulation: {e}")
            traceback.print_exc()
            return {
                'conversation': [
                    {'speaker': sender_name, 'message': input_data, 'timestamp': '00:00'},
                    {'speaker': receiver_name, 'message': 'Received', 'timestamp': '00:01'}
                ],
                'fraud_analysis': {
                    'is_fraud': False,
                    'confidence_score': 0.0,
                    'fraud_indicators': [],
                    'explanation': f'Error generating simulation: {str(e)}'
                }
            }
    
    def _parse_gemini_response(self, response_text):
        """
        Parse Gemini's response and extract JSON.
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # Normalize to our format
                return {
                    'is_fraud': data.get('is_fraud', False),
                    'score': data.get('confidence_score', 0.0),
                    'reason': data.get('explanation', 'No explanation provided'),
                    'patterns': data.get('fraud_indicators', []),
                    'severity': data.get('severity', 'low'),
                    'recommendation': data.get('recommendation', 'review')
                }
            else:
                # Fallback if no JSON found
                return {
                    'is_fraud': False,
                    'score': 0.0,
                    'reason': 'Could not parse response',
                    'patterns': []
                }
        except json.JSONDecodeError:
            return {
                'is_fraud': False,
                'score': 0.0,
                'reason': 'Invalid JSON response',
                'patterns': []
            }
    
    def get_financial_advice(self, user_message, user_context, conversation_history):
        """
        Generate personalized financial advice using Gemini API.
        Maintains privacy by not storing sensitive information.
        """
        if not self.use_api:
            return self._fallback_financial_advice(user_message)
        
        try:
            # Build context-aware prompt
            context_summary = f"""You are an AI financial advisor providing helpful, personalized financial advice.

User Context (for context only, do not mention specific numbers unless relevant):
- Current account balance: ₹{user_context.get('balance', 0):.2f}
- Total transactions: {user_context.get('total_transactions', 0)}
- Recent spending: ₹{user_context.get('recent_spending', 0):.2f}

Conversation History:
{self._format_conversation_history(conversation_history)}

User Question: {user_message}

Provide a helpful, clear, and actionable response. Be friendly but professional. If the question is about investments, budgeting, savings, or credit, provide practical advice. Keep responses concise (2-3 paragraphs max). Do not provide specific investment recommendations or guarantee returns. Always remind users to consult with certified financial advisors for major financial decisions."""

            response = self.model.generate_content(context_summary)
            
            if response and response.text:
                return response.text.strip()
            else:
                return self._fallback_financial_advice(user_message)
                
        except Exception as e:
            print(f"Gemini API error in financial advice: {e}")
            traceback.print_exc()
            return self._fallback_financial_advice(user_message)
    
    def _format_conversation_history(self, history):
        """Format conversation history for context."""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for msg in history[-6:]:  # Last 6 messages for context
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            formatted.append(f"{role.capitalize()}: {content[:100]}...")
        
        return "\n".join(formatted)
    
    def _fallback_financial_advice(self, user_message):
        """Provide basic financial advice when API is unavailable."""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['budget', 'budgeting', 'spend']):
            return """Creating a budget is essential for financial health! Here's a simple approach:

1. **Track Your Income**: Calculate your total monthly income after taxes.
2. **List Your Expenses**: Categorize them as essential (rent, utilities, food) and non-essential (entertainment, dining out).
3. **Follow the 50/30/20 Rule**: Allocate 50% to needs, 30% to wants, and 20% to savings/debt repayment.
4. **Use Budgeting Tools**: Apps like Mint or YNAB can help you stay on track.

Remember, consistency is key! Review and adjust your budget monthly."""

        elif any(word in message_lower for word in ['invest', 'investment', 'stock', 'etf', 'mutual fund']):
            return """Investment decisions should align with your financial goals and risk tolerance. Here are some general principles:

1. **Start with an Emergency Fund**: Save 3-6 months of expenses before investing.
2. **Diversify**: Don't put all your money in one investment. Consider index funds or ETFs for broad market exposure.
3. **Think Long-Term**: Markets fluctuate, but historically grow over time. Avoid emotional decisions.
4. **Consider Your Timeline**: Younger investors can typically take more risk than those near retirement.

⚠️ **Important**: This is general information only. Consult a certified financial advisor for personalized investment advice."""

        elif any(word in message_lower for word in ['credit', 'credit score', 'fico']):
            return """Improving your credit score takes time but is achievable! Here's how:

1. **Pay Bills On Time**: Payment history is the most important factor (35% of your score).
2. **Keep Credit Utilization Low**: Use less than 30% of your available credit.
3. **Don't Close Old Accounts**: Length of credit history matters (15% of your score).
4. **Limit New Credit Applications**: Too many hard inquiries can hurt your score.
5. **Check Your Credit Report**: Look for errors and dispute them if found.

Building good credit is a marathon, not a sprint. Stay consistent!"""

        elif any(word in message_lower for word in ['save', 'saving', 'savings', 'emergency fund']):
            return """Building savings is crucial for financial security! Here's a practical approach:

1. **Start Small**: Even ₹20 per week adds up to over ₹1,000 per year.
2. **Automate It**: Set up automatic transfers to a savings account each payday.
3. **Build an Emergency Fund**: Aim for 3-6 months of living expenses in a high-yield savings account.
4. **Use the Right Accounts**: Look for high-yield savings accounts with no fees and competitive interest rates.

Pro tip: Treat savings like a non-negotiable bill you pay to yourself first!"""

        elif any(word in message_lower for word in ['debt', 'loan', 'pay off', 'repay']):
            return """Managing debt effectively can save you thousands in interest! Consider these strategies:

1. **List All Debts**: Know what you owe, interest rates, and minimum payments.
2. **Choose a Strategy**:
   - **Avalanche Method**: Pay off highest interest rate first (saves most money)
   - **Snowball Method**: Pay off smallest balance first (builds momentum)
3. **Pay More Than Minimum**: Even small extra payments significantly reduce interest over time.
4. **Consider Debt Consolidation**: If you have multiple high-interest debts, consolidation might help.

Remember: Avoid taking on new debt while paying off existing debt!"""

        else:
            return """I'm here to help with your financial questions! I can provide guidance on:

📊 **Budgeting**: Creating and maintaining a budget that works for you
💰 **Saving**: Building emergency funds and reaching savings goals
💳 **Credit**: Understanding and improving your credit score
📈 **Investing**: Basic investment principles and strategies (general information only)
🏦 **Debt Management**: Strategies for paying off loans and managing debt

What specific area of personal finance would you like to discuss?"""
    
    def get_youtube_recommendation(self, user_query):
        """
        Search for relevant financial education YouTube videos.
        Uses YouTube Data API v3.
        """
        try:
            import requests
            from config import Config
            
            # Check if YouTube API key is configured
            youtube_api_key = getattr(Config, 'YOUTUBE_API_KEY', None)
            if not youtube_api_key or youtube_api_key == 'your-youtube-api-key-here':
                return self._fallback_youtube_recommendation(user_query)
            
            # Enhance search query with finance keywords
            search_query = f"{user_query} personal finance tutorial"
            
            # YouTube Data API search endpoint
            youtube_search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_query,
                'key': youtube_api_key,
                'maxResults': 1,
                'type': 'video',
                'relevanceLanguage': 'en',
                'safeSearch': 'strict',
                'order': 'relevance'
            }
            
            response = requests.get(youtube_search_url, params=params, timeout=5)
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                video = data['items'][0]
                video_id = video['id']['videoId']
                snippet = video['snippet']
                
                return {
                    'title': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': snippet['thumbnails']['high']['url']
                }
            else:
                return self._fallback_youtube_recommendation(user_query)
                
        except Exception as e:
            print(f"YouTube API error: {e}")
            traceback.print_exc()
            return self._fallback_youtube_recommendation(user_query)
    
    def _fallback_youtube_recommendation(self, user_query):
        """Provide curated finance video recommendations as fallback."""
        query_lower = user_query.lower()
        
        # Curated list of popular financial education channels
        recommendations = {
            'budget': {
                'title': 'How to Budget Your Money - The 50/30/20 Rule',
                'url': 'https://www.youtube.com/watch?v=HQzoZfc3GwQ',
                'thumbnail': 'https://i.ytimg.com/vi/HQzoZfc3GwQ/maxresdefault.jpg'
            },
            'invest': {
                'title': 'Investing for Beginners - Complete Guide',
                'url': 'https://www.youtube.com/watch?v=gFQNPmLKj1k',
                'thumbnail': 'https://i.ytimg.com/vi/gFQNPmLKj1k/maxresdefault.jpg'
            },
            'credit': {
                'title': 'How to Build Credit Score - Expert Tips',
                'url': 'https://www.youtube.com/watch?v=YBCT3HA4WTA',
                'thumbnail': 'https://i.ytimg.com/vi/YBCT3HA4WTA/maxresdefault.jpg'
            },
            'save': {
                'title': 'How to Save Money Fast - Practical Tips',
                'url': 'https://www.youtube.com/watch?v=5WfCjg0V2EE',
                'thumbnail': 'https://i.ytimg.com/vi/5WfCjg0V2EE/maxresdefault.jpg'
            },
            'debt': {
                'title': 'How to Get Out of Debt - Proven Strategies',
                'url': 'https://www.youtube.com/watch?v=YlGbRN5Nk-M',
                'thumbnail': 'https://i.ytimg.com/vi/YlGbRN5Nk-M/maxresdefault.jpg'
            }
        }
        
        # Match query to recommendation
        for keyword, video in recommendations.items():
            if keyword in query_lower:
                return video
        
        # Default recommendation
        return {
            'title': 'Personal Finance 101 - Complete Beginner Guide',
            'url': 'https://www.youtube.com/watch?v=1Az8Aj91Xjo',
            'thumbnail': 'https://i.ytimg.com/vi/1Az8Aj91Xjo/maxresdefault.jpg'
        }


# Singleton instance
fraud_service = FraudDetectionService()
