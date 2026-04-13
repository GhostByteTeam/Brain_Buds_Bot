import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify

# ============================================
# CONFIGURATION
# ============================================

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8639340465:AAE7NqxjSTPUxgTGyRxCr2BGqrPQa0xdoaI')
OWNER_ID = int(os.environ.get('OWNER_ID', '7653416743'))
BOT_NAME = "Brain Buds"
BOT_VERSION = "1.0.0"

# ============================================
# FLASK APP FOR VERCEL
# ============================================

app = Flask(__name__)

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
        
        if not update or 'message' not in update:
            return jsonify({'status': 'ok'})
        
        message = update['message']
        chat_id = message['chat']['id']
        user_name = message['from'].get('first_name', 'User')
        text = message.get('text', '')
        
        # Handle commands
        if text == '/start':
            welcome_msg = f"🧠 *Welcome to {BOT_NAME}, {user_name}!* 🌱\n\n"
            welcome_msg += "Your Quiz Bot is ready!\n\n"
            welcome_msg += "Send /menu to see options"
            send_message(chat_id, welcome_msg)
        
        elif text == '/menu':
            welcome_msg = f"🧠 *Welcome back, {user_name}!* 🌱\n\nSelect a topic:"
            buttons = [
                ["📚 Mathematics", "🔬 Science"],
                ["📖 English Grammar", "🧬 Biology"],
                ["⚡ Physics", "🌍 General Knowledge"],
                ["📊 My Stats", "🏆 Leaderboard"],
                ["❓ Help"]
            ]
            send_reply_keyboard(chat_id, welcome_msg, buttons)
        
        elif text == '/help':
            help_text = """
📖 *Help Guide*

*Commands:*
/start - Start the bot
/menu - Show main menu
/help - This message

*Topics Available:*
📚 Mathematics
🔬 Science
📖 English Grammar
🧬 Biology
⚡ Physics
🌍 General Knowledge
"""
            send_message(chat_id, help_text)
        
        elif text == '❓ Help':
            help_text = "Send /help for commands list"
            send_message(chat_id, help_text)
        
        elif text == '📚 Mathematics':
            send_message(chat_id, "📚 *Mathematics*\n\nComing soon! Questions are being added.")
        
        elif text == '🔬 Science':
            send_message(chat_id, "🔬 *Science*\n\nComing soon! Questions are being added.")
        
        elif text == '📖 English Grammar':
            send_message(chat_id, "📖 *English Grammar*\n\nComing soon! Questions are being added.")
        
        elif text == '🧬 Biology':
            send_message(chat_id, "🧬 *Biology*\n\nComing soon! Questions are being added.")
        
        elif text == '⚡ Physics':
            send_message(chat_id, "⚡ *Physics*\n\nComing soon! Questions are being added.")
        
        elif text == '🌍 General Knowledge':
            send_message(chat_id, "🌍 *General Knowledge*\n\nComing soon! Questions are being added.")
        
        elif text == '📊 My Stats':
            send_message(chat_id, "📊 *Your Stats*\n\nNo quizzes taken yet.\nTake a quiz to see stats!")
        
        elif text == '🏆 Leaderboard':
            send_message(chat_id, "🏆 *Leaderboard*\n\nNo data available yet.\nTake quizzes to appear on leaderboard!")
        
        else:
            send_message(chat_id, f"❌ I didn't understand '{text}'\n\nType /menu to see options")
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return f"🤖 {BOT_NAME} v{BOT_VERSION} is running on Vercel!"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return "OK", 200

# ============================================
# VERCEL SERVERLESS HANDLER
# ============================================

# This is the entry point for Vercel
handler = app
