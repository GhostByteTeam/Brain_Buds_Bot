from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOPICS, GRADES
from utils.helpers import get_grade, format_time
from utils.time_utils import get_current_date
from database import update_user_stats, save_user, load_user

# ============================================
# RESULT HANDLER - Quiz Results Display
# ============================================

def show_quiz_result(bot, chat_id, user_id, result, message_id=None):
    """Display quiz result to user"""
    
    # Get grade information
    grade_info = get_grade(result['percentage'])
    
    # Build result message
    result_text = build_result_message(result, grade_info)
    
    # Create inline buttons for next actions
    markup = get_result_action_buttons(result['topic'], result['chapter_id'])
    
    # Send or edit message
    if message_id:
        try:
            bot.edit_message_text(
                result_text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except:
            bot.send_message(
                chat_id,
                result_text,
                reply_markup=markup,
                parse_mode='Markdown'
            )
    else:
        bot.send_message(
            chat_id,
            result_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    
    # Also send wrong answers separately if there are many
    if result.get('wrong_answers') and len(result['wrong_answers']) > 0:
        send_wrong_answers_review(bot, chat_id, result['wrong_answers'], result['topic'], result['chapter_id'])

def build_result_message(result, grade_info):
    """Build the result message text"""
    
    topic_name = TOPICS.get(result['topic'], {}).get('name', result['topic'].capitalize())
    
    # Get quiz type name
    quiz_type_names = {
        'quick': 'Quick Quiz',
        'full': 'Full Test',
        'practice': 'Practice Mode',
        'exam': 'Exam Mode'
    }
    quiz_type_name = quiz_type_names.get(result['quiz_type'], 'Quiz')
    
    result_text = f"""
🎉 *QUIZ COMPLETE!* 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 *Topic:* {topic_name}
📝 *Mode:* {quiz_type_name}
⏱️ *Time Taken:* {format_time(result['time_taken'])}
📅 *Date:* {result['date']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *YOUR SCORE*
✅ Correct: {result['correct']}
❌ Wrong: {result['wrong']}
⏭️ Skipped: {result['skipped']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 *Total:* {result['correct']}/{result['total']} ({result['percentage']}%)

⭐ *Grade:* {grade_info['grade']} {grade_info['emoji']}
💬 *Message:* {grade_info['message']}

🏆 *Total Points:* {result['total_score']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Add performance tips based on grade
    if result['percentage'] >= 90:
        result_text += "\n🌟 *Excellent!* You're a quiz master!\nKeep up the great work!\n"
    elif result['percentage'] >= 70:
        result_text += "\n👍 *Good job!* A little more practice\nand you'll be perfect!\n"
    elif result['percentage'] >= 50:
        result_text += "\n📚 *Keep practicing!* Review the wrong answers\nand try again to improve.\n"
    else:
        result_text += "\n💪 *Don't give up!* Practice makes perfect.\nReview and try the quiz again!\n"
    
    return result_text

def get_result_action_buttons(topic, chapter_id):
    """Get inline buttons for post-quiz actions"""
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

def send_wrong_answers_review(bot, chat_id, wrong_answers, topic, chapter_id):
    """Send detailed review of wrong answers"""
    if not wrong_answers:
        return
    
    review_text = "❌ *WRONG ANSWERS REVIEW*\n"
    review_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, wrong in enumerate(wrong_answers[:5], 1):
        review_text += f"*{i}. {wrong['question']}*\n"
        review_text += f"📝 Your answer: {wrong['user_answer']}\n"
        review_text += f"✅ Correct answer: {wrong['correct_answer']}\n"
        review_text += f"📖 Explanation: {wrong['explanation']}\n\n"
        review_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if len(wrong_answers) > 5:
        review_text += f"\n... and {len(wrong_answers) - 5} more wrong answers.\n"
        review_text += "Take the retest to practice them!\n"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Take Retest", callback_data=f"retest_{topic}_{chapter_id}"))
    
    bot.send_message(
        chat_id,
        review_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

def show_detailed_analysis(bot, chat_id, user_id, topic=None):
    """Show detailed performance analysis for a user"""
    user_data = load_user(user_id)
    
    analysis_text = "📊 *DETAILED PERFORMANCE ANALYSIS*\n"
    analysis_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Overall stats
    total_quizzes = user_data.get('total_quizzes', 0)
    total_correct = user_data.get('total_correct', 0)
    total_questions = user_data.get('total_questions', 0)
    accuracy = user_data.get('accuracy', 0)
    
    analysis_text += f"*Overall Performance*\n"
    analysis_text += f"• Quizzes: {total_quizzes}\n"
    analysis_text += f"• Accuracy: {accuracy}%\n"
    analysis_text += f"• Best Score: {user_data.get('best_score', 0)}\n"
    analysis_text += f"• Current Streak: {user_data.get('current_streak', 0)} days 🔥\n\n"
    
    # Topic-wise analysis
    topic_stats = user_data.get('topic_stats', {})
    if topic_stats:
        analysis_text += "*Topic-wise Performance*\n"
        analysis_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        for topic_id, stats in topic_stats.items():
            topic_name = TOPICS.get(topic_id, {}).get('name', topic_id)
            attempts = stats.get('attempts', 0)
            correct = stats.get('total_correct', 0)
            total = stats.get('total_questions', 0)
            topic_accuracy = (correct / total * 100) if total > 0 else 0
            
            # Progress bar
            bar_length = 10
            filled = int(bar_length * topic_accuracy / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            analysis_text += f"\n*{topic_name}*\n"
            analysis_text += f"  {bar} {topic_accuracy:.1f}%\n"
            analysis_text += f"  📊 {correct}/{total} correct\n"
            analysis_text += f"  🎮 {attempts} attempts\n"
    
    # Weak areas (topics with less than 60% accuracy)
    analysis_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    analysis_text += "*Areas Needing Improvement* 📚\n"
    
    weak_areas_found = False
    for topic_id, stats in topic_stats.items():
        correct = stats.get('total_correct', 0)
        total = stats.get('total_questions', 0)
        topic_accuracy = (correct / total * 100) if total > 0 else 0
        
        if topic_accuracy < 60 and total > 0:
            weak_areas_found = True
            topic_name = TOPICS.get(topic_id, {}).get('name', topic_id)
            analysis_text += f"• {topic_name}: {topic_accuracy:.1f}%\n"
    
    if not weak_areas_found:
        analysis_text += "• Great job! No weak areas detected!\n"
        analysis_text += "  Keep practicing to maintain this! 💪\n"
    
    # Recommendations
    analysis_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    analysis_text += "*Recommendations* 💡\n"
    
    if accuracy < 50:
        analysis_text += "• Start with Practice Mode to learn\n"
        analysis_text += "• Review wrong answers carefully\n"
        analysis_text += "• Take more quizzes on weak topics\n"
    elif accuracy < 70:
        analysis_text += "• Try Quick Quiz for faster revision\n"
        analysis_text += "• Focus on topics below 60%\n"
        analysis_text += "• Take Full Tests on weekends\n"
    elif accuracy < 90:
        analysis_text += "• Challenge yourself with Exam Mode\n"
        analysis_text += "• Maintain daily streak for bonuses\n"
        analysis_text += "• Try to beat your best score\n"
    else:
        analysis_text += "• You're doing excellent!\n"
        analysis_text += "• Help others by sharing tips\n"
        analysis_text += "• Try different topics to expand knowledge\n"
    
    bot.send_message(chat_id, analysis_text, parse_mode='Markdown')

def show_weekly_report(bot, chat_id, user_id):
    """Show weekly performance report"""
    user_data = load_user(user_id)
    quiz_history = user_data.get('quiz_history', [])
    
    # Get last 7 days of quizzes
    from datetime import datetime, timedelta
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    weekly_quizzes = [q for q in quiz_history if q.get('date', '') >= week_ago]
    
    if not weekly_quizzes:
        bot.send_message(
            chat_id,
            "📊 *Weekly Report*\n\n"
            "No quizzes taken in the last 7 days.\n"
            "Take some quizzes to see your weekly report!",
            parse_mode='Markdown'
        )
        return
    
    total_questions = sum(q.get('total', 0) for q in weekly_quizzes)
    total_correct = sum(q.get('score', 0) for q in weekly_quizzes)
    avg_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    report_text = "📊 *WEEKLY PERFORMANCE REPORT*\n"
    report_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    report_text += f"📅 Period: Last 7 days\n"
    report_text += f"🎮 Quizzes taken: {len(weekly_quizzes)}\n"
    report_text += f"📝 Questions answered: {total_questions}\n"
    report_text += f"✅ Correct answers: {total_correct}\n"
    report_text += f"📈 Average accuracy: {avg_percentage:.1f}%\n\n"
    
    # Day by day breakdown
    report_text += "*Daily Breakdown*\n"
    report_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
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
            report_text += f"• {day}: {avg:.1f}% ({len(day_scores[day])} quizzes)\n"
        else:
            report_text += f"• {day}: No quizzes\n"
    
    report_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Improvement trend
    if len(weekly_quizzes) >= 2:
        first_half = weekly_quizzes[:len(weekly_quizzes)//2]
        second_half = weekly_quizzes[len(weekly_quizzes)//2:]
        
        first_avg = sum(q.get('percentage', 0) for q in first_half) / len(first_half) if first_half else 0
        second_avg = sum(q.get('percentage', 0) for q in second_half) / len(second_half) if second_half else 0
        
        if second_avg > first_avg:
            report_text += "📈 *Trend:* Improving! Keep going! 🔥\n"
        elif second_avg < first_avg:
            report_text += "📉 *Trend:* Slipping. Stay consistent! 💪\n"
        else:
            report_text += "📊 *Trend:* Consistent. Good job!\n"
    
    bot.send_message(chat_id, report_text, parse_mode='Markdown')