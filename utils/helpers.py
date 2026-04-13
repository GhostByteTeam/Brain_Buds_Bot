import random
import string
from datetime import datetime
import json
import os
import re

# ============================================
# HELPER FUNCTIONS - Common Utilities
# ============================================

# --------------------------------------------
# TEXT FORMATTING FUNCTIONS
# --------------------------------------------

def format_bold(text):
    """Format text as bold for Telegram"""
    return f"*{text}*"

def format_italic(text):
    """Format text as italic for Telegram"""
    return f"_{text}_"

def format_code(text):
    """Format text as code for Telegram"""
    return f"`{text}`"

def format_pre(text):
    """Format text as preformatted for Telegram"""
    return f"```\n{text}\n```"

def format_escape(text):
    """Escape special characters for Telegram Markdown"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def create_progress_bar(percentage, length=10):
    """Create a text-based progress bar"""
    filled = int(length * percentage / 100)
    empty = length - filled
    return "█" * filled + "░" * empty

def truncate_text(text, max_length=50):
    """Truncate text to max length"""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

# --------------------------------------------
# DATE TIME FUNCTIONS
# --------------------------------------------

def get_current_datetime():
    """Get current datetime as string (YYYY-MM-DD HH:MM:SS)"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_date():
    """Get current date as string (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    """Get current time as string (HH:MM:SS)"""
    return datetime.now().strftime("%H:%M:%S")

# --------------------------------------------
# GRADE AND SCORING FUNCTIONS
# --------------------------------------------

def get_grade(percentage):
    """Get grade based on percentage"""
    if percentage >= 90:
        return {"grade": "A+", "emoji": "🏆", "message": "Excellent! You're a genius!"}
    elif percentage >= 80:
        return {"grade": "A", "emoji": "⭐", "message": "Very Good! Keep it up!"}
    elif percentage >= 70:
        return {"grade": "B+", "emoji": "👍", "message": "Good! Practice more!"}
    elif percentage >= 60:
        return {"grade": "B", "emoji": "📚", "message": "Fair! Need improvement"}
    elif percentage >= 50:
        return {"grade": "C", "emoji": "⚠️", "message": "Average! Work harder"}
    else:
        return {"grade": "D", "emoji": "❌", "message": "Need serious practice"}

def format_time(seconds):
    """Format seconds to MM:SS"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)

def calculate_average(numbers):
    """Calculate average of a list"""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def get_rank_emoji(rank):
    """Get emoji for rank position"""
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return f"#{rank}"

# --------------------------------------------
# QUESTION VALIDATION FUNCTION (FIXED - Added)
# --------------------------------------------

def validate_question(question_data):
    """Validate question data structure"""
    required_fields = ['question', 'options', 'correct']
    
    # Check required fields
    for field in required_fields:
        if field not in question_data:
            return False, f"Missing field: {field}"
    
    # Check question text
    if not question_data['question'] or len(question_data['question']) < 5:
        return False, "Question must be at least 5 characters"
    
    if len(question_data['question']) > 500:
        return False, "Question too long (max 500 characters)"
    
    # Check options
    options = question_data['options']
    if not isinstance(options, list) or len(options) != 4:
        return False, "Must have exactly 4 options"
    
    for i, opt in enumerate(options):
        if not opt or len(opt) < 1:
            return False, f"Option {chr(65+i)} cannot be empty"
        if len(opt) > 200:
            return False, f"Option {chr(65+i)} too long (max 200 characters)"
    
    # Check correct answer
    correct = question_data['correct'].upper()
    if correct not in ['A', 'B', 'C', 'D']:
        return False, "Correct answer must be A, B, C, or D"
    
    # Check explanation (optional)
    explanation = question_data.get('explanation', '')
    if len(explanation) > 500:
        return False, "Explanation too long (max 500 characters)"
    
    return True, "Valid"

# --------------------------------------------
# RANDOM GENERATION FUNCTIONS
# --------------------------------------------

def generate_random_id():
    """Generate a random ID"""
    return random.randint(100000, 999999)

