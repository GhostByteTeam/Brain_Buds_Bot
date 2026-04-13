import json
import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify

# ============================================
# CONFIGURATION
# ============================================

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8639340465:AAE7NqxjSTPUxgTGyRxCr2BGqrPQa0xdoaI')
OWNER_ID = int(os.environ.get('OWNER_ID', '7653416743'))
BOT_NAME = "Brain Buds"
BOT_VERSION = "1.0.0"

# Admin IDs list (sirf owner)
ADMIN_IDS = [OWNER_ID]

# ============================================
# FLASK APP
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

def send_inline_keyboard(chat_id, text, buttons):
    """Send message with inline keyboard"""
    markup = {
        'inline_keyboard': buttons
    }
    return send_message(chat_id, text, markup)

# ============================================
# ADMIN PANEL FUNCTIONS
# ============================================

def is_admin(user_id):
    """Check if user is admin/owner"""
    return user_id in ADMIN_IDS

def show_admin_panel(chat_id):
    """Show admin panel to owner"""
    text = """
👑 *ADMIN CONTROL PANEL*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Bot Statistics*
📚 *Manage Questions*
📅 *Daily Quiz*
📢 *Broadcast*
👥 *User Management*
⚙️ *Bot Settings*
📤 *Export Data*

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 *Click on any option below*
"""
    
    buttons = [
        [
            {"text": "📊 Bot Stats", "callback_data": "admin_stats"},
            {"text": "📚 Add Question", "callback_data": "admin_add"}
        ],
        [
            {"text": "📅 Set Daily Quiz", "callback_data": "admin_daily"},
            {"text": "📢 Broadcast", "callback_data": "admin_broadcast"}
        ],
        [
            {"text": "👥 Users List", "callback_data": "admin_users"},
            {"text": "⚙️ Settings", "callback_data": "admin_settings"}
        ],
        [
            {"text": "❌ Close", "callback_data": "admin_close"}
        ]
    ]
    
    return send_inline_keyboard(chat_id, text, buttons)

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
        
        # Handle Callback Query (Inline Button Clicks)
        if 'callback_query' in update:
            callback = update['callback_query']
            chat_id = callback['message']['chat']['id']
            user_id = callback['from']['id']
            data = callback['data']
            
            # Answer callback query
            import requests
            answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
            requests.post(answer_url, json={'callback_query_id': callback['id']})
            
            # Handle admin callbacks
            if data == 'admin_stats':
                send_message(chat_id, "📊 *Bot Statistics*\n\nTotal Users: 0\nTotal Questions: 0\nBot Active: ✅", parse_mode='Markdown')
            elif data == 'admin_add':
                send_message(chat_id, "➕ *Add Question*\n\nSend question in format:\n`Q|OptA|OptB|OptC|OptD|Correct|Explanation`\n\nExample:\n`What is 2+2?|3|4|5|6|B|Basic addition`", parse_mode='Markdown')
            elif data == 'admin_daily':
                send_message(chat_id, "📅 *Set Daily Quiz*\n\nSend topic name (maths/science/english/biology/physics/gk)")
            elif data == 'admin_broadcast':
                send_message(chat_id, "📢 *Broadcast*\n\nSend message to broadcast to all users:")
            elif data == 'admin_users':
                send_message(chat_id, "👥 *Users List*\n\nTotal users: 0\n\nNo users yet.")
            elif data == 'admin_settings':
                send_message(chat_id, "⚙️ *Bot Settings*\n\nMaintenance Mode: OFF\nDaily Quiz: ENABLED")
            elif data == 'admin_close':
                send_message(chat_id, "❌ Admin panel closed.")
            
            return jsonify({'status': 'ok'})
        
        # Handle Regular Messages
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            user_name = message['from'].get('first_name', 'User')
            text = message.get('text', '')
            
            # ADMIN COMMAND - Only for owner
            if text == '/admin':
                if is_admin(user_id):
                    show_admin_panel(chat_id)
                else:
                    send_message(chat_id, "❌ Access Denied! You are not authorized to use admin commands.")
                return jsonify({'status': 'ok'})
            
            # Normal User Commands
            if text == '/start':
                welcome_msg = f"🧠 *Welcome to {BOT_NAME}, {user_name}!* 🌱\n\nYour Quiz Bot is ready!\n\nSend /menu to see options"
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
/admin - Admin panel (owner only)
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
                send_message(chat_id, "Send /help for commands list")
            
            elif text == 'ℹ️ About':
                about_text = f"""
ℹ️ *About {BOT_NAME}*

Version: {BOT_VERSION}
Educational Quiz Bot for Students

6 Subjects with chapter-wise quizzes
Daily quiz challenges
Leaderboard competition

Made with ❤️ for learners!
"""
                send_message(chat_id, about_text)
            
            elif text in ["📚 Mathematics", "🔬 Science", "📖 English Grammar", "🧬 Biology", "⚡ Physics", "🌍 General Knowledge"]:
                send_message(chat_id, f"📚 *{text}*\n\nComing soon! Questions are being added.\n\nUse /admin to add questions (owner only).")
            
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
    return f"🤖 {BOT_NAME} v{BOT_VERSION} is running on Vercel!"

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200

# ============================================
# VERCEL SERVERLESS HANDLER
# ============================================

handler = app
