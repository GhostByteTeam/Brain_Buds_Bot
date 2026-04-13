from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOPICS, TOPIC_ORDER, BOT_NAME
from database import load_user, get_all_users, update_leaderboard, load_leaderboard
from utils.helpers import get_rank_emoji, create_progress_bar

# ============================================
# LEADERBOARD - Rankings and Competition
# ============================================

def show_leaderboard(bot, message):
    """Show main leaderboard with options"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Get or create message object for proper editing
    if hasattr(message, 'message_id'):
        message_id = message.message_id
    else:
        message_id = None
    
    # Update leaderboard data
    leaderboard_data = update_leaderboard()
    top_users = leaderboard_data.get('top_users', [])
    
    if not top_users:
        text = "🏆 *LEADERBOARD*\n\n"
        text += "No data available yet.\n"
        text += "Take some quizzes to appear on the leaderboard!"
    else:
        text = build_leaderboard_text(top_users, user_id)
    
    markup = get_leaderboard_keyboard()
    
    if message_id:
        try:
            bot.edit_message_text(
                text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except:
            bot.send_message(
                chat_id,
                text,
                reply_markup=markup,
                parse_mode='Markdown'
            )
    else:
        bot.send_message(
            chat_id,
            text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

def build_leaderboard_text(top_users, current_user_id):
    """Build leaderboard text"""
    text = "🏆 *GLOBAL LEADERBOARD*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "*Rank | User | Points | Level*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    user_found = False
    user_rank = None
    user_points = None
    
    for i, user in enumerate(top_users[:20], 1):
        user_id = user.get('user_id')
        name = user.get('name', 'User')[:15]
        points = user.get('total_correct', 0)
        level = user.get('level', 1)
        
        rank_emoji = get_rank_emoji(i)
        
        # Highlight current user
        if str(user_id) == str(current_user_id):
            text += f"👉 {rank_emoji} *{name}* - {points} pts (Lvl {level}) 👈\n"
            user_found = True
            user_rank = i
            user_points = points
        else:
            text += f"   {rank_emoji} {name} - {points} pts (Lvl {level})\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # If user not in top 20, show their rank
    if not user_found and current_user_id:
        # Find user's rank
        all_users = get_all_users()
        user_scores = []
        
        for uid in all_users:
            user_data = load_user(uid)
            user_scores.append({
                'user_id': uid,
                'name': user_data.get('first_name', 'User'),
                'points': user_data.get('total_correct', 0),
                'level': user_data.get('level', 1)
            })
        
        user_scores.sort(key=lambda x: x['points'], reverse=True)
        
        for i, user in enumerate(user_scores, 1):
            if str(user['user_id']) == str(current_user_id):
                text += f"\n*Your Rank:* #{i}\n"
                text += f"*Your Points:* {user['points']}\n"
                text += f"*Your Level:* {user['level']}\n"
                
                # Show next milestone
                if i > 1:
                    prev_user = user_scores[i-2] if i-2 >= 0 else None
                    if prev_user:
                        points_needed = prev_user['points'] - user['points']
                        text += f"\n📈 *Next Target:* {points_needed} more points to reach #{i-1}\n"
                break
    
    text += "\n💡 *Tip:* Play more quizzes to increase your rank!"
    
    return text

def get_leaderboard_keyboard():
    """Get inline keyboard for leaderboard options"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        InlineKeyboardButton("🏆 Overall", callback_data="leaderboard_overall"),
        InlineKeyboardButton("📊 Accuracy", callback_data="leaderboard_accuracy"),
        InlineKeyboardButton("🔥 Streaks", callback_data="leaderboard_streaks"),
        InlineKeyboardButton("📚 Topic Wise", callback_data="leaderboard_topics"),
        InlineKeyboardButton("◀️ Back to Menu", callback_data="main_menu")
    ]
    
    markup.add(*buttons)
    return markup

def show_accuracy_leaderboard(bot, call):
    """Show leaderboard based on accuracy"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    all_users = get_all_users()
    user_accuracies = []
    
    for uid in all_users:
        user_data = load_user(uid)
        accuracy = user_data.get('accuracy', 0)
        if accuracy > 0:
            user_accuracies.append({
                'user_id': uid,
                'name': user_data.get('first_name', 'User'),
                'accuracy': accuracy,
                'total_questions': user_data.get('total_questions', 0)
            })
    
    user_accuracies.sort(key=lambda x: x['accuracy'], reverse=True)
    
    text = "🎯 *ACCURACY LEADERBOARD*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "*Rank | User | Accuracy | Questions*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    user_found = False
    
    for i, user in enumerate(user_accuracies[:20], 1):
        name = user['name'][:15]
        accuracy = user['accuracy']
        total_q = user['total_questions']
        
        rank_emoji = get_rank_emoji(i)
        
        # Progress bar for accuracy
        bar = create_progress_bar(accuracy, 10)
        
        if str(user['user_id']) == str(user_id):
            text += f"👉 {rank_emoji} *{name}* - {accuracy}%\n"
            text += f"   {bar}\n"
            user_found = True
        else:
            text += f"   {rank_emoji} {name} - {accuracy}%\n"
            text += f"   {bar}\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if not user_found and user_id:
        # Find user's accuracy rank
        for i, user in enumerate(user_accuracies, 1):
            if str(user['user_id']) == str(user_id):
                text += f"\n*Your Accuracy Rank:* #{i}\n"
                text += f"*Your Accuracy:* {user['accuracy']}%\n"
                text += f"*Questions Answered:* {user['total_questions']}\n"
                break
    
    text += "\n💡 *Tip:* Review wrong answers to improve accuracy!"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Leaderboard", callback_data="leaderboard_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_streak_leaderboard(bot, call):
    """Show leaderboard based on streaks"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    all_users = get_all_users()
    user_streaks = []
    
    for uid in all_users:
        user_data = load_user(uid)
        streak = user_data.get('current_streak', 0)
        longest_streak = user_data.get('longest_streak', 0)
        
        if streak > 0 or longest_streak > 0:
            user_streaks.append({
                'user_id': uid,
                'name': user_data.get('first_name', 'User'),
                'current_streak': streak,
                'longest_streak': longest_streak
            })
    
    user_streaks.sort(key=lambda x: x['current_streak'], reverse=True)
    
    text = "🔥 *STREAK LEADERBOARD*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "*Rank | User | Current Streak | Longest*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    user_found = False
    
    for i, user in enumerate(user_streaks[:20], 1):
        name = user['name'][:15]
        current = user['current_streak']
        longest = user['longest_streak']
        
        rank_emoji = get_rank_emoji(i)
        
        # Fire emoji based on streak length
        if current >= 30:
            streak_emoji = "⚡🔥"
        elif current >= 7:
            streak_emoji = "🔥"
        elif current >= 3:
            streak_emoji = "👍"
        else:
            streak_emoji = "📅"
        
        if str(user['user_id']) == str(user_id):
            text += f"👉 {rank_emoji} *{name}* - {streak_emoji} {current} days\n"
            text += f"   (Best: {longest} days)\n"
            user_found = True
        else:
            text += f"   {rank_emoji} {name} - {streak_emoji} {current} days\n"
            text += f"   (Best: {longest} days)\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if not user_found and user_id:
        for i, user in enumerate(user_streaks, 1):
            if str(user['user_id']) == str(user_id):
                text += f"\n*Your Streak Rank:* #{i}\n"
                text += f"*Current Streak:* {user['current_streak']} days\n"
                text += f"*Longest Streak:* {user['longest_streak']} days\n"
                
                if user['current_streak'] < 7:
                    needed = 7 - user['current_streak']
                    text += f"\n📅 *Goal:* {needed} more days to get 🔥 badge!\n"
                break
    
    text += "\n💡 *Tip:* Play daily quiz to build your streak!"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Leaderboard", callback_data="leaderboard_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_topic_leaderboard(bot, call, topic=None):
    """Show topic-wise leaderboard"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if topic == "topics" or not topic:
        # Show topic selection
        markup = get_topic_leaderboard_keyboard()
        
        text = "📚 *TOPIC-WISE LEADERBOARD*\n\n"
        text += "Select a topic to see rankings:\n\n"
        
        for topic_id in TOPIC_ORDER:
            topic_name = TOPICS[topic_id]['name']
            topic_icon = TOPICS[topic_id]['icon']
            text += f"{topic_icon} {topic_name}\n"
        
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    # Show leaderboard for specific topic
    all_users = get_all_users()
    topic_scores = []
    
    for uid in all_users:
        user_data = load_user(uid)
        topic_stats = user_data.get('topic_stats', {})
        
        if topic in topic_stats:
            stats = topic_stats[topic]
            correct = stats.get('total_correct', 0)
            total = stats.get('total_questions', 0)
            accuracy = (correct / total * 100) if total > 0 else 0
            
            topic_scores.append({
                'user_id': uid,
                'name': user_data.get('first_name', 'User'),
                'correct': correct,
                'total': total,
                'accuracy': accuracy
            })
    
    topic_scores.sort(key=lambda x: x['correct'], reverse=True)
    
    topic_name = TOPICS.get(topic, {}).get('name', topic.capitalize())
    topic_icon = TOPICS.get(topic, {}).get('icon', '📚')
    
    text = f"{topic_icon} *{topic_name} LEADERBOARD*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "*Rank | User | Correct | Total | Accuracy*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    user_found = False
    
    for i, user in enumerate(topic_scores[:20], 1):
        name = user['name'][:12]
        correct = user['correct']
        total = user['total']
        accuracy = user['accuracy']
        
        rank_emoji = get_rank_emoji(i)
        
        # Accuracy emoji
        if accuracy >= 80:
            acc_emoji = "🟢"
        elif accuracy >= 60:
            acc_emoji = "🟡"
        else:
            acc_emoji = "🔴"
        
        if str(user['user_id']) == str(user_id):
            text += f"👉 {rank_emoji} *{name}* - {correct}/{total} {acc_emoji}\n"
            user_found = True
        else:
            text += f"   {rank_emoji} {name} - {correct}/{total} {acc_emoji}\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    if not user_found and user_id:
        for i, user in enumerate(topic_scores, 1):
            if str(user['user_id']) == str(user_id):
                text += f"\n*Your Rank:* #{i}\n"
                text += f"*Your Score:* {user['correct']}/{user['total']}\n"
                text += f"*Your Accuracy:* {user['accuracy']:.1f}%\n"
                break
    
    text += f"\n💡 *Tip:* Practice more {topic_name} to improve your rank!"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("◀️ Back to Topics", callback_data="leaderboard_topics"))
    markup.add(InlineKeyboardButton("◀️ Back to Leaderboard", callback_data="leaderboard_back"))
    markup.add(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def get_topic_leaderboard_keyboard():
    """Get inline keyboard for topic leaderboard selection"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    buttons = []
    for topic_id in TOPIC_ORDER:
        topic_name = TOPICS[topic_id]['name']
        topic_icon = TOPICS[topic_id]['icon']
        buttons.append(InlineKeyboardButton(
            f"{topic_icon} {topic_name}",
            callback_data=f"leaderboard_topic_{topic_id}"
        ))
    
    buttons.append(InlineKeyboardButton("◀️ Back to Leaderboard", callback_data="leaderboard_back"))
    buttons.append(InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    
    markup.add(*buttons)
    return markup

def handle_leaderboard_callback(bot, call):
    """Handle leaderboard callback queries"""
    if call.data == "leaderboard_overall":
        show_leaderboard(bot, call.message)
    
    elif call.data == "leaderboard_accuracy":
        show_accuracy_leaderboard(bot, call)
    
    elif call.data == "leaderboard_streaks":
        show_streak_leaderboard(bot, call)
    
    elif call.data == "leaderboard_topics":
        show_topic_leaderboard(bot, call, "topics")
    
    elif call.data.startswith("leaderboard_topic_"):
        topic = call.data.replace("leaderboard_topic_", "")
        show_topic_leaderboard(bot, call, topic)
    
    elif call.data == "leaderboard_back":
        show_leaderboard(bot, call.message)