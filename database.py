import json
import os
from config import (
    USERS_DIR, QUESTIONS_DIR, CHAPTERS_DIR, SESSIONS_DIR,
    DAILY_QUIZ_FILE, LEADERBOARD_FILE, SETTINGS_FILE, BROADCAST_LOG_FILE,
    DATA_DIR  # ADD THIS - it was missing
)

# ============================================
# DATABASE UTILITIES - JSON File Operations
# ============================================

# Ensure directories exist
os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(QUESTIONS_DIR, exist_ok=True)
os.makedirs(CHAPTERS_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)

# --------------------------------------------
# USER DATA FUNCTIONS
# --------------------------------------------

def get_user_file(user_id):
    """Get user file path"""
    return os.path.join(USERS_DIR, f"{user_id}.json")

def load_user(user_id):
    """Load user data from JSON file"""
    file_path = get_user_file(user_id)
    
    default_user_data = {
        "user_id": user_id,
        "first_name": "",
        "username": "",
        "joined_date": "",
        "total_quizzes": 0,
        "total_questions": 0,
        "total_correct": 0,
        "total_wrong": 0,
        "total_skipped": 0,
        "best_score": 0,
        "average_score": 0,
        "accuracy": 0,
        "current_streak": 0,
        "longest_streak": 0,
        "last_quiz_date": "",
        "daily_quiz_completed": False,
        "daily_quiz_streak": 0,
        "coins": 0,
        "level": 1,
        "xp": 0,
        "achievements": [],
        "topic_stats": {},
        "quiz_history": [],
        "settings": {
            "notifications": True,
            "difficulty": "medium",
            "language": "english"
        }
    }
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Merge with default to ensure all keys exist
            for key, value in default_user_data.items():
                if key not in data:
                    data[key] = value
            return data
    else:
        return default_user_data

