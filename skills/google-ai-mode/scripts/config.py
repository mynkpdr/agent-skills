"""
Configuration for Google AI Mode Skill
Minimal config - no auth, no persistence needed
"""

from pathlib import Path
import os
import sys

# Paths
SKILL_DIR = Path(__file__).parent.parent

# User-data cache root - deliberately outside the skill folder itself, so
# search results and debug logs (real data, not build artifacts) survive a
# skill reinstall/update and are never at risk of being committed to git.
# Platform-specific cache directories:
# - Windows: %LOCALAPPDATA%\google-ai-mode-skill
# - macOS: ~/Library/Caches/google-ai-mode-skill
# - Linux: ~/.cache/google-ai-mode-skill
if sys.platform == "win32":
    # Windows: Use AppData\Local
    CACHE_ROOT = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "google-ai-mode-skill"
elif sys.platform == "darwin":
    # macOS: Use ~/Library/Caches
    CACHE_ROOT = Path.home() / "Library" / "Caches" / "google-ai-mode-skill"
else:
    # Linux/Unix: Use ~/.cache
    CACHE_ROOT = Path.home() / ".cache" / "google-ai-mode-skill"

BROWSER_PROFILE_DIR = CACHE_ROOT / "chrome_profile"
RESULTS_DIR = CACHE_ROOT / "results"
LOGS_DIR = CACHE_ROOT / "logs"

BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Browser Configuration
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--no-first-run',
    '--no-default-browser-check',
    '--lang=en',  # CRITICAL: Must be 'en' not 'en-US' for UI language!
    '--disable-translate',  # Disable auto-translate popup
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Locale settings for consistent language
LOCALE = "en-US"
EXTRA_HTTP_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9"
}

# Timeouts
PAGE_LOAD_TIMEOUT = 45000  # 45 seconds
