import time
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID, ADMIN_IDS, BOT_NAME
from database import get_all_users, load_user, save_user, load_broadcast_log, save_broadcast_log
from decorators import admin_only
from utils.helpers import get_current_datetime

# ============================================
# BROADCAST SYSTEM - Send Messages to All Users
# ============================================

# Store broadcast states
broadcast_states = {}

def start_broadcast_from_admin(bot, call):
    """Start broadcast process from admin panel"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    broadcast_states[user_id] = {
        'step': 'waiting_for_message',
        'type': 'text'
    }
    
    text = """
📢 *BROADCAST SYSTEM*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are about to send a message to ALL users.

⚠️ *Important Notes:*
• This message will be sent to ALL registered users
• You cannot undo this action
• Please be careful with your message

━━━━━━━━━━━━━━━━━━━━━━━━━━━
*What would you like to send?*

1. 📝 Text Message
2. 🖼️ Text + Image
3. 📊 Quiz Link
4. 🔔 Announcement

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Send the number of your choice.
Type /cancel to cancel.
"""
    
    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        parse_mode='Markdown'
    )

def handle_broadcast_input(bot, message):
    """Handle broadcast message input from admin"""
    user_id = message.from_user.id
    
    if user_id not in broadcast_states:
        return False
    
    state = broadcast_states[user_id]
    step = state.get('step')
    
    if step == 'waiting_for_message':
        # First, ask for broadcast type
        choice = message.text.strip()
        
        if choice == '1':
            state['type'] = 'text'
            state['step'] = 'waiting_for_text'
            broadcast_states[user_id] = state
            
            bot.reply_to(
                message,
                "📝 *Send your broadcast message*\n\n"
                "Type the message you want to send to all users.\n"
                "You can use Markdown formatting.\n\n"
                "Type /confirm when done, or /cancel to cancel.",
                parse_mode='Markdown'
            )
            return True
        
        elif choice == '2':
            state['type'] = 'image'
            state['step'] = 'waiting_for_image'
            broadcast_states[user_id] = state
            
            bot.reply_to(
                message,
                "🖼️ *Send your image*\n\n"
                "Send the image you want to broadcast.\n"
                "After sending the image, you can add a caption.\n\n"
                "Type /cancel to cancel.",
                parse_mode='Markdown'
            )
            return True
        
        elif choice == '3':
            state['type'] = 'quiz'
            state['step'] = 'waiting_for_quiz'
            broadcast_states[user_id] = state
            
            bot.reply_to(
                message,
                "📚 *Send quiz link or topic*\n\n"
                "Send the quiz topic or command you want to share.\n"
                "Example: /daily or /topics\n\n"
                "Type /cancel to cancel.",
                parse_mode='Markdown'
            )
            return True
        
        elif choice == '4':
            state['type'] = 'announcement'
            state['step'] = 'waiting_for_announcement'
            broadcast_states[user_id] = state
            
            bot.reply_to(
                message,
                "🔔 *Send your announcement*\n\n"
                "Type the announcement you want to share.\n"
                "It will be formatted as an official announcement.\n\n"
                "Type /confirm when done, or /cancel to cancel.",
                parse_mode='Markdown'
            )
            return True
        
        else:
            bot.reply_to(
                message,
                "❌ Invalid choice! Send 1, 2, 3, or 4.\n\n"
                "Type /cancel to cancel."
            )
            return True
    
    elif step == 'waiting_for_text':
        # Save the broadcast message
        state['message'] = message.text
        state['step'] = 'confirm'
        broadcast_states[user_id] = state
        
        # Show preview
        preview_text = f"""
📝 *Broadcast Preview*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

