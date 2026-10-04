"""KRSNA BHAGWAN - CLI entry point with setup wizard."""
import sys

from .config_loader import load_config, save_config, config_exists, CONFIG_PATH


BANNER = r"""
┌────────────────────────────────────────────────────┐
│ _  ______  ____  _   _    _       ____  ___  ____  │
│| |/ /  _ \/ ___|| \ | |  / \     / ___|/ _ \|  _ \ │
│| ' /| |_) \___ \|  \| | / _ \   | |  _| | | | | | |│
│| . \|  _ < ___) | |\  |/ ___ \  | |_| | |_| | |_| |│
│|_|\_\_| \_\____/|_| \_/_/   \_\  \____|\___/|____/ │
└────────────────────────────────────────────────────┘

"""


def show_banner():
    # Enable ANSI colors on Windows    if sys.platform == "win32":
        try:
            import os
            os.system("")
        except Exception:
            pass

    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    print(f"{CYAN}{BANNER}{RESET}")
    print(f"{MAGENTA}{BOLD}{' ' * 78}(@wjv_1){RESET}")
    print(f"{CYAN}{'━' * 90}{RESET}")
    print()


def ask(prompt, default=None):
    try:
        val = input(f"\033[93m{prompt}\033[0m").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Cancelled.")
        sys.exit(0)


def run_wizard():
    show_banner()

    # If config exists, ask user if they want to reuse
    if config_exists():
        print(f"📁 Existing config found at: {CONFIG_PATH}")
        choice = ask("Use existing config? [Y/n] : ", "y").lower()
        if choice in ("y", "yes", ""):
            cfg = load_config()
            if cfg and cfg.get("TOKENS"):
                print(f"✅ Loaded {len(cfg['TOKENS'])} token(s)\n")
                return cfg
        print("🔄 Reconfiguring...\n")

    # -------- TOKEN PROMPT --------
    print("📝 Enter your bot tokens separated by commas.")
    print("   Example: 123:ABC,456:DEF,789:GHI\n")
    tokens_raw = ask("ENTER BOT TOKEN : ")
    tokens = [t.strip() for t in tokens_raw.split(",") if t.strip()]

    if not tokens:
        print("❌ No tokens provided. Exiting.")
        sys.exit(1)

    # -------- OWNER ID PROMPT --------
    print()
    while True:
        owner_raw = ask("ENTER OWNER ID (numeric) : ")
        try:
            owner_id = int(owner_raw)
            break
        except (ValueError, TypeError):
            print("   ⚠️  Please enter a valid numeric ID.\n")

    # -------- REBRAND PROMPT --------
    print()
    rebrand = ask("ENTER REBRAND NAME : ", default="KRSNA BHAGWAN")
    if not rebrand:
        rebrand = "KRSNA BHAGWAN"

    # -------- SAVE --------
    path = save_config(tokens, owner_id, rebrand)

    print()
    print("━" * 90)
    print(f"✅ Config saved to: {path}")
    print(f"   • Tokens   : {len(tokens)}")
    print(f"   • Owner ID : {owner_id}")
    print(f"   • Rebrand  : {rebrand}")
    print("━" * 90)
    print()

    return {"TOKENS": tokens, "OWNER_ID": owner_id, "REBRAND": rebrand}


def main():
    """Entry point — runs wizard then launches the bot."""
    cfg = run_wizard()

    # Inject config into bot module
    from . import bot as bot_module
    bot_module.TOKENS = cfg["TOKENS"]
    bot_module.OWNER_ID = cfg["OWNER_ID"]
    bot_module.REBRAND = cfg["REBRAND"]

    print("🚀 Launching KRSNA BHAGWAN cluster...\n")
    bot_module.run_bot()


if __name__ == "__main__":
    main()
