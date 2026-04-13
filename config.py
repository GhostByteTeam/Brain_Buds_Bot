import os

# ============================================
# BRAIN BUDS BOT - CONFIGURATION FILE
# ============================================

# --------------------------------------------
# BOT SETTINGS
# --------------------------------------------
BOT_TOKEN = "8639340465:AAE7NqxjSTPUxgTGyRxCr2BGqrPQa0xdoaI"
BOT_NAME = "Brain Buds"
BOT_USERNAME = "@BrainBudsBot"
BOT_VERSION = "1.0.0"

# --------------------------------------------
# OWNER / ADMIN SETTINGS
# Sirf owner hi admin panel access kar sakta hai
# --------------------------------------------
OWNER_ID = 7653416743  # Apna Telegram ID yahan daalein
ADMIN_IDS = [7653416743]  # Sirf owner ka ID, koi aur nahi

# --------------------------------------------
# TOPICS CONFIGURATION
# --------------------------------------------
TOPICS = {
    "maths": {
        "name": "Mathematics",
        "emoji": "📚",
        "icon": "🔢"
    },
    "science": {
        "name": "Science",
        "emoji": "🔬",
        "icon": "🧪"
    },
    "english": {
        "name": "English Grammar",
        "emoji": "📖",
        "icon": "✏️"
    },
    "biology": {
        "name": "Biology",
        "emoji": "🧬",
        "icon": "🔬"
    },
    "physics": {
        "name": "Physics",
        "emoji": "⚡",
        "icon": "🎯"
    },
    "gk": {
        "name": "General Knowledge",
        "emoji": "🌍",
        "icon": "🏆"
    }
}

# Topic list order (jis order mein dikhega)
TOPIC_ORDER = ["maths", "science", "english", "biology", "physics", "gk"]

# --------------------------------------------
# QUIZ TYPES
# --------------------------------------------
QUIZ_TYPES = {
    "quick": {
        "name": "Quick Quiz",
        "questions": 5,
        "time_limit": 60,
        "description": "5 questions, 1 minute"
    },
    "full": {
        "name": "Full Test",
        "questions": 20,
        "time_limit": 600,
        "description": "20 questions, 10 minutes"
    },
    "practice": {
        "name": "Practice Mode",
        "questions": 10,
        "time_limit": None,
        "description": "No time limit, learn at your pace"
    },
    "exam": {
        "name": "Exam Mode",
        "questions": 15,
        "time_limit": 300,
        "description": "15 questions, 5 minutes, negative marking"
    }
}

# --------------------------------------------
# SCORING SYSTEM
# --------------------------------------------
SCORES = {
    "correct": 10,
    "wrong": 0,
    "negative_exam": -2,
    "skip": 0,
    "streak_bonus": 5,
    "time_bonus": 2,
    "completion_bonus": 10
}

# --------------------------------------------
# GRADES (Percentage wise)
# --------------------------------------------
GRADES = {
    "A+": {"min": 90, "max": 100, "emoji": "🏆", "message": "Excellent! You're a genius!"},
    "A": {"min": 80, "max": 89, "emoji": "⭐", "message": "Very Good! Keep it up!"},
    "B+": {"min": 70, "max": 79, "emoji": "👍", "message": "Good! Practice more!"},
    "B": {"min": 60, "max": 69, "emoji": "📚", "message": "Fair! Need improvement"},
    "C": {"min": 50, "max": 59, "emoji": "⚠️", "message": "Average! Work harder"},
    "D": {"min": 0, "max": 49, "emoji": "❌", "message": "Need serious practice"}
}

# --------------------------------------------
# FILE PATHS
# --------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
QUESTIONS_DIR = os.path.join(DATA_DIR, "questions")
CHAPTERS_DIR = os.path.join(DATA_DIR, "chapters")
USERS_DIR = os.path.join(DATA_DIR, "users")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
UTILS_DIR = os.path.join(BASE_DIR, "utils")

# JSON Files
DAILY_QUIZ_FILE = os.path.join(DATA_DIR, "daily_quiz.json")
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
BROADCAST_LOG_FILE = os.path.join(DATA_DIR, "broadcast_log.json")

# --------------------------------------------
# QUIZ DEFAULTS
# --------------------------------------------
DEFAULT_QUESTIONS_PER_QUIZ = 10
DEFAULT_TIME_PER_QUESTION = 30
MAX_QUESTIONS_PER_TOPIC = 500
MIN_QUESTIONS_FOR_QUIZ = 5

# --------------------------------------------
# REMINDER SETTINGS
# --------------------------------------------
REMINDER_TIME = "09:00"  # 9 AM daily
REMINDER_ENABLED = True

# --------------------------------------------
# BUTTON LABELS
# --------------------------------------------
BUTTONS = {
    "main_menu": "🏠 Main Menu",
    "back": "◀️ Back",
    "next": "Next ▶️",
    "skip": "⏭️ Skip",
    "quit": "❌ Quit",
    "leaderboard": "🏆 Leaderboard",
    "my_stats": "📊 My Stats",
    "daily_quiz": "📅 Daily Quiz",
    "help": "❓ Help",
    "about": "ℹ️ About"
}

# --------------------------------------------
# MESSAGES (will be loaded from assets)
# --------------------------------------------
# These are fallback messages if asset files not found

WELCOME_MESSAGE_FALLBACK = """
🧠 WELCOME TO BRAIN BUDS! 🌱

Your personal quiz bot to test your knowledge!

📚 Available Topics:
• Mathematics
• Science
• English Grammar
• Biology
• Physics
• General Knowledge

✨ Features:
• Chapter-wise quizzes
• Multiple quiz modes
• Daily quiz challenge
• Leaderboard
• Detailed results

Type /menu to start!
"""

HELP_MESSAGE_FALLBACK = """
📖 BRAIN BUDS - Help Guide

🎮 Commands:
/start - Start the bot
/menu - Show main menu
/topics - Show all topics
/daily - Daily quiz
/leaderboard - Top scores
/mystats - Your progress
/help - This message
/about - About bot

📝 During Quiz:
/ans A - Answer option A
/ans B - Answer option B
/ans C - Answer option C
/ans D - Answer option D
/skip - Skip current question
/quit - Quit quiz

🏆 Scoring:
• Correct: +10 points
• Wrong: 0 points (-2 in exam mode)
• Streak bonus: +5
• Time bonus: +2
• Completion: +10

Good luck! 🍀
"""

ABOUT_MESSAGE_FALLBACK = """
ℹ️ ABOUT BRAIN BUDS

Version: 1.0.0
Created for students to practice and improve knowledge.

✨ Features:
• 6+ subjects with chapters
• 4 quiz modes
• Daily quiz challenge
• Detailed performance analysis
• Leaderboard competition

Made with ❤️ for learners everywhere!

Contact: @BrainBudsSupport
"""

# --------------------------------------------
# CREATE DIRECTORIES FUNCTION
# --------------------------------------------
def create_directories():
    """Create all necessary directories if they don't exist"""
    directories = [
        DATA_DIR,
        QUESTIONS_DIR,
        CHAPTERS_DIR,
        USERS_DIR,
        SESSIONS_DIR,
        ASSETS_DIR,
        UTILS_DIR
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    print("All directories are ready!")

# Run directory creation when config is imported
create_directories()