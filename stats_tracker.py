import os
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOPICS, BOT_NAME
from database import load_user, save_user, get_all_users, get_total_users_count
from utils.helpers import format_user_stats, get_grade, create_progress_bar
from utils.time_utils import get_current_date, days_between, format_date

# ============================================
# STATS TRACKER - User Statistics Management
# ============================================

def show_user_stats(bot, message):
    """Show user's statistics"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    user_data = load_user(user_id)
    
    # Get or create message object for proper editing
    if hasattr(message, 'message_id'):
        message_id = message.message_id
    else:
        message_id = None
    
    stats_text = build_stats_text(user_data)
    markup = get_stats_keyboard(user_data)
    
    if message_id:
        try:
            bot.edit_message_text(
                stats_text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except:
            bot.send_message(
                chat_id,
                stats_text,
                reply_markup=markup,
                parse_mode='Markdown'
            )
    else:
        bot.send_message(
            chat_id,
            stats_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

def build_stats_text(user_data):
    """Build statistics text from user data"""
    
    # Basic stats
    total_quizzes = user_data.get('total_quizzes', 0)
    total_questions = user_data.get('total_questions', 0)
    total_correct = user_data.get('total_correct', 0)
    total_wrong = user_data.get('total_wrong', 0)
    total_skipped = user_data.get('total_skipped', 0)
    
    accuracy = user_data.get('accuracy', 0)
    best_score = user_data.get('best_score', 0)
    average_score = user_data.get('average_score', 0)
    
    # Streak info
    current_streak = user_data.get('current_streak', 0)
    longest_streak = user_data.get('longest_streak', 0)
    daily_streak = user_data.get('daily_quiz_streak', 0)
    
    # Level and XP
    level = user_data.get('level', 1)
    xp = user_data.get('xp', 0)
    xp_needed = level * 500
    xp_progress = (xp / xp_needed * 100) if xp_needed > 0 else 0
    
    # Coins
    coins = user_data.get('coins', 0)
    
    # Grade based on accuracy
    grade_info = get_grade(accuracy)
    
    stats_text = f"""
