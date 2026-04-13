import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import threading
import time
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (
    BOT_TOKEN, BOT_NAME, BOT_VERSION, OWNER_ID, ADMIN_IDS,
    TOPICS, TOPIC_ORDER, WELCOME_MESSAGE_FALLBACK, HELP_MESSAGE_FALLBACK,
    ABOUT_MESSAGE_FALLBACK, REMINDER_TIME, REMINDER_ENABLED
)
from database import (
    load_user, save_user, get_all_users, get_total_users_count,
    load_settings, save_settings, update_leaderboard
)
from decorators import admin_only, rate_limit, bot_active_only, log_command, handle_errors
from buttons import get_main_menu_keyboard, get_back_button
import main_menu
import topics_handler
import quiz_engine
import result_handler
import admin_panel
import broadcast_system
import leaderboard
import stats_tracker
import reminder_system

# ============================================
# INITIALIZE BOT
# ============================================

# Check if BOT_TOKEN is configured
if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("❌ ERROR: Please set your BOT_TOKEN in config.py")
    print("📝 Get your token from @BotFather on Telegram")
    sys.exit(1)

if OWNER_ID == 123456789:
    print("⚠️ WARNING: Using default OWNER_ID. Please update with your Telegram ID")
    print("📝 Get your ID from @userinfobot on Telegram")

bot = telebot.TeleBot(BOT_TOKEN)
print(f"🤖 {BOT_NAME} v{BOT_VERSION} is starting...")
print(f"📊 Bot Token: {BOT_TOKEN[:15]}...")
print(f"👑 Owner ID: {OWNER_ID}")
print(f"✅ Bot is ready!")

# Store user states for multi-step operations
user_states = {}

# Store active quizzes (will be populated from quiz_engine)
active_quizzes = {}

# ============================================
# COMMAND HANDLERS
# ============================================

