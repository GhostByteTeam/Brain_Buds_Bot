from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import TOPICS, TOPIC_ORDER, BOT_NAME
from database import load_user
from buttons import get_main_menu_keyboard

# ============================================
# MAIN MENU HANDLER
# ============================================

def show_main_menu(bot, message):
    """Show the main menu with all options"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Load user data for personalized message
    user_data = load_user(user_id)
    
    # Get user stats for personalized greeting
    total_quizzes = user_data.get('total_quizzes', 0)
    current_streak = user_data.get('current_streak', 0)
    level = user_data.get('level', 1)
    
    # Create personalized greeting
    greeting = f"🧠 *Welcome back, {user_name}!* 🌱\n\n"
    
    if total_quizzes == 0:
        greeting += "You haven't taken any quizzes yet.\n"
        greeting += "Select a topic below to get started!\n\n"
    else:
        greeting += f"📊 *Your Stats:*\n"
        greeting += f"• Quizzes completed: {total_quizzes}\n"
        greeting += f"• Current streak: {current_streak} days 🔥\n"
        greeting += f"• Level: {level}\n\n"
    
    greeting += "*What would you like to do today?*\n"
    greeting += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Send menu with buttons
    bot.send_message(
        message.chat.id,
        greeting,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard()
    )

def show_topics_menu(bot, message):
    """Show topics selection menu"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    for topic_id in TOPIC_ORDER:
        topic_name = TOPICS[topic_id]["name"]
        topic_emoji = TOPICS[topic_id]["emoji"]
        markup.add(InlineKeyboardButton(
            f"{topic_emoji} {topic_name}",
            callback_data=f"topic_{topic_id}"
        ))
    
    markup.add(InlineKeyboardButton("◀️ Back to Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        "📚 *Select a Subject*\n\n"
        "Choose a topic to start your quiz journey!\n"
        "Each subject has multiple chapters and question banks.\n\n"
        "👇 *Tap on a subject to continue:*",
        message.chat.id,
        message.message_id if hasattr(message, 'message_id') else None,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_quick_actions(bot, message):
    """Show quick action buttons"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        KeyboardButton("📅 Daily Quiz"),
        KeyboardButton("🏆 Leaderboard"),
        KeyboardButton("📊 My Stats"),
        KeyboardButton("❓ Help"),
        KeyboardButton("◀️ Back to Menu")
    ]
    
    markup.add(*buttons)
    
    bot.send_message(
        message.chat.id,
        "⚡ *Quick Actions*\n\n"
        "Choose an option below:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_help_section(bot, message):
    """Show help section with categories"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    buttons = [
        InlineKeyboardButton("📖 Command Guide", callback_data="help_commands"),
        InlineKeyboardButton("🏆 Scoring System", callback_data="help_scoring"),
        InlineKeyboardButton("📚 Quiz Types", callback_data="help_quiztypes"),
        InlineKeyboardButton("❓ FAQ", callback_data="help_faq"),
        InlineKeyboardButton("◀️ Back to Menu", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    
    bot.edit_message_text(
        "❓ *Help Center*\n\n"
        "What would you like to know about?\n"
        "Select a topic below:",
        message.chat.id,
        message.message_id if hasattr(message, 'message_id') else None,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_help_commands(bot, message):
    """Show all available commands"""
    commands_text = """
📖 *Complete Command Guide*

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*🎮 Basic Commands*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

/start - Start the bot
/menu - Show main menu
/topics - Show all subjects
/help - Show this help
/about - About this bot

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*📚 Quiz Commands*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

/ans A - Answer option A
/ans B - Answer option B
/ans C - Answer option C
/ans D - Answer option D
/skip - Skip current question
/quit - Quit current quiz

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*📊 Progress Commands*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

/mystats - Your statistics
/leaderboard - Top scores
/daily - Daily quiz challenge

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*👑 Admin Commands (Owner Only)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

/admin - Admin panel
/broadcast - Send message to all
/stats - Bot statistics
/addquiz - Add new question
/setdaily - Set daily quiz

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *Tip:* Use /menu to see all options
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Help", callback_data="help_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        commands_text,
        message.chat.id,
        message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_help_scoring(bot, message):
    """Show scoring system explanation"""
    scoring_text = """
🏆 *Scoring System Explained*

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Points System*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Correct Answer : +10 points
❌ Wrong Answer  : 0 points
⚠️ Wrong (Exam)  : -2 points
⏭️ Skip         : 0 points

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Bonuses*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 3 Correct Streak : +5 points
⚡ Time Bonus       : +2 points
🎯 Quiz Completion  : +10 points

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Grading Scale*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

90-100% : A+ 🏆 Excellent!
80-89%  : A  ⭐ Very Good!
70-79%  : B+ 👍 Good!
60-69%  : B  📚 Fair
50-59%  : C  ⚠️ Average
0-49%   : D  ❌ Need Practice

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Example Calculation*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

10 Questions Quiz:
• 8 Correct  = 80 points
• 2 Wrong    = 0 points
• 1 Streak   = +5 points
• Completion = +10 points
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total = 95 points!
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Help", callback_data="help_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        scoring_text,
        message.chat.id,
        message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_help_quiztypes(bot, message):
    """Show quiz types explanation"""
    quiztypes_text = """
📚 *Quiz Types Explained*

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Quick Quiz* 📝
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 5 questions
• 1 minute time limit
• Best for quick revision
• +2 time bonus if early

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Full Test* 📖
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 20 questions
• 10 minute time limit
• Complete topic coverage
• Best for thorough practice

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Practice Mode* 🎯
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 10 questions
• No time limit
• Learn at your pace
• See answers after each question

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Exam Mode* ⚡
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 15 questions
• 5 minute time limit
• Negative marking (-2)
• Real exam simulation

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *Recommendation:*
Start with Practice Mode,
then try Quick Quiz,
then Full Test,
finally Exam Mode!
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Help", callback_data="help_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        quiztypes_text,
        message.chat.id,
        message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_help_faq(bot, message):
    """Show frequently asked questions"""
    faq_text = """
❓ *Frequently Asked Questions*

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: Can I retake a quiz?
A: Yes! You can take any quiz unlimited times.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: How do I see wrong answers?
A: After each quiz, result shows all wrong 
   answers with explanations.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: What is streak?
A: Playing daily quiz consecutively.
   Longer streak = more rewards!

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: How to increase my rank?
A: Play more quizzes, get correct answers,
   maintain daily streaks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: Bot not responding?
A: Type /start to restart or wait a few seconds.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: How to report a bug?
A: Contact @BrainBudsSupport

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: Can I add my own questions?
A: Only admin can add questions.
   Contact bot owner for requests.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *More Questions?*
Contact: @BrainBudsSupport
    """
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Help", callback_data="help_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        faq_text,
        message.chat.id,
        message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )