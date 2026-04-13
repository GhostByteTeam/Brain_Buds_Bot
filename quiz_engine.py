import random
import time
import json
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import QUIZ_TYPES, SCORES, TOPICS
from database import (
    load_questions, get_questions_by_chapter, save_session, load_session, 
    delete_session, load_user, save_user, load_daily_quiz, save_daily_quiz,
    update_user_stats
)
from buttons import get_quiz_control_buttons, get_result_buttons
from utils.time_utils import format_time, get_current_date, is_today, get_current_datetime, days_between
from result_handler import show_quiz_result

# ============================================
# ACTIVE QUIZZES STORAGE
# ============================================

active_quizzes = {}  # user_id -> QuizSession object

# ============================================
# QUIZ SESSION CLASS
# ============================================

class QuizSession:
    def __init__(self, user_id, topic, chapter_id, quiz_type, questions_list):
        self.user_id = user_id
        self.topic = topic
        self.chapter_id = chapter_id
        self.quiz_type = quiz_type
        self.questions = questions_list
        self.total_questions = len(questions_list)
        self.current_index = 0
        self.correct = 0
        self.wrong = 0
        self.skipped = 0
        self.answers = []
        self.start_time = time.time()
        self.status = "active"
        self.streak_count = 0
        
        # Get quiz settings
        self.time_limit = QUIZ_TYPES.get(quiz_type, {}).get("time_limit")
        self.is_exam_mode = (quiz_type == "exam")
    
    def get_current_question(self):
        """Get current question text"""
        if self.current_index < self.total_questions:
            q = self.questions[self.current_index]
            return q
        return None
    
    def check_answer(self, answer):
        """Check if answer is correct and update score"""
        current_q = self.get_current_question()
        if not current_q:
            return False
        
        is_correct = (answer.upper() == current_q['correct'].upper())
        
        # Calculate points
        points = 0
        if is_correct:
            points = SCORES['correct']
            self.correct += 1
            self.streak_count += 1
        else:
            if self.is_exam_mode:
                points = SCORES['negative_exam']
            else:
                points = SCORES['wrong']
            self.wrong += 1
            self.streak_count = 0
        
        # Streak bonus
        if self.streak_count >= 3:
            points += SCORES['streak_bonus']
        
        # Store answer
        self.answers.append({
            'question': current_q['question'],
            'options': current_q['options'],
            'user_answer': answer,
            'correct_answer': current_q['correct'],
            'is_correct': is_correct,
            'explanation': current_q.get('explanation', 'No explanation available.'),
            'points_earned': points
        })
        
        self.current_index += 1
        return is_correct
    
    def skip_question(self):
        """Skip current question"""
        current_q = self.get_current_question()
        if current_q:
            self.answers.append({
                'question': current_q['question'],
                'options': current_q['options'],
                'user_answer': 'SKIPPED',
                'correct_answer': current_q['correct'],
                'is_correct': False,
                'explanation': current_q.get('explanation', 'No explanation available.'),
                'points_earned': 0
            })
            self.skipped += 1
            self.current_index += 1
            self.streak_count = 0
            return True
        return False
    
    def is_complete(self):
        """Check if quiz is complete"""
        return self.current_index >= self.total_questions
    
    def get_time_remaining(self):
        """Get remaining time in seconds"""
        if self.time_limit:
            elapsed = time.time() - self.start_time
            remaining = self.time_limit - elapsed
            return max(0, int(remaining))
        return None
    
    def is_time_up(self):
        """Check if time is up"""
        if self.time_limit:
            elapsed = time.time() - self.start_time
            return elapsed >= self.time_limit
        return False
    
    def calculate_total_score(self):
        """Calculate total score including bonuses"""
        total = sum(a['points_earned'] for a in self.answers)
        
        # Completion bonus
        total += SCORES['completion_bonus']
        
        # Time bonus (if finished early)
        if self.time_limit:
            time_taken = time.time() - self.start_time
            if time_taken < self.time_limit * 0.7:
                total += SCORES['time_bonus'] * 2
            elif time_taken < self.time_limit * 0.9:
                total += SCORES['time_bonus']
        
        return total
    
    def get_result(self):
        """Get complete quiz result"""
        time_taken = int(time.time() - self.start_time)
        percentage = (self.correct / self.total_questions) * 100 if self.total_questions > 0 else 0
        
        # Get wrong answers for review
        wrong_answers = [a for a in self.answers if not a['is_correct'] and a['user_answer'] != 'SKIPPED']
        
        result = {
            'topic': self.topic,
            'chapter_id': self.chapter_id,
            'quiz_type': self.quiz_type,
            'total': self.total_questions,
            'correct': self.correct,
            'wrong': self.wrong,
            'skipped': self.skipped,
            'percentage': round(percentage, 2),
            'time_taken': time_taken,
            'total_score': self.calculate_total_score(),
            'answers': self.answers,
            'wrong_answers': wrong_answers,
            'date': get_current_date()
        }
        
        return result

# ============================================
# QUIZ START FUNCTIONS
# ============================================