def generate_session_id():
    """Generate a unique session ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    return f"{timestamp}_{random_num}"

def get_random_emoji():
    """Get a random emoji for fun messages"""
    emojis = ["🎉", "🎊", "🌟", "⭐", "💪", "🔥", "⚡", "🎯", "🏆", "📚", "🧠", "💡", "✨", "🍀"]
    return random.choice(emojis)

def get_random_greeting():
    """Get a random greeting message"""
    greetings = [
        "Hey there!", "Hello!", "Namaste!", "Welcome back!", 
        "Great to see you!", "Ready to learn?", "Let's go!",
        "Keep learning!", "You're doing great!"
    ]
    return random.choice(greetings)

# --------------------------------------------
# DICTIONARY OPERATIONS
# --------------------------------------------

def merge_dicts(dict1, dict2):
    """Merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result

def safe_get(data, keys, default=None):
    """Safely get nested dictionary value"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data

# --------------------------------------------
# LIST OPERATIONS
# --------------------------------------------

def chunk_list(lst, chunk_size):
    """Split a list into chunks"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def shuffle_list(lst):
    """Shuffle a list randomly"""
    shuffled = lst.copy()
    random.shuffle(shuffled)
    return shuffled

def get_unique_items(lst):
    """Get unique items from list while preserving order"""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

# --------------------------------------------
# STRING VALIDATION
# --------------------------------------------

def is_valid_email(email):
    """Check if email is valid (basic check)"""
    return "@" in email and "." in email

def is_valid_username(username):
    """Check if username is valid"""
    return username.isalnum() and 3 <= len(username) <= 30

def clean_text(text):
    """Clean text by removing extra spaces and special characters"""
    text = ' '.join(text.split())
    return text.strip()

def is_valid_answer(answer):
    """Check if answer is valid (A, B, C, D, or skip)"""
    valid_answers = ['A', 'B', 'C', 'D', 'SKIP', 'QUIT']
    return answer.upper() in valid_answers

def normalize_answer(answer):
    """Normalize answer input"""
    answer = answer.strip().upper()
    if answer in ['A', 'B', 'C', 'D']:
        return answer
    elif answer in ['SKIP', 'S']:
        return 'SKIP'
    elif answer in ['QUIT', 'Q', 'EXIT']:
        return 'QUIT'
    return None

# --------------------------------------------
# FILE OPERATIONS
# --------------------------------------------

def read_text_file(file_path):
    """Read text file content"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
    except Exception:
        return None

def write_text_file(file_path, content):
    """Write content to text file"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False

# --------------------------------------------
# USER STATS FORMATTING
# --------------------------------------------

def format_user_stats(user_data):
    """Format user statistics into a readable string"""
    stats = f"""
📊 *YOUR STATISTICS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 *Total Quizzes:* {user_data.get('total_quizzes', 0)}
📝 *Total Questions:* {user_data.get('total_questions', 0)}
✅ *Correct Answers:* {user_data.get('total_correct', 0)}
❌ *Wrong Answers:* {user_data.get('total_wrong', 0)}
⏭️ *Skipped:* {user_data.get('total_skipped', 0)}

📈 *Accuracy:* {user_data.get('accuracy', 0)}%
🏆 *Best Score:* {user_data.get('best_score', 0)}
📊 *Average Score:* {user_data.get('average_score', 0)}

🔥 *Current Streak:* {user_data.get('current_streak', 0)} days
⭐ *Longest Streak:* {user_data.get('longest_streak', 0)} days

💰 *Coins:* {user_data.get('coins', 0)}
🎚️ *Level:* {user_data.get('level', 1)}
✨ *XP:* {user_data.get('xp', 0)}/500

━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    return stats

def format_quiz_result(result):
    """Format quiz result into a readable string"""
    percentage = result['percentage']
    grade_info = get_grade(percentage)
    
    result_text = f"""
🎉 *QUIZ COMPLETE!* 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 *Topic:* {result['topic'].upper()}
⏱️ *Time Taken:* {format_time(result['time_taken'])}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *YOUR SCORE*
✅ Correct: {result['correct']}
❌ Wrong: {result['wrong']}
⏭️ Skipped: {result['skipped']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 *Total:* {result['correct']}/{result['total']} ({percentage}%)

⭐ *Grade:* {grade_info['grade']} {grade_info['emoji']}
💬 *Message:* {grade_info['message']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return result_text

def format_leaderboard_entry(rank, user, score, is_user=False):
    """Format a single leaderboard entry"""
    prefix = "👉 " if is_user else "   "
    rank_emoji = get_rank_emoji(rank)
    return f"{prefix}{rank_emoji} *{user}* - {score} points"