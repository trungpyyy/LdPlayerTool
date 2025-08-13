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
IMAGE_CAPTURE_DELAY = 5.0  # seconds between screenshots
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
WINDOW_WIDTH = 350
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Rise of Kingdoms Tool"
WINDOW_BACKGROUND = "#f0f0f0"

# Log display settings
LOG_DISPLAY_HEIGHT = 8
LOG_DISPLAY_WIDTH = 40
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
LOCALHOST_PATTERNS = ["127.0.0.1", "localhost"]

# Device connection settings
DEVICE_CHECK_INTERVAL = 5.0  # seconds
DEVICE_RECONNECT_ATTEMPTS = 3

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
