"""
Configuration file for Rise of Kingdoms Tool
All settings can be modified here without changing the main code
"""

import os

# ==================== ADB SETTINGS ====================
ADB_PATH = "adb/adb.exe"
ADB_TIMEOUT = 15  # seconds
ADB_RETRY_ATTEMPTS = 3

# ==================== IMAGE RECOGNITION SETTINGS ====================
TEMPLATE_MATCHING_THRESHOLD = 0.9  # 0.0 to 1.0 (higher = more strict)
IMAGE_CAPTURE_DELAY = 2 # seconds between screenshots
TEMPLATE_SEARCH_TIMEOUT = 10  # seconds to wait for objects

# ==================== TASK SETTINGS ====================
# Delays between task operations (in seconds)
FARM_DELAY = 2.0
EXPLORE_DELAY = 3.0
TRAIN_DELAY = 1.5
RECRUITMENT_DELAY = 2.0

# Task iteration limits
MAX_TASK_ITERATIONS = 1000
TASK_RETRY_DELAY = 2.0

# ==================== UI SETTINGS ====================
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 700
WINDOW_TITLE = "🎮 Rise of Kingdoms Tool"
WINDOW_BACKGROUND = "#f0f2f5"

# ==================== COLOR SCHEME ====================
# Modern gradient theme with better contrast
COLORS = {
    "primary": "#ffffff",           # White
    "secondary": "#f8f9fa",        # Light gray
    "accent": "#6366f1",           # Modern indigo
    "accent_light": "#818cf8",     # Lighter indigo
    "accent_dark": "#4f46e5",      # Darker indigo
    "success": "#10b981",          # Modern green
    "success_light": "#34d399",    # Light green
    "warning": "#f59e0b",          # Modern amber
    "warning_light": "#fbbf24",    # Light amber
    "error": "#ef4444",            # Modern red
    "error_light": "#f87171",      # Light red
    "text_primary": "#1f2937",     # Dark gray text
    "text_secondary": "#6b7280",   # Medium gray text
    "text_muted": "#9ca3af",       # Muted text
    "border": "#e5e7eb",           # Light border
    "border_light": "#f3f4f6",     # Lighter border
    "button_bg": "#6366f1",        # Indigo button
    "button_hover": "#4f46e5",     # Darker indigo hover
    "button_secondary": "#f3f4f6", # Secondary button
    "button_secondary_hover": "#e5e7eb", # Secondary button hover
    "checkbox_bg": "#ffffff",      # White checkbox
    "input_bg": "#ffffff",         # White input
    "frame_bg": "#ffffff",         # White frame
    "card_bg": "#ffffff",          # Card background
    "card_shadow": "#00000010",    # Card shadow
    "gradient_start": "#667eea",   # Gradient start
    "gradient_end": "#764ba2",     # Gradient end
}

# ==================== FONT SETTINGS ====================
FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "heading": ("Segoe UI", 11, "bold"),
    "subheading": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 9),
    "button": ("Segoe UI", 9, "bold"),
    "small": ("Segoe UI", 8),
    "caption": ("Segoe UI", 7),
}

# UI spacing and sizing - more compact
SPACING = {
    "xs": 2,
    "sm": 4,
    "md": 8,
    "lg": 12,
    "xl": 16,
}

# Button styles for different types
BUTTON_STYLES = {
    "primary": {
        "bg": COLORS["accent"],
        "fg": COLORS["primary"],
        "activebackground": COLORS["accent_dark"],
        "activeforeground": COLORS["primary"],
        "relief": "flat",
        "bd": 0,
        "padx": SPACING["md"],
        "pady": SPACING["xs"],
        "cursor": "hand2"
    },
    "secondary": {
        "bg": COLORS["button_secondary"],
        "fg": COLORS["text_primary"],
        "activebackground": COLORS["button_secondary_hover"],
        "activeforeground": COLORS["text_primary"],
        "relief": "flat",
        "bd": 0,
        "padx": SPACING["md"],
        "pady": SPACING["xs"],
        "cursor": "hand2"
    },
    "danger": {
        "bg": COLORS["error"],
        "fg": COLORS["primary"],
        "activebackground": COLORS["error_light"],
        "activeforeground": COLORS["primary"],
        "relief": "flat",
        "bd": 0,
        "padx": SPACING["sm"],
        "pady": SPACING["xs"],
        "cursor": "hand2"
    },
    "success": {
        "bg": COLORS["success"],
        "fg": COLORS["primary"],
        "activebackground": COLORS["success_light"],
        "activeforeground": COLORS["primary"],
        "relief": "flat",
        "bd": 0,
        "padx": SPACING["sm"],
        "pady": SPACING["xs"],
        "cursor": "hand2"
    }
}

# Input field styles
INPUT_STYLES = {
    "default": {
        "relief": "flat",
        "bd": 1,
        "highlightthickness": 1,
        "highlightbackground": COLORS["border"],
        "highlightcolor": COLORS["accent"],
        "bg": COLORS["input_bg"],
        "fg": COLORS["text_primary"],
        "insertbackground": COLORS["text_primary"]
    }
}

# Checkbox styles
CHECKBOX_STYLES = {
    "default": {
        "relief": "flat",
        "bd": 0,
        "bg": COLORS["card_bg"],
        "selectcolor": COLORS["accent"],
        "activebackground": COLORS["card_bg"],
        "activeforeground": COLORS["text_primary"],
        "cursor": "hand2"
    }
}

