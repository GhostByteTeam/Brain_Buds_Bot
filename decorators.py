import functools
import time
from config import OWNER_ID, ADMIN_IDS

# ============================================
# DECORATORS - Access Control & Utilities
# ============================================

# --------------------------------------------
# ADMIN ONLY DECORATOR
# Sirf owner hi admin commands use kar sakta hai
# --------------------------------------------

def admin_only(func):
    """Decorator to restrict command to admin/owner only"""
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        
        # Check if user is owner or in admin list
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            return func(message, *args, **kwargs)
        else:
            # Not authorized
            from telebot import TeleBot
            bot = args[0] if args else None
            if bot:
                bot.reply_to(message, "❌ Access Denied!\n\nYou are not authorized to use admin commands.\nThis bot can only be used by the owner.")
            return None
    return wrapper

# --------------------------------------------
# OWNER ONLY DECORATOR (Strict)
# Sirf ek specific owner hi use kar sakta hai
# --------------------------------------------

def owner_only(func):
    """Decorator to restrict command to single owner only"""
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        
        if user_id == OWNER_ID:
            return func(message, *args, **kwargs)
        else:
            from telebot import TeleBot
            bot = args[0] if args else None
            if bot:
                bot.reply_to(message, "❌ This command is for bot owner only!")
            return None
    return wrapper

# --------------------------------------------
# RATE LIMIT DECORATOR
# Spam se bachne ke liye
# --------------------------------------------

rate_limit_data = {}

def rate_limit(limit_per_minute=10):
    """Decorator to limit how many times a user can use a command per minute"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(message, *args, **kwargs):
            user_id = message.from_user.id
            current_time = time.time()
            
            # Initialize user data if not exists
            if user_id not in rate_limit_data:
                rate_limit_data[user_id] = []
            
            # Clean old entries (older than 60 seconds)
            rate_limit_data[user_id] = [t for t in rate_limit_data[user_id] if current_time - t < 60]
            
            # Check if limit exceeded
            if len(rate_limit_data[user_id]) >= limit_per_minute:
                from telebot import TeleBot
                bot = args[0] if args else None
                if bot:
                    bot.reply_to(message, f"⚠️ Slow down! You can use this command {limit_per_minute} times per minute.\nPlease wait a moment.")
                return None
            
            # Add current time to list
            rate_limit_data[user_id].append(current_time)
            
            return func(message, *args, **kwargs)
        return wrapper
    return decorator

# --------------------------------------------
# BOT ACTIVE DECORATOR
# Bot band ho to commands na chalein
# --------------------------------------------

def bot_active_only(func):
    """Decorator to check if bot is active before processing command"""
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        try:
            from database import load_settings
            
            settings = load_settings()
            
            if not settings.get("bot_active", True):
                from telebot import TeleBot
                bot = args[0] if args else None
                if bot:
                    bot.reply_to(message, "⚠️ Bot is currently under maintenance.\nPlease try again later.")
                return None
            
            if settings.get("maintenance_mode", False):
                # Check if user is admin (can use during maintenance)
                user_id = message.from_user.id
                if user_id == OWNER_ID or user_id in ADMIN_IDS:
                    return func(message, *args, **kwargs)
                else:
                    from telebot import TeleBot
                    bot = args[0] if args else None
                    if bot:
                        bot.reply_to(message, "⚠️ Bot is under maintenance.\nOnly admins can access right now.\nPlease try again later.")
                    return None
            
            return func(message, *args, **kwargs)
        except:
            return func(message, *args, **kwargs)
    return wrapper

# --------------------------------------------
# LOGGING DECORATOR
# Har command ka log rakhne ke liye
# --------------------------------------------

def log_command(func):
    """Decorator to log user commands"""
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        command = message.text if message.text else "unknown"
        
        print(f"[LOG] User: {user_name} ({user_id}) | Command: {command}")
        
        # Call the actual function
        return func(message, *args, **kwargs)
    return wrapper

# --------------------------------------------
# ERROR HANDLER DECORATOR
# Errors ko handle karne ke liye
# --------------------------------------------

def handle_errors(func):
    """Decorator to catch and handle errors gracefully"""
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        try:
            return func(message, *args, **kwargs)
        except Exception as e:
            from telebot import TeleBot
            bot = args[0] if args else None
            
            error_message = f"❌ Something went wrong!\n\nError: {str(e)[:100]}\n\nPlease try again or contact support."
            
            if bot:
                bot.reply_to(message, error_message)
            
            # Print error for debugging
            print(f"[ERROR] {func.__name__}: {str(e)}")
            return None
    return wrapper

# --------------------------------------------
# QUIZ ACTIVE CHECK DECORATOR
# Check if user has active quiz before allowing certain commands
# --------------------------------------------

def quiz_active_only(func):
    """Decorator to check if user has an active quiz session"""
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        
        try:
            from database import load_session
            
            session = load_session(user_id)
            
            if not session:
                from telebot import TeleBot
                bot = args[0] if args else None
                if bot:
                    bot.reply_to(message, "❌ You don't have an active quiz!\n\nStart a quiz using /menu or /topics")
                return None
            
            return func(message, *args, **kwargs)
        except:
            from telebot import TeleBot
            bot = args[0] if args else None
            if bot:
                bot.reply_to(message, "❌ No active quiz found.\nStart a new quiz with /menu")
            return None
    return wrapper

# --------------------------------------------
# PREMIUM USER CHECK (Future use)
# Agar future mein premium feature add karna ho to
# --------------------------------------------

def premium_only(func):
    """Decorator to restrict command to premium users only (future feature)"""
    @functools.wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.from_user.id
        
        # For now, all users are premium
        # Future: Check database for premium status
        return func(message, *args, **kwargs)
    return wrapper