def start_quiz(bot, call, topic, chapter_id, quiz_type):
    """Start a new quiz for the user"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Get questions for this chapter
    questions = get_questions_by_chapter(topic, chapter_id)
    
    if not questions:
        bot.answer_callback_query(call.id, "No questions available for this chapter yet!")
        return
    
    # Get quiz settings
    quiz_settings = QUIZ_TYPES.get(quiz_type, QUIZ_TYPES['quick'])
    num_questions = min(quiz_settings['questions'], len(questions))
    
    # Select random questions
    selected_questions = random.sample(questions, num_questions)
    
    # Create quiz session
    session = QuizSession(user_id, topic, chapter_id, quiz_type, selected_questions)
    active_quizzes[user_id] = session
    
    # Save session to file (for persistence)
    session_data = {
        'user_id': user_id,
        'topic': topic,
        'chapter_id': chapter_id,
        'quiz_type': quiz_type,
        'current_index': 0,
        'correct': 0,
        'wrong': 0,
        'skipped': 0,
        'start_time': session.start_time,
        'questions': selected_questions
    }
    save_session(user_id, session_data)
    
    # Send first question
    send_question(bot, chat_id, user_id, message_id)

def send_question(bot, chat_id, user_id, message_id=None):
    """Send current question to user"""
    session = active_quizzes.get(user_id)
    if not session:
        return
    
    current_q = session.get_current_question()
    if not current_q:
        return
    
    q_num = session.current_index + 1
    total = session.total_questions
    
    # Build question text
    question_text = f"📚 *Question {q_num}/{total}*\n"
    question_text += f"📖 Topic: {TOPICS[session.topic]['name']}\n"
    
    if session.time_limit:
        remaining = session.get_time_remaining()
        question_text += f"⏱️ Time left: {format_time(remaining)}\n"
    
    question_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    question_text += f"*{current_q['question']}*\n\n"
    question_text += f"A) {current_q['options'][0]}\n"
    question_text += f"B) {current_q['options'][1]}\n"
    question_text += f"C) {current_q['options'][2]}\n"
    question_text += f"D) {current_q['options'][3]}\n\n"
    question_text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    question_text += "👇 *Tap on an option to answer*"
    
    markup = get_quiz_control_buttons(q_num, total)
    
    if message_id:
        try:
            bot.edit_message_text(
                question_text,
                chat_id,
                message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except:
            bot.send_message(
                chat_id,
                question_text,
                reply_markup=markup,
                parse_mode='Markdown'
            )
    else:
        bot.send_message(
            chat_id,
            question_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

def handle_inline_answer(bot, call, answer):
    """Handle answer from inline button"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    session = active_quizzes.get(user_id)
    if not session:
        bot.answer_callback_query(call.id, "No active quiz! Start a new quiz from /menu")
        return
    
    # Handle quit
    if answer == "quit":
        delete_session(user_id)
        if user_id in active_quizzes:
            del active_quizzes[user_id]
        bot.edit_message_text(
            "❌ *Quiz Cancelled!*\n\nType /menu to start a new quiz.",
            chat_id,
            message_id,
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "Quiz cancelled")
        return
    
    # Handle skip
    if answer == "skip":
        session.skip_question()
        bot.answer_callback_query(call.id, "⏭️ Question skipped!")
        
        if session.is_complete():
            complete_quiz(bot, chat_id, user_id, message_id)
        else:
            send_question(bot, chat_id, user_id, message_id)
        return
    
    # Handle normal answer (A, B, C, D)
    is_correct = session.check_answer(answer)
    
    # Provide feedback
    current_q = session.get_current_question()
    if is_correct:
        feedback = "✅ *Correct!* 🎉"
        bot.answer_callback_query(call.id, "Correct! +10 points")
    else:
        correct_ans = current_q['correct'] if current_q else "?"
        feedback = f"❌ *Wrong!*\nCorrect answer: {correct_ans}"
        bot.answer_callback_query(call.id, f"Wrong! Correct answer: {correct_ans}")
    
    # Check if quiz is complete
    if session.is_complete():
        complete_quiz(bot, chat_id, user_id, message_id, feedback)
    else:
        # Send feedback and next question
        send_question(bot, chat_id, user_id, message_id)
        
        # Send feedback as separate message (doesn't interfere with quiz)
        bot.send_message(chat_id, feedback, parse_mode='Markdown')

