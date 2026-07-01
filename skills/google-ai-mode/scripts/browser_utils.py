"""
Browser Utilities for Google AI Mode Skill
Uses persistent context to avoid CAPTCHAs
"""

import json
import time
from pathlib import Path

from patchright.sync_api import Playwright, BrowserContext
from config import BROWSER_ARGS, USER_AGENT, BROWSER_PROFILE_DIR, LOCALE, EXTRA_HTTP_HEADERS


def _load_json_preserving_corruption(path: Path, label: str) -> dict:
    """
    Load a JSON profile file, without silently discarding it on a parse
    error. A bare except-and-reset here would mean a single malformed
    write corrupts the real Chrome profile (all of Preferences/Local
    State get overwritten with just our forced settings, losing whatever
    else was in there). Instead, corrupt files are backed up so nothing
    is lost, and the situation is reported instead of hidden.
    """
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        backup_path = path.with_name(f"{path.name}.corrupt-{int(time.time())}")
        try:
            path.rename(backup_path)
            print(f"⚠️  {label} was corrupt and unreadable ({e}). "
                  f"Backed up to {backup_path.name} instead of discarding it.")
        except OSError as rename_error:
            print(f"⚠️  {label} was corrupt and unreadable ({e}); "
                  f"could not back it up either ({rename_error}).")
        return {}


class BrowserFactory:
    """Factory for creating configured browser instances"""

    @staticmethod
    def launch_persistent_context(playwright: Playwright, headless: bool = True) -> BrowserContext:
        """
        Launch browser with PERSISTENT CONTEXT - keeps cookies/session!
        This dramatically reduces CAPTCHA occurrences.

        Sets English as preferred language (but multi-language selectors handle any locale).
        """
        # Step 1: Set Local State (profile-wide settings)
        local_state_file = BROWSER_PROFILE_DIR / "Local State"
        local_state = _load_json_preserving_corruption(local_state_file, "Local State")

        # Force English in Local State
        local_state.update({
            "intl": {
                "app_locale": "en",  # CRITICAL: Chrome UI language
                "accept_languages": "en-US,en"
            }
        })

        with open(local_state_file, 'w', encoding='utf-8') as f:
            json.dump(local_state, f, indent=2)

        # Step 2: Set Default/Preferences (per-profile settings)
        prefs_dir = BROWSER_PROFILE_DIR / "Default"
        prefs_dir.mkdir(parents=True, exist_ok=True)
        prefs_file = prefs_dir / "Preferences"

        # Load existing preferences to preserve cookies/session
        prefs = _load_json_preserving_corruption(prefs_file, "Preferences")

        # FORCE English language settings
        prefs.update({
            "intl": {
                "accept_languages": "en-US,en",
                "selected_languages": "en-US,en",
                "app_locale": "en"  # Redundant but ensures consistency
            },
            "translate": {
                "enabled": False  # Disable auto-translate
            },
            "webkit": {
                "webprefs": {
                    "default_charset": "utf-8"
                }
            }
        })

        # Write preferences atomically
        with open(prefs_file, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=2)

        # NOW launch browser (will read our forced preferences)
        return playwright.chromium.launch_persistent_context(
            str(BROWSER_PROFILE_DIR),  # Persistent profile directory
            channel="chrome",  # Use real Chrome for better anti-detection
            headless=headless,
            user_agent=USER_AGENT,
            locale=LOCALE,  # Force English locale
            extra_http_headers=EXTRA_HTTP_HEADERS,  # Force English language headers
            args=BROWSER_ARGS,
            ignore_default_args=["--enable-automation"],
        )
