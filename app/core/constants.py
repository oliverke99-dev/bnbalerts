"""
Application Constants

Centralized location for magic numbers and configuration constants
used throughout the application.
"""

# Watch Limits
MAX_ACTIVE_WATCHES_PER_USER = 5

# Notification Settings
NOTIFICATION_COOLDOWN_HOURS = 24

# Scheduler Settings
SCHEDULER_CHECK_INTERVAL_SECONDS = 60

# Scan Frequency Settings
DAILY_SCAN_HOUR = 12  # Noon (UTC)
HOURLY_SCAN_INTERVAL_HOURS = 1
SNIPER_SCAN_INTERVAL_MINUTES = 5

# Polling Settings
MAX_POLL_ATTEMPTS = 30
POLL_INTERVAL_SECONDS = 2

# OTP Settings
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10

# Mock Data Settings
MOCK_API_DELAY_SECONDS = 1.5
MOCK_MIN_PROPERTIES = 8
MOCK_MAX_PROPERTIES = 15