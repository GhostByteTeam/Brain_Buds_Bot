import time
from datetime import datetime
import threading
from config import REMINDER_TIME, REMINDER_ENABLED, BOT_NAME
from database import load_user, get_all_users, load_settings
from utils.time_utils import get_current_time_string, parse_time_string

# ============================================
# REMINDER SYSTEM - Daily Quiz Reminders
# ============================================

# Store last reminder date to avoid duplicate reminders
last_reminder_date = {}

def check_and_send_reminders(bot):
    """Check if it's time to send reminders and send them"""
    global last_reminder_date
    
    if not REMINDER_ENABLED:
        return
    
    current_time = get_current_time_string()
    reminder_time = REMINDER_TIME
    
    # Check if current time matches reminder time (within 5 minutes)
    if is_time_to_remind(reminder_time, current_time):
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if already sent today
        if last_reminder_date.get('date') == today:
            return
        
        # Send reminders to all users
        send_daily_reminders(bot)
        
        # Update last reminder date
        last_reminder_date['date'] = today
        print(f"📅 Daily reminders sent at {current_time}")

def is_time_to_remind(reminder_time_str, current_time_str):
    """Check if current time is within reminder window"""
    try:
        reminder_parts = reminder_time_str.split(':')
        current_parts = current_time_str.split(':')
        
        reminder_minutes = int(reminder_parts[0]) * 60 + int(reminder_parts[1])
        current_minutes = int(current_parts[0]) * 60 + int(current_parts[1])
        
        # Allow 5 minute window
        return abs(current_minutes - reminder_minutes) <= 5
        
    except:
        return False

def send_daily_reminders(bot):
    """Send daily quiz reminders to all users"""
    all_users = get_all_users()
    settings = load_settings()
    
    if not settings.get('daily_quiz_enabled', True):
        return
    
    reminder_text = build_reminder_message()
    
    success_count = 0
    total_count = len(all_users)
    
    for user_id in all_users:
        try:
            # Check if user has notifications enabled
            user_data = load_user(user_id)
            user_settings = user_data.get('settings', {})
            
            if user_settings.get('notifications', True):
                bot.send_message(
                    user_id,
                    reminder_text,
                    parse_mode='Markdown'
                )
                success_count += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.05)
            
        except Exception as e:
            print(f"Failed to send reminder to {user_id}: {e}")
    
    print(f"📨 Reminders sent: {success_count}/{total_count} users")

def build_reminder_message():
    """Build the reminder message text"""
    today = datetime.now().strftime("%A")
    
    message = f"""
🌅 *Good Morning!* 🌅

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*{BOT_NAME} Daily Quiz Reminder*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 *Day:* {today}
🎯 *Challenge:* Complete today's daily quiz!

━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ *Benefits of playing daily:*
• Build your streak 🔥
• Earn bonus points ⭐
• Unlock achievements 🏆
• Improve your rank 📈

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*👉 Type /daily to start your quiz!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *Tip:* Just 5 minutes a day makes a big difference!
"""
    return message

def send_streak_reminder(bot, user_id, streak_count):
    """Send streak reminder to a specific user"""
    if streak_count <= 0:
        return
    
    message = f"""
🔥 *Streak Alert!* 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━━
You're on a *{streak_count} day streak!*

{get_streak_encouragement(streak_count)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Don't break your streak today!

👉 *Type /daily to keep it going!*
"""
    
    try:
        bot.send_message(user_id, message, parse_mode='Markdown')
    except:
        pass

def get_streak_encouragement(streak_count):
    """Get encouragement message based on streak length"""
    if streak_count >= 30:
        return "🌟 *AMAZING!* 🌟\nYou're a legend! Keep this incredible momentum going!"
    elif streak_count >= 14:
        return "🎯 *FANTASTIC!* 🎯\nTwo weeks strong! You're building an awesome habit!"
    elif streak_count >= 7:
        return "🔥 *WEEK WARRIOR!* 🔥\nOne week done! You're on fire! Keep it up!"
    elif streak_count >= 3:
        return "👍 *GREAT START!* 👍\nYou're building momentum! Don't stop now!"
    else:
        return "💪 *KEEP GOING!* 💪\nEvery day counts! You've got this!"

def schedule_reminders(bot):
    """Background thread to schedule reminders"""
    while True:
        try:
            check_and_send_reminders(bot)
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"Reminder scheduler error: {e}")
            time.sleep(60)

def start_reminder_scheduler(bot):
    """Start the reminder scheduler in background"""
    reminder_thread = threading.Thread(target=schedule_reminders, args=(bot,), daemon=True)
    reminder_thread.start()
    print("⏰ Reminder scheduler started")

def send_test_reminder(bot, user_id):
    """Send a test reminder (for admin use)"""
    message = """
🔔 *TEST REMINDER*

This is a test message from the reminder system.

If you received this, reminders are working correctly!

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👉 *Type /daily to take today's quiz!*
"""
    
    try:
        bot.send_message(user_id, message, parse_mode='Markdown')
        return True
    except:
        return False

def get_reminder_status():
    """Get current reminder system status"""
    settings = load_settings()
    
    return {
        'enabled': REMINDER_ENABLED,
        'reminder_time': REMINDER_TIME,
        'daily_quiz_enabled': settings.get('daily_quiz_enabled', True),
        'last_reminder_date': last_reminder_date.get('date', 'Never')
    }

def toggle_reminders(enable=None):
    """Enable or disable reminders globally"""
    settings = load_settings()
    
    if enable is not None:
        settings['daily_quiz_enabled'] = enable
    else:
        settings['daily_quiz_enabled'] = not settings.get('daily_quiz_enabled', True)
    
    from database import save_settings
    save_settings(settings)
    
    return settings.get('daily_quiz_enabled', True)

def set_reminder_time(time_str):
    """Set custom reminder time"""
    if parse_time_string(time_str):
        # This would update the config (would need to be saved to settings)
        settings = load_settings()
        settings['reminder_time'] = time_str
        from database import save_settings
        save_settings(settings)
        return True
    return False