@bot.message_handler(commands=['start'])
@handle_errors
@log_command
@bot_active_only
def start_command(message):
    """Handle /start command"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username or "no_username"
    
    # Load or create user data
    user_data = load_user(user_id)
    
    # Update user info if new
    if not user_data.get("first_name"):
        user_data["first_name"] = user_name
        user_data["username"] = username
        user_data["joined_date"] = datetime.now().isoformat()
        save_user(user_id, user_data)
        print(f"📝 New user joined: {user_name} (@{username})")
    
    # Load welcome message from asset file
    welcome_text = WELCOME_MESSAGE_FALLBACK
    try:
        from utils.helpers import read_text_file
        asset_welcome = read_text_file(os.path.join("assets", "welcome_text.txt"))
        if asset_welcome:
            welcome_text = asset_welcome
    except Exception as e:
        print(f"Could not load asset file: {e}")
    
    # Send welcome message with menu
    welcome_msg = f"🧠 *Welcome to {BOT_NAME}, {user_name}!* 🌱\n\n{welcome_text}"
    
    try:
        bot.reply_to(
            message, 
            welcome_msg, 
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        # If Markdown fails, send without formatting
        bot.reply_to(
            message, 
            f"Welcome to {BOT_NAME}, {user_name}!\n\n{welcome_text}",
            reply_markup=get_main_menu_keyboard()
        )

@bot.message_handler(commands=['menu'])
@handle_errors
@log_command
@bot_active_only
def menu_command(message):
    """Handle /menu command - Show main menu"""
    main_menu.show_main_menu(bot, message)

@bot.message_handler(commands=['topics'])
@handle_errors
@log_command
@bot_active_only
def topics_command(message):
    """Handle /topics command - Show all topics"""
    topics_handler.show_topics(bot, message)

@bot.message_handler(commands=['daily'])
@handle_errors
@log_command
@bot_active_only
def daily_command(message):
    """Handle /daily command - Daily quiz"""
    quiz_engine.start_daily_quiz(bot, message)

@bot.message_handler(commands=['leaderboard'])
@handle_errors
@log_command
@bot_active_only
def leaderboard_command(message):
    """Handle /leaderboard command"""
    leaderboard.show_leaderboard(bot, message)

@bot.message_handler(commands=['mystats'])
@handle_errors
@log_command
@bot_active_only
def mystats_command(message):
    """Handle /mystats command"""
    stats_tracker.show_user_stats(bot, message)

@bot.message_handler(commands=['help'])
@handle_errors
@log_command
def help_command(message):
    """Handle /help command"""
    help_text = HELP_MESSAGE_FALLBACK
    
    try:
        from utils.helpers import read_text_file
        asset_help = read_text_file(os.path.join("assets", "help_text.txt"))
        if asset_help:
            help_text = asset_help
    except Exception as e:
        print(f"Could not load help asset: {e}")
    
    try:
        bot.reply_to(message, help_text, parse_mode='Markdown', reply_markup=get_back_button())
    except:
        bot.reply_to(message, help_text, reply_markup=get_back_button())

@bot.message_handler(commands=['about'])
@handle_errors
@log_command
def about_command(message):
    """Handle /about command"""
    about_text = ABOUT_MESSAGE_FALLBACK
    
    try:
        from utils.helpers import read_text_file
        asset_about = read_text_file(os.path.join("assets", "about_text.txt"))
        if asset_about:
            about_text = asset_about
    except Exception as e:
        print(f"Could not load about asset: {e}")
    
    try:
        bot.reply_to(message, about_text, parse_mode='Markdown', reply_markup=get_back_button())
    except:
        bot.reply_to(message, about_text, reply_markup=get_back_button())

@bot.message_handler(commands=['quit'])
@handle_errors
@log_command
def quit_command(message):
    """Handle /quit command - Quit current quiz"""
    user_id = message.from_user.id
    
    from database import delete_session
    
    # Check in quiz_engine active_quizzes
    session = None
    if hasattr(quiz_engine, 'active_quizzes'):
        session = quiz_engine.active_quizzes.get(user_id)
    
    if session:
        delete_session(user_id)
        if user_id in quiz_engine.active_quizzes:
            del quiz_engine.active_quizzes[user_id]
        bot.reply_to(message, "❌ Quiz cancelled!\n\nType /menu to start a new quiz.", reply_markup=get_main_menu_keyboard())
    else:
        bot.reply_to(message, "❌ No active quiz to quit.", reply_markup=get_main_menu_keyboard())

# ============================================
# QUIZ ANSWER HANDLERS
# ============================================

@bot.message_handler(commands=['ans'])
@handle_errors
@log_command
@bot_active_only
def answer_command(message):
    """Handle /ans command - Answer quiz question"""
    quiz_engine.handle_answer(bot, message)

@bot.message_handler(commands=['skip'])
@handle_errors
@log_command
@bot_active_only
def skip_command(message):
    """Handle /skip command - Skip current question"""
    quiz_engine.handle_skip(bot, message)

# ============================================
# TEXT MESSAGE HANDLERS (For buttons)
# ============================================

@bot.message_handler(func=lambda message: message.text == "◀️ Back to Menu")
@handle_errors
def back_to_menu_handler(message):
    """Handle back button"""
    main_menu.show_main_menu(bot, message)

@bot.message_handler(func=lambda message: message.text == "📚 Mathematics")
@handle_errors
def maths_handler(message):
    """Handle Maths topic selection"""
    topics_handler.select_topic(bot, message, "maths")

@bot.message_handler(func=lambda message: message.text == "🔬 Science")
@handle_errors
def science_handler(message):
    """Handle Science topic selection"""
    topics_handler.select_topic(bot, message, "science")

@bot.message_handler(func=lambda message: message.text == "📖 English Grammar")
@handle_errors
def english_handler(message):
    """Handle English topic selection"""
    topics_handler.select_topic(bot, message, "english")

@bot.message_handler(func=lambda message: message.text == "🧬 Biology")
@handle_errors
def biology_handler(message):
    """Handle Biology topic selection"""
    topics_handler.select_topic(bot, message, "biology")

@bot.message_handler(func=lambda message: message.text == "⚡ Physics")
@handle_errors
def physics_handler(message):
    """Handle Physics topic selection"""
    topics_handler.select_topic(bot, message, "physics")

@bot.message_handler(func=lambda message: message.text == "🌍 General Knowledge")
@handle_errors
def gk_handler(message):
    """Handle GK topic selection"""
    topics_handler.select_topic(bot, message, "gk")

@bot.message_handler(func=lambda message: message.text == "📅 Daily Quiz")
@handle_errors
def daily_quiz_handler(message):
    """Handle Daily Quiz button"""
    quiz_engine.start_daily_quiz(bot, message)

@bot.message_handler(func=lambda message: message.text == "🏆 Leaderboard")
@handle_errors
def leaderboard_button_handler(message):
    """Handle Leaderboard button"""
    leaderboard.show_leaderboard(bot, message)

@bot.message_handler(func=lambda message: message.text == "📊 My Stats")
@handle_errors
def mystats_button_handler(message):
    """Handle My Stats button"""
    stats_tracker.show_user_stats(bot, message)

@bot.message_handler(func=lambda message: message.text == "❓ Help")
@handle_errors
def help_button_handler(message):
    """Handle Help button"""
    help_command(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ About")
@handle_errors
def about_button_handler(message):
    """Handle About button"""
    about_command(message)

# ============================================
# ADMIN COMMANDS (Owner Only)
# ============================================

@bot.message_handler(commands=['admin'])
@admin_only
@handle_errors
@log_command
def admin_panel_command(message):
    """Handle /admin command - Show admin panel"""
    admin_panel.show_admin_panel(bot, message)

@bot.message_handler(commands=['broadcast'])
@admin_only
@handle_errors
@log_command
def broadcast_command(message):
    """Handle /broadcast command - Send broadcast"""
    broadcast_system.start_broadcast(bot, message)

@bot.message_handler(commands=['stats'])
@admin_only
@handle_errors
@log_command
def stats_command(message):
    """Handle /stats command - Show bot statistics"""
    admin_panel.show_bot_stats(bot, message)

@bot.message_handler(commands=['users'])
@admin_only
@handle_errors
@log_command
def users_command(message):
    """Handle /users command - List all users"""
    admin_panel.list_users(bot, message)

@bot.message_handler(commands=['addquiz'])
@admin_only
@handle_errors
@log_command
def add_quiz_command(message):
    """Handle /addquiz command - Add new question"""
    admin_panel.start_add_question(bot, message)

@bot.message_handler(commands=['setdaily'])
@admin_only
@handle_errors
@log_command
def set_daily_command(message):
    """Handle /setdaily command - Set daily quiz"""
    admin_panel.set_daily_quiz(bot, message)

# ============================================
# CALLBACK QUERY HANDLERS (Inline Buttons)
# ============================================

@bot.callback_query_handler(func=lambda call: True)
@handle_errors
def callback_handler(call):
    """Handle all callback queries from inline buttons"""
    
    # Topic selection
    if call.data.startswith("topic_"):
        topic = call.data.replace("topic_", "")
        topics_handler.show_chapters(bot, call, topic)
    
    # Chapter selection
    elif call.data.startswith("chapter_"):
        parts = call.data.split("_")
        if len(parts) >= 3:
            topic = parts[1]
            chapter_id = int(parts[2])
            topics_handler.show_quiz_options(bot, call, topic, chapter_id)
    
    # Quiz mode selection
    elif call.data.startswith("quiz_"):
        parts = call.data.split("_")
        if len(parts) >= 4:
            topic = parts[1]
            chapter_id = int(parts[2])
            quiz_type = parts[3]
            quiz_engine.start_quiz(bot, call, topic, chapter_id, quiz_type)
    
    # Answer selection during quiz
    elif call.data.startswith("ans_"):
        answer = call.data.replace("ans_", "")
        quiz_engine.handle_inline_answer(bot, call, answer)
    
    # Back to topics
    elif call.data == "back_to_topics":
        topics_handler.show_topics(bot, call.message)
    
    # Main menu
    elif call.data == "main_menu":
        main_menu.show_main_menu(bot, call.message)
    
    # Leaderboard views
    elif call.data.startswith("leaderboard_"):
        topic = call.data.replace("leaderboard_", "")
        leaderboard.show_topic_leaderboard(bot, call, topic)
    
    elif call.data == "view_leaderboard":
        leaderboard.show_leaderboard(bot, call.message)
    
    elif call.data == "view_mystats":
        stats_tracker.show_user_stats(bot, call.message)
    
    # Retest (wrong answers only)
    elif call.data.startswith("retest_"):
        parts = call.data.split("_")
        if len(parts) >= 3:
            topic = parts[1]
            chapter_id = int(parts[2])
            quiz_engine.start_retest(bot, call, topic, chapter_id)
    
    # Admin panel callbacks
    elif call.data.startswith("admin_"):
        admin_panel.handle_admin_callback(bot, call)
    
    # Settings
    elif call.data.startswith("settings_"):
        stats_tracker.handle_settings_callback(bot, call)
    
    # Daily quiz
    elif call.data == "start_daily_quiz":
        quiz_engine.start_daily_quiz(bot, call.message)
    
    # Cancel
    elif call.data == "cancel":
        try:
            bot.edit_message_text(
                "❌ Operation cancelled.",
                call.message.chat.id,
                call.message.message_id
            )
        except:
            pass
    
    # Default
    else:
        bot.answer_callback_query(call.id, "Processing...")

# ============================================
# REMINDER THREAD
# ============================================

def reminder_thread():
    """Background thread for daily reminders"""
    while True:
        try:
            if REMINDER_ENABLED:
                reminder_system.check_and_send_reminders(bot)
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"Reminder thread error: {e}")
            time.sleep(60)

# Start reminder thread
if REMINDER_ENABLED:
    reminder_thread_obj = threading.Thread(target=reminder_thread, daemon=True)
    reminder_thread_obj.start()
    print("⏰ Reminder thread started")

# ============================================
# UPDATE LEADERBOARD THREAD
# ============================================

def leaderboard_update_thread():
    """Background thread to update leaderboard periodically"""
    while True:
        try:
            time.sleep(3600)  # Update every hour
            update_leaderboard()
            print("📊 Leaderboard updated")
        except Exception as e:
            print(f"Leaderboard update error: {e}")
            time.sleep(3600)

# Start leaderboard update thread
leaderboard_thread_obj = threading.Thread(target=leaderboard_update_thread, daemon=True)
leaderboard_thread_obj.start()
print("📊 Leaderboard update thread started")

# ============================================
# ERROR HANDLER FOR ALL MESSAGES
# ============================================

@bot.message_handler(func=lambda message: True)
@handle_errors
def default_handler(message):
    """Handle any other message not captured by specific handlers"""
    bot.reply_to(
        message,
        "❌ I didn't understand that.\n\n"
        "Type /menu to see available options or /help for commands.",
        reply_markup=get_main_menu_keyboard()
    )

# ============================================
# START BOT
# ============================================

def main():
    """Main function to start the bot"""
    print("\n" + "="*50)
    print(f"🚀 {BOT_NAME} v{BOT_VERSION} is running!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"📊 Total users so far: {get_total_users_count()}")
    print("="*50 + "\n")
    
    try:
        print("🟢 Bot is polling for messages...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ============================================
# WEB SERVER FOR CYCLIC (Keep bot alive)
# ============================================

from flask import Flask, request
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Brain Buds Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# Start web server in background thread
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()
print("🌐 Web server started on port 8080")

if __name__ == "__main__":
    main()
