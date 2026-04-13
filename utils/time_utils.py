from datetime import datetime, timedelta
import time

# ============================================
# TIME UTILITIES - Time Related Functions
# ============================================

# --------------------------------------------
# FORMATTING FUNCTIONS
# --------------------------------------------

def format_time(seconds):
    """Format seconds into readable time (MM:SS or HH:MM:SS)"""
    if seconds < 0:
        seconds = 0
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def format_time_verbose(seconds):
    """Format seconds into verbose format"""
    if seconds < 0:
        seconds = 0
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if secs > 0 or not parts:
        parts.append(f"{secs} second{'s' if secs != 1 else ''}")
    
    return " ".join(parts)

def format_date(date_string, input_format="%Y-%m-%d", output_format="%d %B %Y"):
    """Format date from one format to another"""
    try:
        date_obj = datetime.strptime(date_string, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_string

def format_datetime(dt_string):
    """Format datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%d %B %Y at %I:%M %p")
    except ValueError:
        return dt_string

# --------------------------------------------
# CURRENT DATE/TIME FUNCTIONS (FIXED)
# --------------------------------------------

def get_current_date():
    """Get current date as string (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_date_string():
    """Get current date as string (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time_string():
    """Get current time as string (HH:MM:SS)"""
    return datetime.now().strftime("%H:%M:%S")

def get_current_datetime():
    """Get current datetime as string (YYYY-MM-DD HH:MM:SS)"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_timestamp():
    """Get current Unix timestamp"""
    return int(time.time())

def get_current_iso_string():
    """Get current datetime as ISO format"""
    return datetime.now().isoformat()

# --------------------------------------------
# DATE COMPARISON FUNCTIONS (FIXED)
# --------------------------------------------

def is_today(date_string, input_format="%Y-%m-%d"):
    """Check if date is today"""
    try:
        date_obj = datetime.strptime(date_string, input_format)
        today = datetime.now()
        return date_obj.date() == today.date()
    except ValueError:
        return False

def is_yesterday(date_string, input_format="%Y-%m-%d"):
    """Check if date is yesterday"""
    try:
        date_obj = datetime.strptime(date_string, input_format)
        yesterday = datetime.now() - timedelta(days=1)
        return date_obj.date() == yesterday.date()
    except ValueError:
        return False

def is_same_day(date1, date2):
    """Check if two dates are the same day"""
    return date1 == date2

def days_between(date1, date2):
    """Calculate days between two dates"""
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        return abs((d2 - d1).days)
    except:
        return 0

def days_until(date_string, input_format="%Y-%m-%d"):
    """Calculate days until a given date"""
    try:
        target = datetime.strptime(date_string, input_format)
        today = datetime.now()
        delta = target - today
        return delta.days
    except ValueError:
        return None

def days_since(date_string, input_format="%Y-%m-%d"):
    """Calculate days since a given date"""
    try:
        past = datetime.strptime(date_string, input_format)
        today = datetime.now()
        delta = today - past
        return delta.days
    except ValueError:
        return None

def add_days(date_string, days, input_format="%Y-%m-%d"):
    """Add days to a date"""
    try:
        date_obj = datetime.strptime(date_string, input_format)
        new_date = date_obj + timedelta(days=days)
        return new_date.strftime(input_format)
    except ValueError:
        return date_string

# --------------------------------------------
# TIME CONVERSION FUNCTIONS
# --------------------------------------------

def seconds_to_minutes(seconds):
    """Convert seconds to minutes"""
    return seconds / 60

def minutes_to_seconds(minutes):
    """Convert minutes to seconds"""
    return minutes * 60

def hours_to_seconds(hours):
    """Convert hours to seconds"""
    return hours * 3600

def get_time_difference(start_time, end_time):
    """Get time difference in seconds"""
    return end_time - start_time

# --------------------------------------------
# QUIZ TIMING FUNCTIONS
# --------------------------------------------

def is_time_up(start_time, time_limit):
    """Check if quiz time limit is reached"""
    elapsed = time.time() - start_time
    return elapsed >= time_limit

def get_remaining_time(start_time, time_limit):
    """Get remaining time in seconds"""
    elapsed = time.time() - start_time
    remaining = time_limit - elapsed
    return max(0, int(remaining))

def get_time_percentage(start_time, time_limit):
    """Get percentage of time used"""
    elapsed = time.time() - start_time
    percentage = (elapsed / time_limit) * 100
    return min(100, max(0, int(percentage)))

def should_give_time_bonus(start_time, time_limit):
    """Check if user deserves time bonus (finished early)"""
    time_taken = time.time() - start_time
    if time_limit is None:
        return False
    return time_taken < (time_limit * 0.8)

def calculate_time_bonus(start_time, time_limit):
    """Calculate time bonus points"""
    if time_limit is None:
        return 0
    
    time_taken = time.time() - start_time
    if time_taken < (time_limit * 0.5):
        return 10
    elif time_taken < (time_limit * 0.7):
        return 5
    elif time_taken < (time_limit * 0.9):
        return 2
    return 0

# --------------------------------------------
# TIMER FUNCTIONS
# --------------------------------------------

def start_timer():
    """Start a timer and return start time"""
    return time.time()

def stop_timer(start_time):
    """Stop timer and return elapsed seconds"""
    return int(time.time() - start_time)

class Timer:
    """Simple timer class"""
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self):
        """Stop the timer"""
        if self.start_time:
            self.end_time = time.time()
            return self.get_elapsed()
        return 0
    
    def get_elapsed(self):
        """Get elapsed time in seconds"""
        if self.start_time:
            end = self.end_time if self.end_time else time.time()
            return int(end - self.start_time)
        return 0
    
    def reset(self):
        """Reset the timer"""
        self.start_time = None
        self.end_time = None
    
    def is_running(self):
        """Check if timer is running"""
        return self.start_time is not None and self.end_time is None

# --------------------------------------------
# STREAK CALCULATIONS
# --------------------------------------------

def calculate_streak(last_played_date):
    """Calculate current streak based on last played date"""
    if not last_played_date:
        return 0
    
    try:
        last_date = datetime.strptime(last_played_date, "%Y-%m-%d")
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        if last_date.date() == today:
            return 1
        elif last_date.date() == yesterday:
            return 2
        else:
            return 0
    except ValueError:
        return 0

def should_reset_streak(last_played_date):
    """Check if streak should be reset"""
    if not last_played_date:
        return True
    
    try:
        last_date = datetime.strptime(last_played_date, "%Y-%m-%d")
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        return last_date.date() < yesterday
    except ValueError:
        return True

# --------------------------------------------
# REMINDER TIME FUNCTIONS
# --------------------------------------------

def parse_time_string(time_string):
    """Parse time string like '09:00' to time object"""
    try:
        return datetime.strptime(time_string, "%H:%M").time()
    except ValueError:
        return None

def is_time_to_remind(reminder_time_str, last_reminded_date):
    """Check if it's time to send reminder"""
    try:
        reminder_time = datetime.strptime(reminder_time_str, "%H:%M").time()
        now = datetime.now()
        
        current_time = now.time()
        
        if last_reminded_date == now.strftime("%Y-%m-%d"):
            return False
        
        reminder_minutes = reminder_time.hour * 60 + reminder_time.minute
        current_minutes = current_time.hour * 60 + current_time.minute
        
        return abs(current_minutes - reminder_minutes) <= 5
        
    except (ValueError, AttributeError):
        return False

# --------------------------------------------
# SLEEP/WAIT FUNCTIONS
# --------------------------------------------

def sleep_seconds(seconds):
    """Sleep for given seconds"""
    time.sleep(seconds)

def sleep_minutes(minutes):
    """Sleep for given minutes"""
    time.sleep(minutes * 60)