📊 *YOUR STATISTICS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 *Profile*
• Username: {user_data.get('username', 'Not set')}
• Joined: {format_date(user_data.get('joined_date', get_current_date())[:10]) if user_data.get('joined_date') else 'Recently'}
• Level: {level} ⭐
• XP: {xp}/{xp_needed} ({xp_progress:.0f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 *Performance*
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Quizzes: {total_quizzes}
• Total Questions: {total_questions}
• ✅ Correct: {total_correct}
• ❌ Wrong: {total_wrong}
• ⏭️ Skipped: {total_skipped}
• 🎯 Accuracy: {accuracy}%
• 🏆 Best Score: {best_score}/{total_questions if total_questions > 0 else 1}
• 📊 Average Score: {average_score}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 *Streaks*
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Current Streak: {current_streak} days
• Longest Streak: {longest_streak} days
• Daily Quiz Streak: {daily_streak} days

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 *Rewards*
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Coins: {coins} 🪙
• Grade: {grade_info['grade']} {grade_info['emoji']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 *"{grade_info['message']}"*
"""
    
    # Add progress bar for level
    progress_bar = create_progress_bar(xp_progress, 10)
    stats_text += f"\n📊 *Level Progress*\n{progress_bar} {xp_progress:.0f}%\n"
    
    # Add recent achievements if any
    achievements = user_data.get('achievements', [])
    if achievements:
        stats_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        stats_text += "🏅 *Recent Achievements*\n"
        for ach in achievements[-3:]:
            stats_text += f"• {ach}\n"
    
    return stats_text

def get_stats_keyboard(user_data):
    """Get inline keyboard for stats options"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("📊 Topic-wise Stats", callback_data="stats_topics"),
        InlineKeyboardButton("📅 Weekly Report", callback_data="stats_weekly"),
        InlineKeyboardButton("🏆 Achievements", callback_data="stats_achievements"),
        InlineKeyboardButton("📈 Recent Quizzes", callback_data="stats_recent"),
        InlineKeyboardButton("⚙️ Settings", callback_data="stats_settings"),
        InlineKeyboardButton("◀️ Back to Menu", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    return markup

def show_topic_stats(bot, call):
    """Show topic-wise statistics"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    user_data = load_user(user_id)
    topic_stats = user_data.get('topic_stats', {})
    
    if not topic_stats:
        text = "📊 *Topic-wise Statistics*\n\n"
        text += "No topic statistics available yet.\n"
        text += "Take quizzes on different topics to see your performance!"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Back to Stats", callback_data="stats_back"))
        markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
        
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    text = "📊 *TOPIC-WISE PERFORMANCE*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Sort topics by accuracy
    topic_performance = []
    for topic_id, stats in topic_stats.items():
        attempts = stats.get('attempts', 0)
        correct = stats.get('total_correct', 0)
        total = stats.get('total_questions', 0)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        topic_name = TOPICS.get(topic_id, {}).get('name', topic_id)
        topic_performance.append({
            'name': topic_name,
            'id': topic_id,
            'attempts': attempts,
            'correct': correct,
            'total': total,
            'accuracy': accuracy
        })
    
    # Sort by accuracy descending
    topic_performance.sort(key=lambda x: x['accuracy'], reverse=True)
    
    for topic in topic_performance:
        # Progress bar
        bar = create_progress_bar(topic['accuracy'], 10)
        
        # Emoji based on accuracy
        if topic['accuracy'] >= 80:
            emoji = "🟢"
        elif topic['accuracy'] >= 60:
            emoji = "🟡"
        elif topic['accuracy'] >= 40:
            emoji = "🟠"
        else:
            emoji = "🔴"
        
        text += f"{emoji} *{topic['name']}*\n"
        text += f"   {bar} {topic['accuracy']:.1f}%\n"
        text += f"   📊 {topic['correct']}/{topic['total']} correct\n"
        text += f"   🎮 {topic['attempts']} attempts\n\n"
    
    # Find weakest topic
    weakest = min(topic_performance, key=lambda x: x['accuracy']) if topic_performance else None
    if weakest:
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"💪 *Focus Area:* {weakest['name']}\n"
        text += f"   Current accuracy: {weakest['accuracy']:.1f}%\n"
        text += "   Practice this topic to improve!"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Stats", callback_data="stats_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_weekly_report(bot, call):
    """Show weekly performance report"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    user_data = load_user(user_id)
    quiz_history = user_data.get('quiz_history', [])
    
    # Get last 7 days of quizzes
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    weekly_quizzes = [q for q in quiz_history if q.get('date', '') >= week_ago]
    
    if not weekly_quizzes:
        text = "📅 *Weekly Report*\n\n"
        text += "No quizzes taken in the last 7 days.\n"
        text += "Take some quizzes to see your weekly report!"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Back to Stats", callback_data="stats_back"))
        
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    total_questions = sum(q.get('total', 0) for q in weekly_quizzes)
    total_correct = sum(q.get('score', 0) for q in weekly_quizzes)
    avg_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    text = "📅 *WEEKLY PERFORMANCE REPORT*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📆 Period: Last 7 days\n"
    text += f"🎮 Quizzes taken: {len(weekly_quizzes)}\n"
    text += f"📝 Questions answered: {total_questions}\n"
    text += f"✅ Correct answers: {total_correct}\n"
    text += f"📈 Average accuracy: {avg_percentage:.1f}%\n\n"
    
    # Day by day breakdown
    text += "*Daily Breakdown*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_scores = {day: [] for day in days}
    
    for quiz in weekly_quizzes:
        try:
            quiz_date = datetime.strptime(quiz.get('date', ''), "%Y-%m-%d")
            day_name = days[quiz_date.weekday()]
            day_scores[day_name].append(quiz.get('percentage', 0))
        except:
            pass
    
    for day in days:
        if day_scores[day]:
            avg = sum(day_scores[day]) / len(day_scores[day])
            # Progress bar for the day
            bar = create_progress_bar(avg, 10)
            text += f"• *{day}*: {bar} {avg:.1f}%\n"
        else:
            text += f"• *{day}*: ❌ No quizzes\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Improvement trend
    if len(weekly_quizzes) >= 2:
        first_half = weekly_quizzes[:len(weekly_quizzes)//2]
        second_half = weekly_quizzes[len(weekly_quizzes)//2:]
        
        first_avg = sum(q.get('percentage', 0) for q in first_half) / len(first_half) if first_half else 0
        second_avg = sum(q.get('percentage', 0) for q in second_half) / len(second_half) if second_half else 0
        
        if second_avg > first_avg:
            text += "📈 *Trend:* Improving! Keep going! 🔥\n"
            improvement = second_avg - first_avg
            text += f"   +{improvement:.1f}% improvement\n"
        elif second_avg < first_avg:
            text += "📉 *Trend:* Slipping. Stay consistent! 💪\n"
            improvement = first_avg - second_avg
            text += f"   -{improvement:.1f}% decline\n"
        else:
            text += "📊 *Trend:* Consistent. Good job!\n"
    
    # Recommendation based on performance
    text += "\n💡 *Recommendation*\n"
    if avg_percentage < 50:
        text += "• Start with Practice Mode\n"
        text += "• Take more quizzes daily\n"
        text += "• Review wrong answers carefully\n"
    elif avg_percentage < 70:
        text += "• Focus on weak topics\n"
        text += "• Try Quick Quiz for revision\n"
        text += "• Set a daily quiz goal\n"
    elif avg_percentage < 90:
        text += "• Challenge with Exam Mode\n"
        text += "• Try to beat your best score\n"
        text += "• Maintain daily streak\n"
    else:
        text += "• Excellent performance!\n"
        text += "• Try different topics\n"
        text += "• Help others learn\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Stats", callback_data="stats_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_achievements(bot, call):
    """Show user achievements and badges"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    user_data = load_user(user_id)
    achievements = user_data.get('achievements', [])
    
    # Define all possible achievements
    all_achievements = {
        'first_quiz': {'name': '🌟 First Step', 'desc': 'Completed first quiz', 'icon': '🎯'},
        'quiz_master': {'name': '🏆 Quiz Master', 'desc': 'Completed 50 quizzes', 'icon': '🏆'},
        'perfect_score': {'name': '💯 Perfect!', 'desc': 'Got 100% in a quiz', 'icon': '⭐'},
        'streak_7': {'name': '🔥 Week Warrior', 'desc': '7 day streak', 'icon': '🔥'},
        'streak_30': {'name': '⚡ Month Master', 'desc': '30 day streak', 'icon': '⚡'},
        'topic_expert': {'name': '📚 Topic Expert', 'desc': 'Mastered a topic', 'icon': '📚'},
        'speed_demon': {'name': '⚡ Speed Demon', 'desc': 'Completed quiz in half time', 'icon': '🚀'},
        'accuracy_king': {'name': '🎯 Accuracy King', 'desc': '90%+ accuracy', 'icon': '🎯'},
        'daily_champ': {'name': '📅 Daily Champ', 'desc': 'Completed 7 daily quizzes', 'icon': '📅'},
        'gk_pro': {'name': '🌍 GK Pro', 'desc': 'Mastered General Knowledge', 'icon': '🌍'},
        'math_genius': {'name': '📐 Math Genius', 'desc': 'Mastered Mathematics', 'icon': '📐'},
        'science_star': {'name': '🔬 Science Star', 'desc': 'Mastered Science', 'icon': '🔬'}
    }
    
    text = "🏅 *ACHIEVEMENTS & BADGES*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if achievements:
        text += "*Earned Achievements:*\n"
        for ach in achievements:
            ach_info = all_achievements.get(ach, {'name': ach, 'desc': '', 'icon': '🏅'})
            text += f"{ach_info['icon']} *{ach_info['name']}*\n"
            text += f"   {ach_info['desc']}\n\n"
    else:
        text += "❌ *No achievements yet*\n"
        text += "Complete quizzes and challenges to earn badges!\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "*Locked Achievements:*\n\n"
    
    # Show locked achievements
    earned_set = set(achievements)
    for ach_id, ach_info in all_achievements.items():
        if ach_id not in earned_set:
            text += f"🔒 {ach_info['icon']} *{ach_info['name']}*\n"
            text += f"   {ach_info['desc']}\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💡 *Tips to earn achievements:*\n"
    text += "• Play daily to build streaks\n"
    text += "• Aim for perfect scores\n"
    text += "• Master different topics\n"
    text += "• Complete quizzes quickly\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Stats", callback_data="stats_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_recent_quizzes(bot, call):
    """Show recent quiz history"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    user_data = load_user(user_id)
    quiz_history = user_data.get('quiz_history', [])
    
    if not quiz_history:
        text = "📋 *Recent Quizzes*\n\n"
        text += "No quizzes taken yet.\n"
        text += "Take your first quiz using /menu!"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("◀️ Back to Stats", callback_data="stats_back"))
        
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    text = "📋 *RECENT QUIZZES*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Show last 10 quizzes
    for i, quiz in enumerate(quiz_history[-10:][::-1], 1):
        date = quiz.get('date', 'Unknown')
        topic = quiz.get('topic', 'Unknown')
        score = quiz.get('score', 0)
        total = quiz.get('total', 0)
        percentage = quiz.get('percentage', 0)
        
        # Emoji based on score
        if percentage >= 80:
            emoji = "🟢"
        elif percentage >= 60:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        topic_name = TOPICS.get(topic, {}).get('name', topic.capitalize())
        text += f"{i}. {emoji} *{topic_name}*\n"
        text += f"   📅 {date}\n"
        text += f"   📊 Score: {score}/{total} ({percentage:.0f}%)\n\n"
    
    # Calculate improvement trend
    if len(quiz_history) >= 3:
        last_three = quiz_history[-3:]
        avg_last_three = sum(q.get('percentage', 0) for q in last_three) / 3
        prev_three = quiz_history[-6:-3] if len(quiz_history) >= 6 else quiz_history[:3]
        if prev_three:
            avg_prev_three = sum(q.get('percentage', 0) for q in prev_three) / len(prev_three)
            if avg_last_three > avg_prev_three:
                text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                text += "📈 *You're improving!* Keep going! 🔥\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Stats", callback_data="stats_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_settings(bot, call):
    """Show user settings"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    user_data = load_user(user_id)
    settings = user_data.get('settings', {})
    
    notifications = settings.get('notifications', True)
    difficulty = settings.get('difficulty', 'medium')
    language = settings.get('language', 'english')
    
    text = "⚙️ *USER SETTINGS*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += f"🔔 *Notifications:* {'ON ✅' if notifications else 'OFF ❌'}\n"
    text += f"📝 *Default Difficulty:* {difficulty.capitalize()}\n"
    text += f"🌐 *Language:* {language.capitalize()}\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "Tap buttons below to change settings:\n"
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton(
            f"🔔 {'Turn OFF' if notifications else 'Turn ON'} Notifications", 
            callback_data="settings_notifications"
        ),
        InlineKeyboardButton(
            f"📝 Difficulty: {difficulty.capitalize()}", 
            callback_data="settings_difficulty"
        ),
        InlineKeyboardButton(
            f"🌐 Language: {language.capitalize()}", 
            callback_data="settings_language"
        ),
        InlineKeyboardButton("◀️ Back to Stats", callback_data="stats_back"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def handle_settings_callback(bot, call):
    """Handle settings button callbacks"""
    user_id = call.from_user.id
    user_data = load_user(user_id)
    settings = user_data.get('settings', {})
    
    if call.data == "settings_notifications":
        # Toggle notifications
        current = settings.get('notifications', True)
        settings['notifications'] = not current
        user_data['settings'] = settings
        save_user(user_id, user_data)
        bot.answer_callback_query(call.id, f"Notifications turned {'ON' if not current else 'OFF'}")
        show_settings(bot, call)
    
    elif call.data == "settings_difficulty":
        # Cycle through difficulties
        difficulties = ['easy', 'medium', 'hard']
        current = settings.get('difficulty', 'medium')
        next_idx = (difficulties.index(current) + 1) % len(difficulties)
        settings['difficulty'] = difficulties[next_idx]
        user_data['settings'] = settings
        save_user(user_id, user_data)
        bot.answer_callback_query(call.id, f"Difficulty set to {difficulties[next_idx].capitalize()}")
        show_settings(bot, call)
    
    elif call.data == "settings_language":
        # Cycle through languages
        languages = ['english', 'hindi']
        current = settings.get('language', 'english')
        next_idx = (languages.index(current) + 1) % len(languages)
        settings['language'] = languages[next_idx]
        user_data['settings'] = settings
        save_user(user_id, user_data)
        bot.answer_callback_query(call.id, f"Language set to {languages[next_idx].capitalize()}")
        show_settings(bot, call)
    
    elif call.data == "stats_back":
        show_user_stats(bot, call.message)
    
    elif call.data == "stats_topics":
        show_topic_stats(bot, call)
    
    elif call.data == "stats_weekly":
        show_weekly_report(bot, call)
    
    elif call.data == "stats_achievements":
        show_achievements(bot, call)
    
    elif call.data == "stats_recent":
        show_recent_quizzes(bot, call)
    
    elif call.data == "stats_settings":
        show_settings(bot, call)

def check_and_update_streak(user_id):
    """Check and update user streak"""
    user_data = load_user(user_id)
    last_played = user_data.get('last_quiz_date', '')
    today = get_current_date()
    
    if last_played == today:
        return  # Already updated today
    
    if last_played:
        days_diff = days_between(last_played, today)
        if days_diff == 1:
            # Consecutive day
            current_streak = user_data.get('current_streak', 0) + 1
            user_data['current_streak'] = current_streak
            
            # Update longest streak
            if current_streak > user_data.get('longest_streak', 0):
                user_data['longest_streak'] = current_streak
                
            # Check for streak achievements
            if current_streak == 7:
                add_achievement(user_id, 'streak_7')
            elif current_streak == 30:
                add_achievement(user_id, 'streak_30')
        elif days_diff > 1:
            # Streak broken
            user_data['current_streak'] = 0
    
    user_data['last_quiz_date'] = today
    save_user(user_id, user_data)

def add_achievement(user_id, achievement_id):
    """Add an achievement to user"""
    user_data = load_user(user_id)
    achievements = user_data.get('achievements', [])
    
    if achievement_id not in achievements:
        achievements.append(achievement_id)
        user_data['achievements'] = achievements
        save_user(user_id, user_data)
        return True
    return False

def update_user_level(user_id):
    """Update user level based on XP"""
    user_data = load_user(user_id)
    xp = user_data.get('xp', 0)
    level = (xp // 500) + 1
    
    if level != user_data.get('level', 1):
        user_data['level'] = level
        save_user(user_id, user_data)
        return True
    return False