import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOPICS, TOPIC_ORDER, QUIZ_TYPES
from database import load_questions, load_chapters, get_questions_count, get_questions_by_chapter
from buttons import get_chapters_keyboard, get_quiz_modes_keyboard, get_topics_keyboard

# ============================================
# TOPICS HANDLER - Topic and Chapter Management
# ============================================

def show_topics(bot, message):
    """Show all available topics to user"""
    user_id = message.from_user.id
    
    # Get or create message object for proper editing
    if hasattr(message, 'chat'):
        chat_id = message.chat.id
    else:
        chat_id = message
    
    markup = get_topics_keyboard()
    
    topics_text = "📚 *Available Subjects*\n\n"
    topics_text += "Choose a subject to start your quiz journey!\n\n"
    topics_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for topic_id in TOPIC_ORDER:
        topic_name = TOPICS[topic_id]["name"]
        topic_icon = TOPICS[topic_id]["icon"]
        q_count = get_questions_count(topic_id)
        topics_text += f"{topic_icon} *{topic_name}*\n"
        topics_text += f"   📊 {q_count} questions available\n\n"
    
    topics_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    topics_text += "👇 *Tap on a subject to continue*"
    
    # Check if this is a callback or direct message
    if hasattr(message, 'message_id'):
        bot.edit_message_text(
            topics_text,
            chat_id,
            message.message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            chat_id,
            topics_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

def select_topic(bot, message, topic):
    """Handle topic selection from reply keyboard"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Show chapters for selected topic
    show_chapters_direct(bot, chat_id, topic)

def show_chapters(bot, call, topic):
    """Show chapters for selected topic (from inline callback)"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    chapters = load_chapters(topic)
    topic_name = TOPICS[topic]["name"]
    topic_icon = TOPICS[topic]["icon"]
    
    # Update question counts for chapters
    for chapter in chapters:
        q_count = len(get_questions_by_chapter(topic, chapter["id"]))
        chapter["question_count"] = q_count
    
    if not chapters:
        # No chapters found, create default
        chapters = create_default_chapters(topic)
    
    markup = get_chapters_keyboard(topic, chapters)
    
    chapters_text = f"{topic_icon} *{topic_name} - Chapters*\n\n"
    chapters_text += "Select a chapter to begin:\n\n"
    chapters_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for chapter in chapters:
        q_count = chapter.get("question_count", 0)
        status = "✅" if q_count > 0 else "❌"
        chapters_text += f"{status} *{chapter['name']}*\n"
        chapters_text += f"   📊 {q_count} questions\n\n"
    
    chapters_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    chapters_text += "👇 *Tap on a chapter to continue*"
    
    bot.edit_message_text(
        chapters_text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_chapters_direct(bot, chat_id, topic):
    """Show chapters for selected topic (direct message)"""
    chapters = load_chapters(topic)
    topic_name = TOPICS[topic]["name"]
    topic_icon = TOPICS[topic]["icon"]
    
    # Update question counts for chapters
    for chapter in chapters:
        q_count = len(get_questions_by_chapter(topic, chapter["id"]))
        chapter["question_count"] = q_count
    
    if not chapters:
        chapters = create_default_chapters(topic)
    
    markup = get_chapters_keyboard(topic, chapters)
    
    chapters_text = f"{topic_icon} *{topic_name} - Chapters*\n\n"
    chapters_text += "Select a chapter to begin:\n\n"
    chapters_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for chapter in chapters:
        q_count = chapter.get("question_count", 0)
        status = "✅" if q_count > 0 else "❌"
        chapters_text += f"{status} *{chapter['name']}*\n"
        chapters_text += f"   📊 {q_count} questions\n\n"
    
    chapters_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    chapters_text += "👇 *Tap on a chapter to continue*"
    
    bot.send_message(
        chat_id,
        chapters_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_quiz_options(bot, call, topic, chapter_id):
    """Show quiz type options for selected chapter"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    chapters = load_chapters(topic)
    chapter_name = None
    for ch in chapters:
        if ch["id"] == chapter_id:
            chapter_name = ch["name"]
            break
    
    topic_name = TOPICS[topic]["name"]
    topic_icon = TOPICS[topic]["icon"]
    
    markup = get_quiz_modes_keyboard(topic, chapter_id)
    
    quiz_text = f"{topic_icon} *{topic_name}* → *{chapter_name}*\n\n"
    quiz_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    quiz_text += "*Choose Quiz Mode:*\n\n"
    
    for mode_id, mode_info in QUIZ_TYPES.items():
        quiz_text += f"• *{mode_info['name']}*\n"
        quiz_text += f"  {mode_info['description']}\n\n"
    
    quiz_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    quiz_text += "💡 *Tip:* Start with Practice Mode to learn!"
    
    bot.edit_message_text(
        quiz_text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def create_default_chapters(topic):
    """Create default chapters for a topic if none exist"""
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
    
    from database import save_chapters
    if topic in default_chapters:
        save_chapters(topic, default_chapters[topic])
        return default_chapters[topic]
    
    return []