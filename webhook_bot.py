import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from config import BOT_TOKEN, BOT_NAME, BOT_VERSION, OWNER_ID
from database import load_user, save_user
from buttons import get_main_menu_keyboard

# ============================================
# FLASK APP FOR WEBHOOK
# ============================================

app = Flask(__name__)

# Store bot instance (will be initialized)
bot = None

def send_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    """Send message via Telegram API"""
    import requests
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=data, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def send_reply_keyboard(chat_id, text, buttons):
    """Send message with reply keyboard"""
    markup = {
        'keyboard': buttons,
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    return send_message(chat_id, text, markup)

# ============================================
# WEBHOOK HANDLER
# ============================================

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    try:
        update = request.get_json()
        
        if not update:
            return jsonify({'status': 'ok'})
        
        # Handle message
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            user_name = message['from'].get('first_name', 'User')
            text = message.get('text', '')
            
            # Process commands
            if text == '/start':
                # Load or create user
                user_data = load_user(user_id)
                if not user_data.get('first_name'):
                    user_data['first_name'] = user_name
                    user_data['joined_date'] = datetime.now().isoformat()
                    save_user(user_id, user_data)
                
                welcome_msg = f"🧠 *Welcome to {BOT_NAME}, {user_name}!* 🌱\n\n"
                welcome_msg += "Select a topic to start your quiz journey!\n\n"
                welcome_msg += "📚 Mathematics\n"
                welcome_msg += "🔬 Science\n"
                welcome_msg += "📖 English Grammar\n"
                welcome_msg += "🧬 Biology\n"
                welcome_msg += "⚡ Physics\n"
                welcome_msg += "🌍 General Knowledge"
                
                buttons = [
                    ["📚 Mathematics", "🔬 Science"],
                    ["📖 English Grammar", "🧬 Biology"],
                    ["⚡ Physics", "🌍 General Knowledge"],
                    ["❓ Help", "ℹ️ About"]
                ]
                
                send_reply_keyboard(chat_id, welcome_msg, buttons)
            
            elif text == '/menu':
                welcome_msg = f"🧠 *Welcome back, {user_name}!* 🌱\n\nSelect a topic:"
                buttons = [
                    ["📚 Mathematics", "🔬 Science"],
                    ["📖 English Grammar", "🧬 Biology"],
                    ["⚡ Physics", "🌍 General Knowledge"],
                    ["📊 My Stats", "🏆 Leaderboard"],
                    ["❓ Help", "ℹ️ About"]
                ]
                send_reply_keyboard(chat_id, welcome_msg, buttons)
            
            elif text == '/help':
                help_text = """
📖 *Help Guide*

*Commands:*
/start - Start the bot
/menu - Show main menu
/topics - Show all subjects
/daily - Daily quiz
/leaderboard - Top scores
/mystats - Your progress
/help - This message

*During Quiz:*
Send A, B, C, or D to answer
Send SKIP to skip question
Send QUIT to quit quiz
"""
                send_message(chat_id, help_text)
            
            elif text == '❓ Help':
                help_text = """
📖 *Help Guide*

*Commands:*
/start - Start the bot
/menu - Show main menu
/topics - Show all subjects
/daily - Daily quiz
/leaderboard - Top scores
/mystats - Your progress
"""
                send_message(chat_id, help_text)
            
            elif text == 'ℹ️ About':
                about_text = f"""
ℹ️ *About {BOT_NAME}*

Version: {BOT_VERSION}
Educational Quiz Bot for Students

6 Subjects with chapter-wise quizzes
Daily quiz challenges
Leaderboard competition
Progress tracking

Made with ❤️ for learners!
"""
                send_message(chat_id, about_text)
            
            elif text == '📊 My Stats':
                user_data = load_user(user_id)
                stats_text = f"""
📊 *Your Statistics*

Total Quizzes: {user_data.get('total_quizzes', 0)}
Total Correct: {user_data.get('total_correct', 0)}
Accuracy: {user_data.get('accuracy', 0)}%
Level: {user_data.get('level', 1)}
"""
                send_message(chat_id, stats_text)
            
            else:
                # Handle topic selection
                topic_map = {
                    "📚 Mathematics": "maths",
                    "🔬 Science": "science",
                    "📖 English Grammar": "english",
                    "🧬 Biology": "biology",
                    "⚡ Physics": "physics",
                    "🌍 General Knowledge": "gk"
                }
                
                if text in topic_map:
                    send_message(chat_id, f"📚 *{text} Selected*\n\nComing soon! Questions are being added.")
                else:
                    send_message(chat_id, "❌ I didn't understand that.\nType /menu to see options.")
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/')
def home():
    return f"🤖 {BOT_NAME} v{BOT_VERSION} is running on PythonAnywhere!"

# ============================================
# SET WEBHOOK
# ============================================

def set_webhook():
    """Set webhook for Telegram bot"""
    import requests
    
    # Get your PythonAnywhere URL
    # Replace 'yourusername' with your actual PythonAnywhere username
    webhook_url = "https://yourusername.pythonanywhere.com/webhook"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    params = {'url': webhook_url}
    
    response = requests.post(url, json=params)
    print(f"Webhook set response: {response.json()}")

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print(f"🚀 {BOT_NAME} v{BOT_VERSION} starting...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print("✅ Bot is ready!")
    
    # Set webhook when starting
    set_webhook()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8000)