def handle_answer(bot, message):
    """Handle /ans command from text"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    session = active_quizzes.get(user_id)
    if not session:
        bot.reply_to(message, "❌ No active quiz! Start a new quiz with /menu")
        return
    
    # Extract answer from command
    text = message.text.strip()
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ Please specify answer: /ans A, /ans B, /ans C, or /ans D")
        return
    
    answer = parts[1].upper()
    if answer not in ['A', 'B', 'C', 'D']:
        bot.reply_to(message, "❌ Invalid answer! Use A, B, C, or D")
        return
    
    # Process answer
    is_correct = session.check_answer(answer)
    
    if is_correct:
        feedback = "✅ Correct! 🎉"
    else:
        current_q = session.get_current_question()
        correct_ans = current_q['correct'] if current_q else "?"
        feedback = f"❌ Wrong! Correct answer: {correct_ans}"
    
    # Check if quiz is complete
    if session.is_complete():
        complete_quiz(bot, chat_id, user_id, None, feedback)
    else:
        bot.reply_to(message, feedback)
        send_question(bot, chat_id, user_id)

def handle_skip(bot, message):
    """Handle /skip command"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    session = active_quizzes.get(user_id)
    if not session:
        bot.reply_to(message, "❌ No active quiz!")
        return
    
    session.skip_question()
    bot.reply_to(message, "⏭️ Question skipped!")
    
    if session.is_complete():
        complete_quiz(bot, chat_id, user_id, None)
    else:
        send_question(bot, chat_id, user_id)

def complete_quiz(bot, chat_id, user_id, message_id=None, feedback=None):
    """Complete the quiz and show results"""
    session = active_quizzes.get(user_id)
    if not session:
        return
    
    # Get result
    result = session.get_result()
    
    # Save to database
    update_user_stats(user_id, result)
    
    # Delete session
    delete_session(user_id)
    if user_id in active_quizzes:
        del active_quizzes[user_id]
    
    # Send feedback if any
    if feedback:
        bot.send_message(chat_id, feedback, parse_mode='Markdown')
    
    # Show result
    show_quiz_result(bot, chat_id, user_id, result, message_id)

# ============================================
# DAILY QUIZ FUNCTIONS
# ============================================

def start_daily_quiz(bot, message):
    """Start daily quiz for user"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Load daily quiz data
    daily_data = load_daily_quiz()
    today = get_current_date()
    
    # Check if daily quiz exists for today
    if daily_data.get('date') != today:
        bot.reply_to(
            message,
            "📅 *Daily Quiz*\n\n"
            "No daily quiz set for today yet.\n"
            "Admin will set it soon!\n\n"
            "Check back later.",
            parse_mode='Markdown'
        )
        return
    
    # Check if user already completed today's quiz
    participants = daily_data.get('participants', {})
    if str(user_id) in participants:
        user_score = participants[str(user_id)]
        bot.reply_to(
            message,
            f"📅 *Daily Quiz*\n\n"
            f"❌ You have already completed today's quiz!\n"
            f"Your score: {user_score}\n\n"
            f"Come back tomorrow for a new quiz!",
            parse_mode='Markdown'
        )
        return
    
    # Start daily quiz
    questions = daily_data.get('questions', [])
    if not questions:
        bot.reply_to(message, "No questions available for daily quiz!")
        return
    
    # Create quiz session
    session = QuizSession(user_id, "daily", 0, "quick", questions)
    active_quizzes[user_id] = session
    
    # Save session
    session_data = {
        'user_id': user_id,
        'topic': 'daily',
        'chapter_id': 0,
        'quiz_type': 'quick',
        'current_index': 0,
        'correct': 0,
        'wrong': 0,
        'skipped': 0,
        'start_time': session.start_time,
        'questions': questions,
        'is_daily': True
    }
    save_session(user_id, session_data)
    
    # Send first question
    bot.reply_to(
        message,
        "📅 *Daily Quiz Started!*\n\n"
        "You have 5 questions.\n"
        "Good luck! 🍀",
        parse_mode='Markdown'
    )
    send_question(bot, chat_id, user_id)

def save_daily_quiz_result(user_id, score):
    """Save daily quiz result for user"""
    daily_data = load_daily_quiz()
    today = get_current_date()
    
    if daily_data.get('date') != today:
        daily_data['date'] = today
        daily_data['participants'] = {}
    
    if 'participants' not in daily_data:
        daily_data['participants'] = {}
    
    daily_data['participants'][str(user_id)] = score
    save_daily_quiz(daily_data)
    
    # Update user daily streak
    user_data = load_user(user_id)
    last_daily = user_data.get('last_daily_date', '')
    
    if last_daily == get_current_date():
        return  # Already updated
    
    if is_today(last_daily):
        # Already played today
        pass
    else:
        # Check if consecutive
        from utils.time_utils import days_between
        if last_daily and days_between(last_daily, get_current_date()) == 1:
            user_data['daily_quiz_streak'] = user_data.get('daily_quiz_streak', 0) + 1
        else:
            user_data['daily_quiz_streak'] = 1
        
        user_data['last_daily_date'] = get_current_date()
        save_user(user_id, user_data)

# ============================================
# RETEST FUNCTION (Wrong Answers Only)
# ============================================

def start_retest(bot, call, topic, chapter_id):
    """Start retest with only wrong answers from previous quiz"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # This would need to store wrong answers from last quiz
    # For now, show message
    bot.answer_callback_query(call.id, "Feature coming soon!")
    bot.edit_message_text(
        "🔄 *Retest Feature*\n\n"
        "This feature will show you questions you got wrong.\n"
        "Coming in next update!",
        chat_id,
        message_id,
        parse_mode='Markdown'
    )