def save_user(user_id, data):
    """Save user data to JSON file"""
    file_path = get_user_file(user_id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_user_stats(user_id, quiz_result):
    """Update user statistics after a quiz"""
    user_data = load_user(user_id)
    
    # Update totals
    user_data["total_quizzes"] = user_data.get("total_quizzes", 0) + 1
    user_data["total_questions"] = user_data.get("total_questions", 0) + quiz_result["total"]
    user_data["total_correct"] = user_data.get("total_correct", 0) + quiz_result["correct"]
    user_data["total_wrong"] = user_data.get("total_wrong", 0) + quiz_result["wrong"]
    user_data["total_skipped"] = user_data.get("total_skipped", 0) + quiz_result["skipped"]
    
    # Update best score
    if quiz_result["correct"] > user_data.get("best_score", 0):
        user_data["best_score"] = quiz_result["correct"]
    
    # Update accuracy
    total_ans = user_data["total_correct"] + user_data["total_wrong"]
    if total_ans > 0:
        user_data["accuracy"] = round((user_data["total_correct"] / total_ans) * 100, 2)
    
    # Update average score
    user_data["average_score"] = round(
        (user_data["total_correct"] / user_data["total_quizzes"]) if user_data["total_quizzes"] > 0 else 0, 2
    )
    
    # Update topic stats
    topic = quiz_result["topic"]
    if topic not in user_data["topic_stats"]:
        user_data["topic_stats"][topic] = {
            "attempts": 0,
            "total_correct": 0,
            "total_questions": 0
        }
    user_data["topic_stats"][topic]["attempts"] += 1
    user_data["topic_stats"][topic]["total_correct"] += quiz_result["correct"]
    user_data["topic_stats"][topic]["total_questions"] += quiz_result["total"]
    
    # Add to quiz history
    user_data["quiz_history"].append({
        "date": quiz_result.get("date", ""),
        "topic": quiz_result["topic"],
        "score": quiz_result["correct"],
        "total": quiz_result["total"],
        "percentage": quiz_result["percentage"]
    })
    
    # Keep only last 50 history entries
    if len(user_data["quiz_history"]) > 50:
        user_data["quiz_history"] = user_data["quiz_history"][-50:]
    
    # Update XP and level
    xp_gained = quiz_result["correct"] * 10
    user_data["xp"] = user_data.get("xp", 0) + xp_gained
    user_data["level"] = (user_data["xp"] // 500) + 1
    
    save_user(user_id, user_data)
    return user_data

def get_all_users():
    """Get list of all user IDs"""
    users = []
    if os.path.exists(USERS_DIR):
        for file in os.listdir(USERS_DIR):
            if file.endswith(".json"):
                user_id = file.replace(".json", "")
                users.append(user_id)
    return users

def get_total_users_count():
    """Get total number of users"""
    return len(get_all_users())

# --------------------------------------------
# QUESTIONS DATA FUNCTIONS
# --------------------------------------------

def get_question_file(topic):
    """Get question file path for a topic"""
    return os.path.join(QUESTIONS_DIR, f"{topic}.json")

def load_questions(topic):
    """Load all questions for a topic"""
    file_path = get_question_file(topic)
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Return empty list if file doesn't exist
        return []

def save_questions(topic, questions):
    """Save questions for a topic"""
    file_path = get_question_file(topic)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

def add_question(topic, question_data):
    """Add a new question to a topic"""
    questions = load_questions(topic)
    question_data["id"] = len(questions) + 1
    questions.append(question_data)
    save_questions(topic, questions)
    return question_data["id"]

def update_question(topic, question_id, question_data):
    """Update an existing question"""
    questions = load_questions(topic)
    for i, q in enumerate(questions):
        if q.get("id") == question_id:
            question_data["id"] = question_id
            questions[i] = question_data
            save_questions(topic, questions)
            return True
    return False

def delete_question(topic, question_id):
    """Delete a question from a topic"""
    questions = load_questions(topic)
    questions = [q for q in questions if q.get("id") != question_id]
    save_questions(topic, questions)
    return True

def get_questions_count(topic):
    """Get total number of questions in a topic"""
    return len(load_questions(topic))

def get_questions_by_chapter(topic, chapter_id):
    """Get questions for a specific chapter"""
    all_questions = load_questions(topic)
    return [q for q in all_questions if q.get("chapter_id") == chapter_id]

# --------------------------------------------
# CHAPTERS DATA FUNCTIONS
# --------------------------------------------

def get_chapter_file(topic):
    """Get chapter file path for a topic"""
    return os.path.join(CHAPTERS_DIR, f"{topic}_chapters.json")

def load_chapters(topic):
    """Load all chapters for a topic"""
    file_path = get_chapter_file(topic)
    
    default_chapters = {
        "maths": [
            {"id": 1, "name": "Algebra", "question_count": 0},
            {"id": 2, "name": "Geometry", "question_count": 0},
            {"id": 3, "name": "Trigonometry", "question_count": 0},
            {"id": 4, "name": "Arithmetic", "question_count": 0},
            {"id": 5, "name": "Calculus", "question_count": 0}
        ],
        "science": [
            {"id": 1, "name": "Physics Basics", "question_count": 0},
            {"id": 2, "name": "Chemistry", "question_count": 0},
            {"id": 3, "name": "Biology Basics", "question_count": 0}
        ],
        "english": [
            {"id": 1, "name": "Tenses", "question_count": 0},
            {"id": 2, "name": "Parts of Speech", "question_count": 0},
            {"id": 3, "name": "Sentence Structure", "question_count": 0},
            {"id": 4, "name": "Vocabulary", "question_count": 0}
        ],
        "biology": [
            {"id": 1, "name": "Human Body", "question_count": 0},
            {"id": 2, "name": "Plants", "question_count": 0},
            {"id": 3, "name": "Animals", "question_count": 0},
            {"id": 4, "name": "Cells and Genetics", "question_count": 0}
        ],
        "physics": [
            {"id": 1, "name": "Laws of Motion", "question_count": 0},
            {"id": 2, "name": "Units and Measurements", "question_count": 0},
            {"id": 3, "name": "Light and Optics", "question_count": 0},
            {"id": 4, "name": "Electricity and Magnetism", "question_count": 0}
        ],
        "gk": [
            {"id": 1, "name": "Indian History", "question_count": 0},
            {"id": 2, "name": "World Geography", "question_count": 0},
            {"id": 3, "name": "Indian Polity", "question_count": 0},
            {"id": 4, "name": "Science and Technology", "question_count": 0},
            {"id": 5, "name": "Current Affairs", "question_count": 0}
        ]
    }
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Create default chapters for this topic
        if topic in default_chapters:
            return default_chapters[topic]
        return []

def save_chapters(topic, chapters):
    """Save chapters for a topic"""
    file_path = get_chapter_file(topic)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(chapters, f, indent=2, ensure_ascii=False)

def update_chapter_question_count(topic, chapter_id):
    """Update question count for a chapter"""
    chapters = load_chapters(topic)
    questions = get_questions_by_chapter(topic, chapter_id)
    
    for chapter in chapters:
        if chapter["id"] == chapter_id:
            chapter["question_count"] = len(questions)
            break
    
    save_chapters(topic, chapters)

# --------------------------------------------
# SESSION DATA FUNCTIONS
# --------------------------------------------

def get_session_file(user_id):
    """Get session file path for a user"""
    return os.path.join(SESSIONS_DIR, f"{user_id}.json")

def save_session(user_id, session_data):
    """Save active quiz session"""
    file_path = get_session_file(user_id)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

def load_session(user_id):
    """Load active quiz session"""
    file_path = get_session_file(user_id)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def delete_session(user_id):
    """Delete active quiz session"""
    file_path = get_session_file(user_id)
    if os.path.exists(file_path):
        os.remove(file_path)

# --------------------------------------------
# DAILY QUIZ FUNCTIONS
# --------------------------------------------

def load_daily_quiz():
    """Load daily quiz data"""
    if os.path.exists(DAILY_QUIZ_FILE):
        with open(DAILY_QUIZ_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "date": "",
            "topic": "",
            "questions": [],
            "participants": {}
        }

def save_daily_quiz(data):
    """Save daily quiz data"""
    with open(DAILY_QUIZ_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --------------------------------------------
# LEADERBOARD FUNCTIONS
# --------------------------------------------

def load_leaderboard():
    """Load leaderboard data"""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"last_updated": "", "top_users": []}

def save_leaderboard(data):
    """Save leaderboard data"""
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_leaderboard():
    """Update leaderboard with latest user stats"""
    all_users = get_all_users()
    top_users = []
    
    for user_id in all_users:
        user_data = load_user(user_id)
        top_users.append({
            "user_id": user_id,
            "name": user_data.get("first_name", "User"),
            "total_correct": user_data.get("total_correct", 0),
            "accuracy": user_data.get("accuracy", 0),
            "level": user_data.get("level", 1)
        })
    
    top_users.sort(key=lambda x: x["total_correct"], reverse=True)
    
    from datetime import datetime
    leaderboard_data = {
        "last_updated": datetime.now().isoformat(),
        "top_users": top_users[:50]
    }
    
    save_leaderboard(leaderboard_data)
    return leaderboard_data

def get_leaderboard_file():
    """Get leaderboard file path"""
    return LEADERBOARD_FILE

# --------------------------------------------
# BROADCAST LOG FUNCTIONS
# --------------------------------------------

def load_broadcast_log():
    """Load broadcast log"""
    if os.path.exists(BROADCAST_LOG_FILE):
        with open(BROADCAST_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"broadcasts": []}

def save_broadcast_log(data):
    """Save broadcast log"""
    with open(BROADCAST_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_broadcast(message, total_sent, success_count):
    """Log a broadcast message"""
    log = load_broadcast_log()
    log["broadcasts"].append({
        "date": __import__("datetime").datetime.now().isoformat(),
        "message": message[:100],
        "total_sent": total_sent,
        "success_count": success_count
    })
    save_broadcast_log(log)

# --------------------------------------------
# SETTINGS FUNCTIONS
# --------------------------------------------

def load_settings():
    """Load bot settings"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "bot_active": True,
            "maintenance_mode": False,
            "daily_quiz_enabled": True,
            "reminder_time": "09:00",
            "default_quiz_type": "quick"
        }

def save_settings(data):
    """Save bot settings"""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)