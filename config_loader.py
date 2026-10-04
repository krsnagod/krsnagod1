"""Config loader — reads/writes config.py in the current directory."""
import importlib.util
import datetime
from pathlib import Path

CONFIG_FILENAME = "config.py"
CONFIG_PATH = Path.cwd() / CONFIG_FILENAME


def config_exists():
    return CONFIG_PATH.exists()


def load_config():
    """Load config.py dynamically."""
    if not CONFIG_PATH.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "KRSNAgod_config", str(CONFIG_PATH)
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {
            "TOKENS": getattr(mod, "TOKENS", []),
            "OWNER_ID": getattr(mod, "OWNER_ID", None),
            "REBRAND": getattr(mod, "REBRAND", "KRSNA BHAGWAN"),
        }
    except Exception as e:
        print(f"⚠️  Failed to load config.py: {e}")
        return None


def save_config(tokens, owner_id, rebrand):
    """Write config.py with the user's values."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f'''# ============================================================
# KRSNA BHAGWAN — Auto-Generated Config
# Generated on: {now}
# Powered by @wjv_1
# ============================================================

TOKENS = {tokens!r}

OWNER_ID = {owner_id!r}

REBRAND = {rebrand!r}
'''
    CONFIG_PATH.write_text(content, encoding="utf-8")
    return CONFIG_PATH
