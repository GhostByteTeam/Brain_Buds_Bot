import os
import json
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID, ADMIN_IDS, TOPICS, TOPIC_ORDER, BOT_NAME, BOT_VERSION
from database import (
    load_user, save_user, get_all_users, get_total_users_count,
    load_questions, save_questions, add_question, update_question, delete_question,
    load_chapters, save_chapters, get_questions_count, get_questions_by_chapter,
    load_daily_quiz, save_daily_quiz, load_settings, save_settings,
    load_broadcast_log, get_leaderboard_file
)
from decorators import admin_only, owner_only
from utils.helpers import validate_question, get_current_datetime

# ============================================
# ADMIN PANEL - Owner Only Features
# ============================================

# Store admin states for multi-step operations
admin_states = {}

def show_admin_panel(bot, message):
    """Show admin panel with all options"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if user is admin
    if user_id not in ADMIN_IDS and user_id != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use admin commands!")
        return
    
    text = build_admin_panel_text()
    markup = get_admin_panel_keyboard()
    
    bot.send_message(
        chat_id,
        text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def build_admin_panel_text():
    """Build admin panel welcome text"""
    total_users = get_total_users_count()
    settings = load_settings()
    
    text = f"""
👑 *ADMIN CONTROL PANEL*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 *Bot:* {BOT_NAME} v{BOT_VERSION}
📊 *Total Users:* {total_users}
📅 *Bot Status:* {'🟢 Active' if settings.get('bot_active', True) else '🔴 Maintenance'}
📢 *Daily Quiz:* {'✅ Enabled' if settings.get('daily_quiz_enabled', True) else '❌ Disabled'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Available Actions:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 *Question Bank Management*
• Add/Edit/Delete questions
• Bulk import/export

📅 *Daily Quiz Management*
• Set today's quiz
• View daily stats

📢 *Broadcast System*
• Send messages to all users

⚙️ *Bot Settings*
• Maintenance mode
• Bot configuration

📊 *Analytics*
• View bot statistics
• Export user data

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 *Tap on any option below*
"""
    return text

def get_admin_panel_keyboard():
    """Get admin panel inline keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("📊 Bot Statistics", callback_data="admin_stats"),
        InlineKeyboardButton("📚 Manage Questions", callback_data="admin_questions"),
        InlineKeyboardButton("📅 Daily Quiz", callback_data="admin_daily_quiz"),
        InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
        InlineKeyboardButton("👥 User Management", callback_data="admin_users"),
        InlineKeyboardButton("⚙️ Bot Settings", callback_data="admin_settings"),
        InlineKeyboardButton("📤 Export Data", callback_data="admin_export"),
        InlineKeyboardButton("🔄 Update Leaderboard", callback_data="admin_update_lb"),
        InlineKeyboardButton("◀️ Close Panel", callback_data="admin_close")
    ]
    
    markup.add(*buttons)
    return markup

def show_bot_stats(bot, call):
    """Show detailed bot statistics"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    total_users = get_total_users_count()
    settings = load_settings()
    
    # Calculate total questions across all topics
    total_questions = 0
    topic_stats = {}
    
    for topic_id in TOPIC_ORDER:
        q_count = get_questions_count(topic_id)
        total_questions += q_count
        topic_stats[topic_id] = q_count
    
    # Calculate active users (played in last 7 days)
    active_users = 0
    from utils.time_utils import get_current_date, days_between
    
    all_users = get_all_users()
    for uid in all_users:
        user_data = load_user(uid)
        last_quiz = user_data.get('last_quiz_date', '')
        if last_quiz:
            try:
                days = days_between(last_quiz, get_current_date())
                if days <= 7:
                    active_users += 1
            except:
                pass
    
    # Get daily quiz stats
    daily_data = load_daily_quiz()
    daily_participants = len(daily_data.get('participants', {}))
    
    text = f"""
