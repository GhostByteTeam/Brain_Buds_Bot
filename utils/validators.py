import re

# ============================================
# VALIDATORS - Input Validation Functions
# ============================================

# --------------------------------------------
# QUIZ ANSWER VALIDATION
# --------------------------------------------

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
# QUESTION VALIDATION (For Admin)
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
# USER INPUT VALIDATION
# --------------------------------------------

def validate_name(name):
    """Validate user name input"""
    if not name:
        return False, "Name cannot be empty"
    
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 50:
        return False, "Name too long (max 50 characters)"
    
    # Allow letters, spaces, dots, and hyphens
    if not re.match(r'^[a-zA-Z\s\.\-]+$', name):
        return False, "Name can only contain letters, spaces, dots, and hyphens"
    
    return True, "Valid"

def validate_email(email):
    """Validate email address"""
    if not email:
        return False, "Email cannot be empty"
    
    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 100:
        return False, "Email too long (max 100 characters)"
    
    return True, "Valid"

def validate_username(username):
    """Validate username"""
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 30:
        return False, "Username too long (max 30 characters)"
    
    # Allow letters, numbers, underscore, dot
    if not re.match(r'^[a-zA-Z0-9_.]+$', username):
        return False, "Username can only contain letters, numbers, underscore, and dot"
    
    return True, "Valid"

def validate_age(age):
    """Validate age input"""
    try:
        age_int = int(age)
        if age_int < 5:
            return False, "Age must be at least 5"
        if age_int > 120:
            return False, "Invalid age"
        return True, "Valid"
    except ValueError:
        return False, "Age must be a number"

# --------------------------------------------
# QUIZ CONFIGURATION VALIDATION
# --------------------------------------------

def validate_quiz_config(config):
    """Validate quiz configuration"""
    valid_types = ['quick', 'full', 'practice', 'exam']
    
    quiz_type = config.get('type')
    if quiz_type not in valid_types:
        return False, f"Invalid quiz type. Choose from: {', '.join(valid_types)}"
    
    # Validate question count
    q_count = config.get('question_count', 0)
    if q_count < 1:
        return False, "Question count must be at least 1"
    
    if q_count > 100:
        return False, "Question count cannot exceed 100"
    
    # Validate time limit
    time_limit = config.get('time_limit')
    if time_limit is not None:
        if time_limit < 10:
            return False, "Time limit must be at least 10 seconds"
        if time_limit > 3600:
            return False, "Time limit cannot exceed 1 hour"
    
    return True, "Valid"

# --------------------------------------------
# NUMBER VALIDATION
# --------------------------------------------

def is_positive_integer(value):
    """Check if value is a positive integer"""
    try:
        num = int(value)
        return num > 0
    except ValueError:
        return False

def is_in_range(value, min_val, max_val):
    """Check if value is within range"""
    try:
        num = int(value)
        return min_val <= num <= max_val
    except ValueError:
        return False

def validate_percentage(percentage):
    """Validate percentage value"""
    try:
        p = float(percentage)
        return 0 <= p <= 100
    except ValueError:
        return False

# --------------------------------------------
# COMMAND VALIDATION
# --------------------------------------------

def is_valid_command(text):
    """Check if text is a valid command"""
    if not text:
        return False
    return text.startswith('/')

def extract_command_args(text):
    """Extract arguments from command"""
    parts = text.split(maxsplit=1)
    if len(parts) > 1:
        return parts[1].strip()
    return None

# --------------------------------------------
# TOPIC AND CHAPTER VALIDATION
# --------------------------------------------

def is_valid_topic(topic, available_topics):
    """Check if topic is valid"""
    return topic in available_topics

def is_valid_chapter(chapter_id, chapters):
    """Check if chapter ID is valid"""
    try:
        cid = int(chapter_id)
        return any(ch['id'] == cid for ch in chapters)
    except (ValueError, TypeError):
        return False

# --------------------------------------------
# DATE VALIDATION
# --------------------------------------------

def is_valid_date(date_string, format="%Y-%m-%d"):
    """Check if date string is valid"""
    from datetime import datetime
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

def is_future_date(date_string):
    """Check if date is in future"""
    from datetime import datetime
    try:
        date = datetime.strptime(date_string, "%Y-%m-%d")
        return date > datetime.now()
    except ValueError:
        return False

# --------------------------------------------
# SAFE INPUT HANDLING
# --------------------------------------------

def sanitize_input(text):
    """Sanitize user input to prevent injection"""
    if not text:
        return ""
    
    # Remove dangerous characters
    dangerous = ['<', '>', '{', '}', '[', ']', '|', ';', '&', '$', '`', '\\']
    for char in dangerous:
        text = text.replace(char, '')
    
    # Limit length
    if len(text) > 1000:
        text = text[:1000]
    
    return text.strip()

def validate_telegram_id(user_id):
    """Validate Telegram user ID"""
    try:
        uid = int(user_id)
        return uid > 0
    except (ValueError, TypeError):
        return False