CARD_STYLE = {
    "relief": "flat",
    "bd": 0,
    "bg": COLORS["card_bg"],
    "highlightthickness": 1,
    "highlightbackground": COLORS["border"],
    "highlightcolor": COLORS["accent"],
}

# Log display settings
LOG_DISPLAY_HEIGHT = 6
LOG_DISPLAY_WIDTH = 35
MAX_LOG_ENTRIES = 1000

# ==================== LOGGING SETTINGS ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DIRECTORY = "logs"
LOG_FILENAME_PREFIX = "ld_tool"

# ==================== ERROR HANDLING SETTINGS ====================
MAX_ERROR_RETRIES = 3
ERROR_RETRY_DELAY = 2.0
SHOW_ERROR_DIALOGS = True
CONTINUE_ON_ERROR = True

# ==================== DEVICE SETTINGS ====================
# Filter out certain device types
FILTER_LOCALHOST_DEVICES = True
LOCALHOST_PATTERNS = []

# Device connection settings
DEVICE_CHECK_INTERVAL = 5.0  # seconds
DEVICE_RECONNECT_ATTEMPTS = 3

# ==================== STATE MANAGEMENT SETTINGS ====================
# Default application state settings
DEFAULT_PAUSE_STATE = True  # Devices start in paused state by default
STATE_AUTO_SAVE = True  # Automatically save state changes
STATE_FILE_PATH = "data/app_state.json"  # Path to state file

# ==================== GAME-SPECIFIC SETTINGS ====================
# Rise of Kingdoms specific coordinates and settings
GAME_DISCONNECT_BUTTON = (638, 471)
GAME_ALWAYS_CHECK_DIRECTORY = "./images/always_check"
GAME_EXPLORE_CHECK_DIRECTORY = "./images/explore_check"
GAME_ALL_ARMIES_IMAGE = "./images/AllArmies.png"
GAME_DISCONNECTED_IMAGE = "./images/disconnected.png"

# ==================== ADVANCED SETTINGS ====================
# Performance settings
ENABLE_PERFORMANCE_MONITORING = True
PERFORMANCE_LOG_INTERVAL = 60  # seconds

# Debug settings
SAVE_SCREENSHOTS = False
SCREENSHOT_DIRECTORY = "screenshots"
ENABLE_VERBOSE_LOGGING = True

# ==================== VALIDATION FUNCTIONS ====================
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check ADB path
    if not os.path.exists(ADB_PATH):
        errors.append(f"ADB path not found: {ADB_PATH}")
    
    # Check threshold values
    if not 0.0 <= TEMPLATE_MATCHING_THRESHOLD <= 1.0:
        errors.append(f"Template matching threshold must be between 0.0 and 1.0, got: {TEMPLATE_MATCHING_THRESHOLD}")
    
    # Check delay values
    if any(delay < 0 for delay in [FARM_DELAY, EXPLORE_DELAY, TRAIN_DELAY, RECRUITMENT_DELAY]):
        errors.append("All delay values must be non-negative")
    
    # Check timeout values
    if any(timeout <= 0 for timeout in [ADB_TIMEOUT, TEMPLATE_SEARCH_TIMEOUT]):
        errors.append("All timeout values must be positive")
    
    return errors

def get_config_summary():
    """Get a summary of current configuration"""
    return {
        "ADB Settings": {
            "Path": ADB_PATH,
            "Timeout": f"{ADB_TIMEOUT}s",
            "Retry Attempts": ADB_RETRY_ATTEMPTS
        },
        "Image Recognition": {
            "Threshold": TEMPLATE_MATCHING_THRESHOLD,
            "Capture Delay": f"{IMAGE_CAPTURE_DELAY}s",
            "Search Timeout": f"{TEMPLATE_SEARCH_TIMEOUT}s"
        },
        "Task Delays": {
            "Farm": f"{FARM_DELAY}s",
            "Explore": f"{EXPLORE_DELAY}s",
            "Train": f"{TRAIN_DELAY}s",
            "Recruitment": f"{RECRUITMENT_DELAY}s"
        },
        "UI": {
            "Window Size": f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}",
            "Log Display": f"{LOG_DISPLAY_HEIGHT}x{LOG_DISPLAY_WIDTH}",
            "Max Log Entries": MAX_LOG_ENTRIES
        },
        "Logging": {
            "Level": LOG_LEVEL,
            "Directory": LOG_DIRECTORY,
            "Save Screenshots": SAVE_SCREENSHOTS
        }
    }

# ==================== ENVIRONMENT OVERRIDES ====================
# Allow environment variables to override config
def load_from_environment():
    """Load configuration from environment variables if they exist"""
    import os
    
    global ADB_PATH, TEMPLATE_MATCHING_THRESHOLD, LOG_LEVEL
    
    # Override with environment variables if they exist
    if os.getenv("LD_TOOL_ADB_PATH"):
        ADB_PATH = os.getenv("LD_TOOL_ADB_PATH")
    
    if os.getenv("LD_TOOL_THRESHOLD"):
        try:
            TEMPLATE_MATCHING_THRESHOLD = float(os.getenv("LD_TOOL_THRESHOLD"))
        except ValueError:
            pass
    
    if os.getenv("LD_TOOL_LOG_LEVEL"):
        LOG_LEVEL = os.getenv("LD_TOOL_LOG_LEVEL")

# Load environment overrides when module is imported
load_from_environment()

# Validate configuration on import
if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")
        print("\nConfiguration Summary:")
        summary = get_config_summary()
        for category, settings in summary.items():
            print(f"\n{category}:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