{message.text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *Recipients:* All users ({len(get_all_users())} users)

Type /confirm to send this broadcast.
Type /cancel to cancel.
"""
        bot.reply_to(message, preview_text, parse_mode='Markdown')
        return True
    
    elif step == 'waiting_for_announcement':
        # Format as announcement
        announcement = f"""
🔔 *OFFICIAL ANNOUNCEMENT*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

{message.text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {get_current_datetime()}
🤖 {BOT_NAME}
"""
        state['message'] = announcement
        state['step'] = 'confirm'
        broadcast_states[user_id] = state
        
        # Show preview
        preview_text = f"""
🔔 *Announcement Preview*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

{announcement[:500]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *Recipients:* All users ({len(get_all_users())} users)

Type /confirm to send this announcement.
Type /cancel to cancel.
"""
        bot.reply_to(message, preview_text, parse_mode='Markdown')
        return True
    
    elif step == 'waiting_for_quiz':
        state['quiz_link'] = message.text
        state['step'] = 'confirm'
        broadcast_states[user_id] = state
        
        quiz_message = f"""
📚 *Quiz Alert!* 📚

Test your knowledge with this quiz!

👉 *{message.text}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Challenge yourself and improve your rank! 🏆
"""
        state['message'] = quiz_message
        
        preview_text = f"""
📚 *Quiz Broadcast Preview*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

{quiz_message[:500]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *Recipients:* All users ({len(get_all_users())} users)

Type /confirm to send this broadcast.
Type /cancel to cancel.
"""
        bot.reply_to(message, preview_text, parse_mode='Markdown')
        return True
    
    elif step == 'confirm':
        # This is handled by the confirm command
        pass
    
    return False

def handle_broadcast_image(bot, message):
    """Handle image broadcast"""
    user_id = message.from_user.id
    
    if user_id not in broadcast_states:
        return False
    
    state = broadcast_states[user_id]
    
    if state.get('step') != 'waiting_for_image':
        return False
    
    # Get photo file_id
    if message.photo:
        photo_id = message.photo[-1].file_id
        state['photo_id'] = photo_id
        state['step'] = 'waiting_for_caption'
        broadcast_states[user_id] = state
        
        bot.reply_to(
            message,
            "✅ Image received!\n\n"
            "Now send the caption for this image (or type 'skip' for no caption).\n\n"
            "Type /confirm when done, or /cancel to cancel."
        )
        return True
    else:
        bot.reply_to(
            message,
            "❌ Please send a valid image.\n\n"
            "Type /cancel to cancel."
        )
        return True

def handle_broadcast_caption(bot, message):
    """Handle image caption"""
    user_id = message.from_user.id
    
    if user_id not in broadcast_states:
        return False
    
    state = broadcast_states[user_id]
    
    if state.get('step') != 'waiting_for_caption':
        return False
    
    caption = message.text.strip()
    if caption.lower() == 'skip':
        caption = None
    
    state['caption'] = caption
    state['step'] = 'confirm'
    broadcast_states[user_id] = state
    
    preview_text = f"""
🖼️ *Image Broadcast Preview*

📷 *Image:* [Image attached]
📝 *Caption:* {caption if caption else 'No caption'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *Recipients:* All users ({len(get_all_users())} users)

Type /confirm to send this broadcast.
Type /cancel to cancel.
"""
    
    # Send preview with the image
    if caption:
        bot.send_photo(message.chat.id, state['photo_id'], caption=preview_text, parse_mode='Markdown')
    else:
        bot.send_photo(message.chat.id, state['photo_id'], caption=preview_text, parse_mode='Markdown')
    
    return True

def confirm_broadcast(bot, message):
    """Confirm and send broadcast"""
    user_id = message.from_user.id
    
    if user_id not in broadcast_states:
        bot.reply_to(message, "❌ No broadcast in progress. Use /admin to start a new broadcast.")
        return False
    
    state = broadcast_states[user_id]
    
    if state.get('step') != 'confirm':
        bot.reply_to(message, "❌ Please complete the broadcast setup first.")
        return False
    
    # Send initial confirmation
    bot.reply_to(message, "📢 *Starting broadcast...*\n\nThis may take a few moments.", parse_mode='Markdown')
    
    # Get all users
    all_users = get_all_users()
    total_users = len(all_users)
    success_count = 0
    fail_count = 0
    
    broadcast_type = state.get('type', 'text')
    broadcast_message = state.get('message', '')
    photo_id = state.get('photo_id')
    caption = state.get('caption')
    
    # Send to each user
    for user_id_str in all_users:
        try:
            if broadcast_type == 'text':
                bot.send_message(int(user_id_str), broadcast_message, parse_mode='Markdown')
            elif broadcast_type == 'image' and photo_id:
                bot.send_photo(int(user_id_str), photo_id, caption=caption, parse_mode='Markdown')
            elif broadcast_type == 'quiz':
                bot.send_message(int(user_id_str), broadcast_message, parse_mode='Markdown')
            elif broadcast_type == 'announcement':
                bot.send_message(int(user_id_str), broadcast_message, parse_mode='Markdown')
            
            success_count += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.05)
            
        except Exception as e:
            fail_count += 1
            print(f"Failed to send to {user_id_str}: {e}")
    
    # Log broadcast
    log_broadcast(broadcast_message[:100], total_users, success_count)
    
    # Send completion report
    report = f"""
✅ *Broadcast Complete!*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Report:*
• Total users: {total_users}
• ✅ Successfully sent: {success_count}
• ❌ Failed: {fail_count}
• 📝 Broadcast type: {broadcast_type}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 {get_current_datetime()}
"""
    
    bot.send_message(message.chat.id, report, parse_mode='Markdown')
    
    # Clear broadcast state
    del broadcast_states[user_id]
    return True

def cancel_broadcast(bot, message):
    """Cancel broadcast"""
    user_id = message.from_user.id
    
    if user_id in broadcast_states:
        del broadcast_states[user_id]
        bot.reply_to(message, "❌ Broadcast cancelled.")
    else:
        bot.reply_to(message, "No active broadcast to cancel.")

def log_broadcast(message, total_sent, success_count):
    """Log broadcast to file"""
    log_data = load_broadcast_log()
    
    log_entry = {
        'id': len(log_data.get('broadcasts', [])) + 1,
        'date': get_current_datetime(),
        'message': message[:200],
        'total_sent': total_sent,
        'success_count': success_count,
        'failure_count': total_sent - success_count
    }
    
    if 'broadcasts' not in log_data:
        log_data['broadcasts'] = []
    
    log_data['broadcasts'].append(log_entry)
    
    # Keep only last 100 broadcasts
    if len(log_data['broadcasts']) > 100:
        log_data['broadcasts'] = log_data['broadcasts'][-100:]
    
    save_broadcast_log(log_data)

def get_broadcast_history(bot, message):
    """Show broadcast history (admin only)"""
    user_id = message.from_user.id
    
    if user_id not in ADMIN_IDS and user_id != OWNER_ID:
        bot.reply_to(message, "❌ Admin only command!")
        return
    
    log_data = load_broadcast_log()
    broadcasts = log_data.get('broadcasts', [])
    
    if not broadcasts:
        bot.reply_to(message, "📢 *Broadcast History*\n\nNo broadcasts sent yet.", parse_mode='Markdown')
        return
    
    text = "📢 *BROADCAST HISTORY*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for b in broadcasts[-10:][::-1]:
        text += f"🆔 #{b['id']}\n"
        text += f"📅 {b['date']}\n"
        text += f"📊 Sent: {b['success_count']}/{b['total_sent']}\n"
        text += f"📝 Message: {b['message']}...\n\n"
    
    bot.reply_to(message, text, parse_mode='Markdown')