📊 *BOT STATISTICS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 *Bot Information*
• Name: {BOT_NAME}
• Version: {BOT_VERSION}
• Status: {'🟢 Active' if settings.get('bot_active', True) else '🔴 Maintenance'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👥 *User Statistics*
• Total Users: {total_users}
• Active Users (7 days): {active_users}
• Engagement Rate: {(active_users/total_users*100) if total_users > 0 else 0:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 *Question Bank*
• Total Questions: {total_questions}
"""

    for topic_id, count in topic_stats.items():
        topic_name = TOPICS.get(topic_id, {}).get('name', topic_id)
        text += f"• {topic_name}: {count} questions\n"
    
    text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 *Daily Quiz*
• Today's Participants: {daily_participants}
• Daily Quiz Enabled: {'✅' if settings.get('daily_quiz_enabled', True) else '❌'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ *System*
• Maintenance Mode: {'🔴 ON' if settings.get('maintenance_mode', False) else '🟢 OFF'}
• Reminder Time: {settings.get('reminder_time', '09:00')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 *Last Updated:* {get_current_datetime()}
"""
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats"))
    markup.add(InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_back"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_questions_menu(bot, call):
    """Show questions management menu"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    text = """
📚 *QUESTION BANK MANAGEMENT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select a topic to manage questions:

Available Topics:
"""

    for topic_id in TOPIC_ORDER:
        topic_name = TOPICS.get(topic_id, {}).get('name', topic_id)
        q_count = get_questions_count(topic_id)
        text += f"\n• {topic_name}: {q_count} questions"
    
    text += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👇 *Select a topic below*"
    
    markup = get_topics_management_keyboard()
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def get_topics_management_keyboard():
    """Get topics selection keyboard for admin"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = []
    for topic_id in TOPIC_ORDER:
        topic_name = TOPICS.get(topic_id, {}).get('name', topic_id)
        topic_icon = TOPICS.get(topic_id, {}).get('icon', '📚')
        buttons.append(InlineKeyboardButton(
            f"{topic_icon} {topic_name}",
            callback_data=f"admin_topic_{topic_id}"
        ))
    
    buttons.append(InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_back"))
    
    markup.add(*buttons)
    return markup

def show_topic_questions_menu(bot, call, topic):
    """Show question management options for a specific topic"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    topic_name = TOPICS.get(topic, {}).get('name', topic)
    q_count = get_questions_count(topic)
    
    text = f"""
📚 *Managing: {topic_name}*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Total Questions:* {q_count}

*What would you like to do?*

• Add new questions
• Edit existing questions
• Delete questions
• Bulk import questions
• Export questions

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 *Select an action below*
"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("➕ Add Question", callback_data=f"admin_add_{topic}"),
        InlineKeyboardButton("✏️ Edit Question", callback_data=f"admin_edit_{topic}"),
        InlineKeyboardButton("🗑️ Delete Question", callback_data=f"admin_delete_{topic}"),
        InlineKeyboardButton("📤 Export Questions", callback_data=f"admin_export_{topic}"),
        InlineKeyboardButton("◀️ Back to Topics", callback_data="admin_questions"),
        InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_back")
    ]
    
    markup.add(*buttons)
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def start_add_question(bot, call, topic):
    """Start the add question process"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Initialize admin state for this user
    admin_states[user_id] = {
        'action': 'adding_question',
        'topic': topic,
        'step': 'question_text',
        'data': {}
    }
    
    text = f"""
➕ *Add New Question - {TOPICS.get(topic, {}).get('name', topic)}*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

*Step 1/7:* Enter the question text

Example: "What is the capital of France?"

Please send the question text as a message.
Type /cancel to cancel this operation.
"""
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        parse_mode='Markdown'
    )

def handle_add_question_step(bot, message):
    """Handle each step of adding a question"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id not in admin_states:
        return False
    
    state = admin_states[user_id]
    if state.get('action') != 'adding_question':
        return False
    
    step = state.get('step')
    topic = state.get('topic')
    data = state.get('data', {})
    
    if step == 'question_text':
        # Save question text
        data['question'] = message.text.strip()
        state['step'] = 'option_a'
        state['data'] = data
        admin_states[user_id] = state
        
        bot.reply_to(
            message,
            f"✅ Question saved!\n\n*Step 2/7:* Enter option A\n\nType /cancel to cancel.",
            parse_mode='Markdown'
        )
        return True
    
    elif step == 'option_a':
        data['option_a'] = message.text.strip()
        state['step'] = 'option_b'
        state['data'] = data
        admin_states[user_id] = state
        
        bot.reply_to(
            message,
            f"✅ Option A saved!\n\n*Step 3/7:* Enter option B\n\nType /cancel to cancel.",
            parse_mode='Markdown'
        )
        return True
    
    elif step == 'option_b':
        data['option_b'] = message.text.strip()
        state['step'] = 'option_c'
        state['data'] = data
        admin_states[user_id] = state
        
        bot.reply_to(
            message,
            f"✅ Option B saved!\n\n*Step 4/7:* Enter option C\n\nType /cancel to cancel.",
            parse_mode='Markdown'
        )
        return True
    
    elif step == 'option_c':
        data['option_c'] = message.text.strip()
        state['step'] = 'option_d'
        state['data'] = data
        admin_states[user_id] = state
        
        bot.reply_to(
            message,
            f"✅ Option C saved!\n\n*Step 5/7:* Enter option D\n\nType /cancel to cancel.",
            parse_mode='Markdown'
        )
        return True
    
    elif step == 'option_d':
        data['option_d'] = message.text.strip()
        state['step'] = 'correct_answer'
        state['data'] = data
        admin_states[user_id] = state
        
        bot.reply_to(
            message,
            f"✅ Option D saved!\n\n*Step 6/7:* Enter correct answer (A, B, C, or D)\n\nType /cancel to cancel.",
            parse_mode='Markdown'
        )
        return True
    
    elif step == 'correct_answer':
        answer = message.text.strip().upper()
        if answer not in ['A', 'B', 'C', 'D']:
            bot.reply_to(
                message,
                "❌ Invalid answer! Please enter A, B, C, or D.\n\nType /cancel to cancel."
            )
            return True
        
        data['correct'] = answer
        state['step'] = 'explanation'
        state['data'] = data
        admin_states[user_id] = state
        
        bot.reply_to(
            message,
            f"✅ Correct answer set to {answer}!\n\n*Step 7/7:* Enter explanation (optional, or type 'skip')\n\nType /cancel to cancel.",
            parse_mode='Markdown'
        )
        return True
    
    elif step == 'explanation':
        explanation = message.text.strip()
        if explanation.lower() != 'skip':
            data['explanation'] = explanation
        
        # Save the question
        question_data = {
            'question': data['question'],
            'options': [data['option_a'], data['option_b'], data['option_c'], data['option_d']],
            'correct': data['correct'],
            'explanation': data.get('explanation', ''),
            'chapter_id': 1,  # Default chapter
            'created_at': get_current_datetime()
        }
        
        # Validate question
        is_valid, msg = validate_question(question_data)
        if not is_valid:
            bot.reply_to(message, f"❌ Invalid question: {msg}\n\nPlease start over with /admin")
            del admin_states[user_id]
            return True
        
        # Add to database
        new_id = add_question(topic, question_data)
        
        if new_id:
            bot.reply_to(
                message,
                f"✅ *Question added successfully!*\n\n"
                f"📝 Question ID: {new_id}\n"
                f"📚 Topic: {TOPICS.get(topic, {}).get('name', topic)}\n"
                f"❓ Question: {data['question'][:100]}...\n\n"
                f"Use /admin to add more questions.",
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(message, "❌ Failed to add question. Please try again.")
        
        # Clear admin state
        del admin_states[user_id]
        return True
    
    return False

def start_edit_question(bot, call, topic):
    """Start editing a question"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    questions = load_questions(topic)
    
    if not questions:
        bot.answer_callback_query(call.id, "No questions available to edit!")
        return
    
    # Store in admin state
    admin_states[user_id] = {
        'action': 'editing_question',
        'topic': topic,
        'step': 'select_question',
        'questions': questions
    }
    
    # Show list of questions to select from
    text = f"✏️ *Edit Question - {TOPICS.get(topic, {}).get('name', topic)}*\n\n"
    text += "Select a question to edit:\n\n"
    
    for i, q in enumerate(questions[:20], 1):
        text += f"{i}. {q['question'][:50]}...\n"
    
    if len(questions) > 20:
        text += f"\n... and {len(questions) - 20} more questions\n"
    
    text += "\nSend the question number to edit.\nType /cancel to cancel."
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def handle_edit_question(bot, message):
    """Handle question editing"""
    user_id = message.from_user.id
    
    if user_id not in admin_states:
        return False
    
    state = admin_states[user_id]
    if state.get('action') != 'editing_question':
        return False
    
    step = state.get('step')
    topic = state.get('topic')
    
    if step == 'select_question':
        try:
            q_num = int(message.text.strip()) - 1
            questions = state.get('questions', [])
            
            if 0 <= q_num < len(questions):
                selected_q = questions[q_num]
                state['selected_question'] = selected_q
                state['selected_index'] = q_num
                state['step'] = 'choose_field'
                admin_states[user_id] = state
                
                text = f"✏️ *Editing Question #{q_num + 1}*\n\n"
                text += f"📝 Question: {selected_q['question']}\n\n"
                text += "What would you like to edit?\n\n"
                text += "1. Question text\n"
                text += "2. Option A\n"
                text += "3. Option B\n"
                text += "4. Option C\n"
                text += "5. Option D\n"
                text += "6. Correct answer\n"
                text += "7. Explanation\n\n"
                text += "Send the number of the field to edit.\nType /cancel to cancel."
                
                bot.reply_to(message, text, parse_mode='Markdown')
            else:
                bot.reply_to(message, f"❌ Invalid number! Please send a number between 1 and {len(questions)}")
        except ValueError:
            bot.reply_to(message, "❌ Please send a valid number!")
        
        return True
    
    elif step == 'choose_field':
        field_map = {
            '1': 'question',
            '2': 'option_a',
            '3': 'option_b',
            '4': 'option_c',
            '5': 'option_d',
            '6': 'correct',
            '7': 'explanation'
        }
        
        field_num = message.text.strip()
        if field_num not in field_map:
            bot.reply_to(message, "❌ Invalid choice! Send a number between 1 and 7.")
            return True
        
        state['editing_field'] = field_map[field_num]
        state['step'] = 'enter_new_value'
        admin_states[user_id] = state
        
        field_names = {
            'question': 'question text',
            'option_a': 'option A',
            'option_b': 'option B',
            'option_c': 'option C',
            'option_d': 'option D',
            'correct': 'correct answer (A/B/C/D)',
            'explanation': 'explanation'
        }
        
        bot.reply_to(
            message,
            f"Enter new value for {field_names[field_map[field_num]]}:\n\nType /cancel to cancel."
        )
        return True
    
    elif step == 'enter_new_value':
        field = state.get('editing_field')
        selected_q = state.get('selected_question')
        selected_index = state.get('selected_index')
        
        new_value = message.text.strip()
        
        if field == 'correct':
            new_value = new_value.upper()
            if new_value not in ['A', 'B', 'C', 'D']:
                bot.reply_to(message, "❌ Invalid! Correct answer must be A, B, C, or D.")
                return True
        
        # Update the question
        if field == 'question':
            selected_q['question'] = new_value
        elif field == 'option_a':
            selected_q['options'][0] = new_value
        elif field == 'option_b':
            selected_q['options'][1] = new_value
        elif field == 'option_c':
            selected_q['options'][2] = new_value
        elif field == 'option_d':
            selected_q['options'][3] = new_value
        elif field == 'correct':
            selected_q['correct'] = new_value
        elif field == 'explanation':
            selected_q['explanation'] = new_value
        
        # Save to database
        questions = load_questions(topic)
        questions[selected_index] = selected_q
        save_questions(topic, questions)
        
        bot.reply_to(
            message,
            f"✅ *Question updated successfully!*\n\n"
            f"Field '{field}' has been updated.\n\n"
            f"Use /admin to manage more questions.",
            parse_mode='Markdown'
        )
        
        # Clear admin state
        del admin_states[user_id]
        return True
    
    return False

def start_delete_question(bot, call, topic):
    """Start deleting a question"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    questions = load_questions(topic)
    
    if not questions:
        bot.answer_callback_query(call.id, "No questions available to delete!")
        return
    
    admin_states[user_id] = {
        'action': 'deleting_question',
        'topic': topic,
        'step': 'select_question',
        'questions': questions
    }
    
    text = f"🗑️ *Delete Question - {TOPICS.get(topic, {}).get('name', topic)}*\n\n"
    text += "Select a question to delete:\n\n"
    
    for i, q in enumerate(questions[:20], 1):
        text += f"{i}. {q['question'][:50]}...\n"
    
    if len(questions) > 20:
        text += f"\n... and {len(questions) - 20} more questions\n"
    
    text += "\nSend the question number to delete.\nType /cancel to cancel."
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ Cancel", callback_data="cancel"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def handle_delete_question(bot, message):
    """Handle question deletion"""
    user_id = message.from_user.id
    
    if user_id not in admin_states:
        return False
    
    state = admin_states[user_id]
    if state.get('action') != 'deleting_question':
        return False
    
    if state.get('step') == 'select_question':
        try:
            q_num = int(message.text.strip()) - 1
            questions = state.get('questions', [])
            topic = state.get('topic')
            
            if 0 <= q_num < len(questions):
                selected_q = questions[q_num]
                
                # Confirm deletion
                text = f"⚠️ *Confirm Deletion*\n\n"
                text += f"Are you sure you want to delete this question?\n\n"
                text += f"📝 Question: {selected_q['question'][:100]}...\n\n"
                text += f"Reply with 'YES' to confirm, or 'NO' to cancel."
                
                state['step'] = 'confirm'
                state['selected_index'] = q_num
                admin_states[user_id] = state
                
                bot.reply_to(message, text, parse_mode='Markdown')
            else:
                bot.reply_to(message, f"❌ Invalid number! Please send a number between 1 and {len(questions)}")
        except ValueError:
            bot.reply_to(message, "❌ Please send a valid number!")
        
        return True
    
    elif state.get('step') == 'confirm':
        confirmation = message.text.strip().upper()
        topic = state.get('topic')
        selected_index = state.get('selected_index')
        
        if confirmation == 'YES':
            questions = load_questions(topic)
            deleted_q = questions.pop(selected_index)
            save_questions(topic, questions)
            
            bot.reply_to(
                message,
                f"✅ *Question deleted successfully!*\n\n"
                f"Deleted: {deleted_q['question'][:100]}...\n\n"
                f"Use /admin to manage more questions.",
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(message, "❌ Deletion cancelled.")
        
        # Clear admin state
        del admin_states[user_id]
        return True
    
    return False

def show_daily_quiz_admin(bot, call):
    """Show daily quiz admin panel"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    daily_data = load_daily_quiz()
    today = datetime.now().strftime("%Y-%m-%d")
    current_topic = daily_data.get('topic', 'Not set')
    current_date = daily_data.get('date', 'Never')
    
    text = f"""
📅 *DAILY QUIZ ADMIN*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📆 *Today's Date:* {today}
📚 *Current Topic:* {current_topic.capitalize() if current_topic != 'Not set' else 'Not set'}
📅 *Last Set:* {current_date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Actions:*
• Set today's daily quiz topic
• View today's participants
• Reset daily quiz

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 *Select an action below*
"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("📚 Set Topic", callback_data="admin_set_daily_topic"),
        InlineKeyboardButton("👥 View Participants", callback_data="admin_daily_participants"),
        InlineKeyboardButton("🔄 Reset Daily Quiz", callback_data="admin_reset_daily"),
        InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_back")
    ]
    
    markup.add(*buttons)
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def set_daily_quiz_topic(bot, call):
    """Start setting daily quiz topic"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    admin_states[user_id] = {
        'action': 'setting_daily_topic',
        'step': 'select_topic'
    }
    
    text = f"📅 *Set Daily Quiz Topic*\n\n"
    text += "Select a topic for today's daily quiz:\n\n"
    
    for topic_id in TOPIC_ORDER:
        topic_name = TOPICS.get(topic_id, {}).get('name', topic_id)
        q_count = get_questions_count(topic_id)
        text += f"• {topic_name}: {q_count} questions\n"
    
    text += "\nSend the topic name (e.g., 'maths', 'science', 'gk')\nType /cancel to cancel."
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        parse_mode='Markdown'
    )

def handle_set_daily_topic(bot, message):
    """Handle setting daily quiz topic"""
    user_id = message.from_user.id
    
    if user_id not in admin_states:
        return False
    
    state = admin_states[user_id]
    if state.get('action') != 'setting_daily_topic':
        return False
    
    topic_input = message.text.strip().lower()
    
    # Find matching topic
    selected_topic = None
    for topic_id in TOPIC_ORDER:
        if topic_input == topic_id or topic_input == TOPICS.get(topic_id, {}).get('name', '').lower():
            selected_topic = topic_id
            break
    
    if not selected_topic:
        bot.reply_to(
            message,
            f"❌ Invalid topic! Available topics: {', '.join(TOPIC_ORDER)}\n\nType /cancel to cancel."
        )
        return True
    
    # Get random questions from this topic
    all_questions = load_questions(selected_topic)
    
    if len(all_questions) < 5:
        bot.reply_to(
            message,
            f"❌ Not enough questions in {TOPICS.get(selected_topic, {}).get('name')}!\n"
            f"Need at least 5 questions, but only {len(all_questions)} available.\n\n"
            f"Please add more questions first."
        )
        del admin_states[user_id]
        return True
    
    # Select 5 random questions
    import random
    selected_questions = random.sample(all_questions, min(5, len(all_questions)))
    
    # Save daily quiz
    daily_data = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'topic': selected_topic,
        'questions': selected_questions,
        'participants': {}
    }
    save_daily_quiz(daily_data)
    
    bot.reply_to(
        message,
        f"✅ *Daily Quiz Set Successfully!*\n\n"
        f"📚 Topic: {TOPICS.get(selected_topic, {}).get('name')}\n"
        f"📝 Questions: 5 random questions\n"
        f"📅 Date: {daily_data['date']}\n\n"
        f"Users can now take the daily quiz using /daily",
        parse_mode='Markdown'
    )
    
    # Clear admin state
    del admin_states[user_id]
    return True

def show_user_management(bot, call):
    """Show user management panel"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    total_users = get_total_users_count()
    
    text = f"""
👥 *USER MANAGEMENT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Total Users:* {total_users}

*Available Actions:*
• View all users
• Search user by ID
• Reset user data
• View user statistics
• Block/Unblock user

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 *Select an action below*
"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("📋 List All Users", callback_data="admin_list_users"),
        InlineKeyboardButton("🔍 Search User", callback_data="admin_search_user"),
        InlineKeyboardButton("🔄 Reset User Data", callback_data="admin_reset_user"),
        InlineKeyboardButton("📊 User Stats", callback_data="admin_user_stats"),
        InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_back")
    ]
    
    markup.add(*buttons)
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def list_all_users(bot, call):
    """List all users (paginated)"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    all_users = get_all_users()
    
    if not all_users:
        text = "📋 *User List*\n\nNo users found."
    else:
        text = f"📋 *User List* (Total: {len(all_users)})\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for i, uid in enumerate(all_users[:30], 1):
            user_data = load_user(uid)
            name = user_data.get('first_name', 'Unknown')
            username = user_data.get('username', 'no username')
            quizzes = user_data.get('total_quizzes', 0)
            text += f"{i}. *{name}*\n"
            text += f"   🆔 ID: {uid}\n"
            text += f"   👤 @{username}\n"
            text += f"   📊 Quizzes: {quizzes}\n\n"
        
        if len(all_users) > 30:
            text += f"\n... and {len(all_users) - 30} more users.\n"
            text += "Use search to find specific users."
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to User Management", callback_data="admin_users"))
    markup.add(InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_back"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_bot_settings(bot, call):
    """Show bot settings panel"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    settings = load_settings()
    
    text = f"""
⚙️ *BOT SETTINGS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 *Bot Status:* {'🟢 Active' if settings.get('bot_active', True) else '🔴 Maintenance'}
🔧 *Maintenance Mode:* {'🔴 ON' if settings.get('maintenance_mode', False) else '🟢 OFF'}
📢 *Daily Quiz:* {'✅ Enabled' if settings.get('daily_quiz_enabled', True) else '❌ Disabled'}
⏰ *Reminder Time:* {settings.get('reminder_time', '09:00')}
📝 *Default Quiz Type:* {settings.get('default_quiz_type', 'quick')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Toggle Settings:*
• Turn bot ON/OFF
• Enable/Disable maintenance mode
• Enable/Disable daily quiz
• Change reminder time

━━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 *Select a setting to change*
"""
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    bot_status_text = "🔴 Turn OFF Bot" if settings.get('bot_active', True) else "🟢 Turn ON Bot"
    maintenance_text = "🔴 Enable Maintenance" if not settings.get('maintenance_mode', False) else "🟢 Disable Maintenance"
    daily_text = "❌ Disable Daily Quiz" if settings.get('daily_quiz_enabled', True) else "✅ Enable Daily Quiz"
    
    buttons = [
        InlineKeyboardButton(bot_status_text, callback_data="admin_toggle_bot"),
        InlineKeyboardButton(maintenance_text, callback_data="admin_toggle_maintenance"),
        InlineKeyboardButton(daily_text, callback_data="admin_toggle_daily"),
        InlineKeyboardButton("⏰ Set Reminder Time", callback_data="admin_set_reminder"),
        InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_back")
    ]
    
    markup.add(*buttons)
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def handle_admin_callback(bot, call):
    """Handle all admin panel callbacks"""
    user_id = call.from_user.id
    
    # Check admin access
    if user_id not in ADMIN_IDS and user_id != OWNER_ID:
        bot.answer_callback_query(call.id, "You are not authorized!")
        return
    
    data = call.data
    
    if data == "admin_back":
        show_admin_panel(bot, call.message)
    
    elif data == "admin_close":
        bot.delete_message(call.message.chat.id, call.message.message_id)
    
    elif data == "admin_stats":
        show_bot_stats(bot, call)
    
    elif data == "admin_questions":
        show_questions_menu(bot, call)
    
    elif data.startswith("admin_topic_"):
        topic = data.replace("admin_topic_", "")
        show_topic_questions_menu(bot, call, topic)
    
    elif data.startswith("admin_add_"):
        topic = data.replace("admin_add_", "")
        start_add_question(bot, call, topic)
    
    elif data.startswith("admin_edit_"):
        topic = data.replace("admin_edit_", "")
        start_edit_question(bot, call, topic)
    
    elif data.startswith("admin_delete_"):
        topic = data.replace("admin_delete_", "")
        start_delete_question(bot, call, topic)
    
    elif data == "admin_daily_quiz":
        show_daily_quiz_admin(bot, call)
    
    elif data == "admin_set_daily_topic":
        set_daily_quiz_topic(bot, call)
    
    elif data == "admin_broadcast":
        from broadcast_system import start_broadcast_from_admin
        start_broadcast_from_admin(bot, call)
    
    elif data == "admin_users":
        show_user_management(bot, call)
    
    elif data == "admin_list_users":
        list_all_users(bot, call)
    
    elif data == "admin_settings":
        show_bot_settings(bot, call)
    
    elif data == "admin_toggle_bot":
        settings = load_settings()
        settings['bot_active'] = not settings.get('bot_active', True)
        save_settings(settings)
        show_bot_settings(bot, call)
        bot.answer_callback_query(call.id, f"Bot turned {'ON' if settings['bot_active'] else 'OFF'}")
    
    elif data == "admin_toggle_maintenance":
        settings = load_settings()
        settings['maintenance_mode'] = not settings.get('maintenance_mode', False)
        save_settings(settings)
        show_bot_settings(bot, call)
        bot.answer_callback_query(call.id, f"Maintenance mode {'ON' if settings['maintenance_mode'] else 'OFF'}")
    
    elif data == "admin_toggle_daily":
        settings = load_settings()
        settings['daily_quiz_enabled'] = not settings.get('daily_quiz_enabled', True)
        save_settings(settings)
        show_bot_settings(bot, call)
        bot.answer_callback_query(call.id, f"Daily quiz {'enabled' if settings['daily_quiz_enabled'] else 'disabled'}")
    
    elif data == "admin_update_lb":
        from database import update_leaderboard
        update_leaderboard()
        bot.answer_callback_query(call.id, "Leaderboard updated successfully!")
        show_admin_panel(bot, call.message)
    
    elif data == "admin_export":
        export_all_data(bot, call)
    
    else:
        bot.answer_callback_query(call.id, "Feature coming soon!")

def export_all_data(bot, call):
    """Export all bot data"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    bot.edit_message_text(
        "📤 *Exporting Data...*\n\nPlease wait, this may take a moment.",
        chat_id,
        message_id,
        parse_mode='Markdown'
    )
    
    # Create export data
    export_data = {
        'export_date': get_current_datetime(),
        'bot_name': BOT_NAME,
        'bot_version': BOT_VERSION,
        'total_users': get_total_users_count(),
        'topics': {},
        'users': {}
    }
    
    # Export questions
    for topic_id in TOPIC_ORDER:
        export_data['topics'][topic_id] = {
            'name': TOPICS.get(topic_id, {}).get('name', topic_id),
            'questions': load_questions(topic_id),
            'chapters': load_chapters(topic_id)
        }
    
    # Export limited user data (without sensitive info)
    all_users = get_all_users()
    for uid in all_users[:100]:  # Limit to 100 users for export
        user_data = load_user(uid)
        export_data['users'][uid] = {
            'first_name': user_data.get('first_name', ''),
            'username': user_data.get('username', ''),
            'total_quizzes': user_data.get('total_quizzes', 0),
            'total_correct': user_data.get('total_correct', 0),
            'accuracy': user_data.get('accuracy', 0),
            'joined_date': user_data.get('joined_date', '')
        }
    
    # Save to file
    export_file = f"brain_buds_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = os.path.join('/tmp', export_file)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    # Send file
    with open(file_path, 'rb') as f:
        bot.send_document(chat_id, f, caption=f"📊 *Export Data*\nDate: {get_current_datetime()}\nTotal Users: {len(export_data['users'])}", parse_mode='Markdown')
    
    # Clean up
    os.remove(file_path)