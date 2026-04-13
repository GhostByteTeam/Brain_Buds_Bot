from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ============================================
# BUTTONS & KEYBOARDS - All UI Elements
# ============================================

# --------------------------------------------
# MAIN MENU BUTTONS (Reply Keyboard)
# --------------------------------------------

def get_main_menu_keyboard():
    """Main menu keyboard with all topic buttons"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        KeyboardButton("📚 Mathematics"),
        KeyboardButton("🔬 Science"),
        KeyboardButton("📖 English Grammar"),
        KeyboardButton("🧬 Biology"),
        KeyboardButton("⚡ Physics"),
        KeyboardButton("🌍 General Knowledge"),
        KeyboardButton("📅 Daily Quiz"),
        KeyboardButton("🏆 Leaderboard"),
        KeyboardButton("📊 My Stats"),
        KeyboardButton("❓ Help"),
        KeyboardButton("ℹ️ About")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# BACK BUTTON (Reply Keyboard)
# --------------------------------------------

def get_back_button():
    """Simple back button"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton("◀️ Back to Menu"))
    return markup

# --------------------------------------------
# QUIZ MODES KEYBOARD (Inline)
# --------------------------------------------

def get_quiz_modes_keyboard(topic, chapter_id):
    """Inline keyboard for quiz mode selection"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("📝 Quick Quiz (5 Qs)", callback_data=f"quiz_{topic}_{chapter_id}_quick"),
        InlineKeyboardButton("📖 Full Test (20 Qs)", callback_data=f"quiz_{topic}_{chapter_id}_full"),
        InlineKeyboardButton("🎯 Practice Mode (10 Qs)", callback_data=f"quiz_{topic}_{chapter_id}_practice"),
        InlineKeyboardButton("⚡ Exam Mode (15 Qs)", callback_data=f"quiz_{topic}_{chapter_id}_exam"),
        InlineKeyboardButton("◀️ Back to Chapters", callback_data=f"chapters_{topic}")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# CHAPTERS KEYBOARD (Inline)
# --------------------------------------------

def get_chapters_keyboard(topic, chapters):
    """Inline keyboard for chapter selection"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    for chapter in chapters:
        chapter_name = chapter.get("name", f"Chapter {chapter['id']}")
        q_count = chapter.get("question_count", 0)
        button_text = f"{chapter_name} ({q_count} Qs)"
        markup.add(InlineKeyboardButton(button_text, callback_data=f"chapter_{topic}_{chapter['id']}"))
    
    markup.add(InlineKeyboardButton("◀️ Back to Topics", callback_data="back_to_topics"))
    
    return markup

# --------------------------------------------
# TOPICS KEYBOARD (Inline)
# --------------------------------------------

def get_topics_keyboard():
    """Inline keyboard for topic selection"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    topics = [
        ("📚 Mathematics", "maths"),
        ("🔬 Science", "science"),
        ("📖 English Grammar", "english"),
        ("🧬 Biology", "biology"),
        ("⚡ Physics", "physics"),
        ("🌍 General Knowledge", "gk")
    ]
    
    for name, topic_id in topics:
        markup.add(InlineKeyboardButton(name, callback_data=f"topic_{topic_id}"))
    
    return markup

# --------------------------------------------
# QUIZ CONTROL BUTTONS (Inline)
# --------------------------------------------

def get_quiz_control_buttons(question_number, total_questions):
    """Inline keyboard during quiz"""
    markup = InlineKeyboardMarkup(row_width=4)
    
    buttons = [
        InlineKeyboardButton("A", callback_data="ans_A"),
        InlineKeyboardButton("B", callback_data="ans_B"),
        InlineKeyboardButton("C", callback_data="ans_C"),
        InlineKeyboardButton("D", callback_data="ans_D"),
        InlineKeyboardButton("⏭️ Skip", callback_data="ans_skip"),
        InlineKeyboardButton("❌ Quit", callback_data="ans_quit")
    ]
    
    markup.add(*buttons)
    
    # Add progress indicator
    markup.add(InlineKeyboardButton(f"📊 Question {question_number}/{total_questions}", callback_data="noop"))
    
    return markup

# --------------------------------------------
# RESULT ACTION BUTTONS (Inline)
# --------------------------------------------

def get_result_buttons(topic, chapter_id):
    """Inline keyboard after quiz completion"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("🔄 Retest (Wrong Only)", callback_data=f"retest_{topic}_{chapter_id}"),
        InlineKeyboardButton("📚 New Quiz", callback_data=f"chapter_{topic}_{chapter_id}"),
        InlineKeyboardButton("🏆 Leaderboard", callback_data="view_leaderboard"),
        InlineKeyboardButton("📊 My Stats", callback_data="view_mystats"),
        InlineKeyboardButton("◀️ Main Menu", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# LEADERBOARD KEYBOARD (Inline)
# --------------------------------------------

def get_leaderboard_keyboard():
    """Inline keyboard for leaderboard options"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("🏆 Overall", callback_data="leaderboard_overall"),
        InlineKeyboardButton("📊 Accuracy", callback_data="leaderboard_accuracy"),
        InlineKeyboardButton("📚 Maths", callback_data="leaderboard_maths"),
        InlineKeyboardButton("🔬 Science", callback_data="leaderboard_science"),
        InlineKeyboardButton("📖 English", callback_data="leaderboard_english"),
        InlineKeyboardButton("🌍 GK", callback_data="leaderboard_gk"),
        InlineKeyboardButton("◀️ Back", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# ADMIN PANEL KEYBOARD (Inline) - Owner Only
# --------------------------------------------

def get_admin_keyboard():
    """Inline keyboard for admin panel"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats"),
        InlineKeyboardButton("📚 Add Question", callback_data="admin_add_question"),
        InlineKeyboardButton("✏️ Edit Question", callback_data="admin_edit_question"),
        InlineKeyboardButton("🗑️ Delete Question", callback_data="admin_delete_question"),
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        InlineKeyboardButton("📅 Set Daily Quiz", callback_data="admin_daily_quiz"),
        InlineKeyboardButton("👥 Users List", callback_data="admin_users"),
        InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings"),
        InlineKeyboardButton("📤 Export Data", callback_data="admin_export"),
        InlineKeyboardButton("◀️ Back", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# SETTINGS KEYBOARD (Inline)
# --------------------------------------------

def get_settings_keyboard():
    """Inline keyboard for user settings"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
        InlineKeyboardButton("📝 Difficulty", callback_data="settings_difficulty"),
        InlineKeyboardButton("🌐 Language", callback_data="settings_language"),
        InlineKeyboardButton("◀️ Back", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# DAILY QUIZ KEYBOARD (Inline)
# --------------------------------------------

def get_daily_quiz_keyboard():
    """Inline keyboard for daily quiz"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    buttons = [
        InlineKeyboardButton("📅 Start Daily Quiz", callback_data="start_daily_quiz"),
        InlineKeyboardButton("📊 Daily Leaderboard", callback_data="daily_leaderboard"),
        InlineKeyboardButton("◀️ Back", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# CONFIRMATION KEYBOARD (Inline)
# --------------------------------------------

def get_confirmation_keyboard(action, data):
    """Confirmation keyboard for important actions"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("✅ Yes", callback_data=f"confirm_{action}_{data}"),
        InlineKeyboardButton("❌ No", callback_data="cancel")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# HELP & SUPPORT KEYBOARD (Inline)
# --------------------------------------------

def get_help_keyboard():
    """Inline keyboard for help section"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    buttons = [
        InlineKeyboardButton("📖 Commands Guide", callback_data="help_commands"),
        InlineKeyboardButton("🏆 Scoring System", callback_data="help_scoring"),
        InlineKeyboardButton("❓ FAQ", callback_data="help_faq"),
        InlineKeyboardButton("📞 Contact Support", callback_data="help_support"),
        InlineKeyboardButton("◀️ Back", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# TOPIC WISE LEADERBOARD HELPER
# --------------------------------------------

def get_topic_leaderboard_buttons():
    """Get topic buttons for leaderboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("📚 Maths", callback_data="lb_maths"),
        InlineKeyboardButton("🔬 Science", callback_data="lb_science"),
        InlineKeyboardButton("📖 English", callback_data="lb_english"),
        InlineKeyboardButton("🧬 Biology", callback_data="lb_biology"),
        InlineKeyboardButton("⚡ Physics", callback_data="lb_physics"),
        InlineKeyboardButton("🌍 GK", callback_data="lb_gk"),
        InlineKeyboardButton("◀️ Back", callback_data="leaderboard_back")
    ]
    
    markup.add(*buttons)
    return markup

# --------------------------------------------
# CANCEL BUTTON (Simple)
# --------------------------------------------

def get_cancel_button():
    """Simple cancel button"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    return markup

# --------------------------------------------
# NUMERIC KEYPAD FOR ADMIN (Simple)
# --------------------------------------------

def get_numeric_keypad():
    """Numeric keypad for admin inputs"""
    markup = InlineKeyboardMarkup(row_width=3)
    
    buttons = [
        InlineKeyboardButton("1", callback_data="num_1"),
        InlineKeyboardButton("2", callback_data="num_2"),
        InlineKeyboardButton("3", callback_data="num_3"),
        InlineKeyboardButton("4", callback_data="num_4"),
        InlineKeyboardButton("5", callback_data="num_5"),
        InlineKeyboardButton("6", callback_data="num_6"),
        InlineKeyboardButton("7", callback_data="num_7"),
        InlineKeyboardButton("8", callback_data="num_8"),
        InlineKeyboardButton("9", callback_data="num_9"),
        InlineKeyboardButton("0", callback_data="num_0"),
        InlineKeyboardButton("✅ Done", callback_data="num_done"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ]
    
    markup.add(*buttons)
    return markup