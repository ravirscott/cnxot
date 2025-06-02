import logging
import random
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from typing import Dict, List, Tuple

# --- Configuration ---
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" # Replace with your bot token

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Username Generation Keywords ---
PREFIXES = [
    "Shadow", "Nova", "Cyber", "Void", "Dark", "Iron", "Star", "Lunar", "Solar",
    "Hyper", "Mega", "Captain", "Agent", "Silent", "Crimson", "Azure", "Golden"
]
CORES = [
    "Striker", "Phantom", "Wolf", "Dragon", "Serpent", "Blade", "Blitz", "Storm",
    "Hunter", "Reaper", "Guardian", "Phoenix", "Viper", "Ghost", "Arrow", "Sphinx"
]
SUFFIXES = [
    "X", "Pro", "HD", "Prime", "MKII", "Zero", "Alpha", "Omega", "Elite", "Max",
    "Playz", "Gamer", "YT", "TV", "Zone", "Realm"
]
ABSTRACT_CONCEPTS = [
    "Echo", "Rift", "Apex", "Zenith", "Flux", "Pulse", "Quasar", "Nebula", "Matrix"
]
SCI_FI_TERMS = [
    "Droid", "Cyborg", "Laser", "Plasma", "Tech", "Warp", "Bot", "Nexus", "Glitch"
]
FANTASY_ELEMENTS = [
    "Mage", "Knight", "Elf", "Orc", "Sorcerer", "Myth", "Rune", "Spell", "Quest"
]

ALL_WORDS = list(set(PREFIXES + CORES + SUFFIXES + ABSTRACT_CONCEPTS + SCI_FI_TERMS + FANTASY_ELEMENTS))
random.shuffle(ALL_WORDS) # For more varied single-word names

# --- Unicode Styles ---
# Source: Mostly https://lingojam.com/StylishTextGenerator or similar Unicode char mappers
STYLES: Dict[str, Dict[str, str]] = {
    "𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀": {
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜',
        'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥',
        'S': '𝗦', 'T': '𝗧', 'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭',
        'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳', 'g': '𝗴', 'h': '𝗵', 'i': '𝗶',
        'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻', 'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿',
        's': '𝘀', 't': '𝘁', 'u': '𝘂', 'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇',
        '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰', '5': '𝟱', '6': '𝟲', '7': '𝟳', '8': '𝟴', '9': '𝟵'
    },
    "𝘐𝘵𝘢𝘭𝘪𝘤 𝘚𝘦𝘳𝘪𝘧": {
        'A': '𝘈', 'B': '𝘉', 'C': '𝘊', 'D': '𝘋', 'E': '𝘌', 'F': '𝘍', 'G': '𝘎', 'H': '𝘏', 'I': '𝘐',
        'J': '𝘑', 'K': '𝘒', 'L': '𝘓', 'M': '𝘔', 'N': '𝘕', 'O': '𝘖', 'P': '𝘗', 'Q': '𝘘', 'R': '𝘙',
        'S': '𝘚', 'T': '𝘛', 'U': '𝘜', 'V': '𝘝', 'W': '𝘞', 'X': '𝘟', 'Y': '𝘠', 'Z': '𝘡',
        'a': '𝘢', 'b': '𝘣', 'c': '𝘤', 'd': '𝘥', 'e': '𝘦', 'f': '𝘧', 'g': '𝘨', 'h': '𝘩', 'i': '𝘪',
        'j': '𝘫', 'k': '𝘬', 'l': '𝘭', 'm': '𝘮', 'n': '𝘯', 'o': '𝘰', 'p': '𝘱', 'q': '𝘲', 'r': '𝘳',
        's': '𝘴', 't': '𝘵', 'u': '𝘶', 'v': '𝘷', 'w': '𝘸', 'x': '𝘹', 'y': '𝘺', 'z': '𝘻',
        # No widely available italic serif numbers in Unicode
    },
    "𝕸𝖊𝖉𝖎𝖊𝖛𝖆𝖑 (Fraktur)": {
        'A': '𝕬', 'B': '𝕭', 'C': '𝕮', 'D': '𝕯', 'E': '𝕰', 'F': '𝕱', 'G': '𝕲', 'H': '𝕳', 'I': '𝕴',
        'J': '𝕵', 'K': '𝕶', 'L': '𝕷', 'M': '𝕸', 'N': '𝕹', 'O': '𝕺', 'P': '𝕻', 'Q': '𝕼', 'R': '𝕽',
        'S': '𝕾', 'T': '𝕿', 'U': '𝖀', 'V': '𝖁', 'W': '𝖂', 'X': '𝖃', 'Y': '𝖄', 'Z': '𝖅',
        'a': '𝖆', 'b': '𝖇', 'c': '𝖈', 'd': '𝖉', 'e': '𝖊', 'f': '𝖋', 'g': '𝖌', 'h': '𝖍', 'i': '𝖎',
        'j': '𝖏', 'k': '𝖐', 'l': '𝖑', 'm': '𝖒', 'n': '𝖓', 'o': '𝖔', 'p': '𝖕', 'q': '𝖖', 'r': '𝖗',
        's': '𝖘', 't': '𝖙', 'u': '𝖚', 'v': '𝖛', 'w': '𝖜', 'x': '𝖝', 'y': '𝖞', 'z': '𝖟'
    },
    "Sᴍᴀʟʟ Cᴀᴘs (ʟɪᴋᴇ)": { # Not true small caps, but similar effect
        'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G', 'H': 'H', 'I': 'I',
        'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N', 'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R',
        'S': 'S', 'T': 'T', 'U': 'U', 'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ',
        'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    },
    "Mσɳσʂραƈҽ-like": {
        'A': '𝙰', 'B': '𝙱', 'C': '𝙲', 'D': '𝙳', 'E': '𝙴', 'F': '𝙵', 'G': '𝙶', 'H': '𝙷', 'I': '𝙸',
        'J': '𝙹', 'K': '𝙺', 'L': '𝙻', 'M': '𝙼', 'N': '𝙽', 'O': '𝙾', 'P': '𝙿', 'Q': '𝚀', 'R': '𝚁',
        'S': '𝚂', 'T': '𝚃', 'U': '𝚄', 'V': '𝚅', 'W': '𝚆', 'X': '𝚇', 'Y': '𝚈', 'Z': '𝚉',
        'a': '𝚊', 'b': '𝚋', 'c': '𝚌', 'd': '𝚍', 'e': '𝚎', 'f': '𝚏', 'g': '𝚐', 'h': '𝚑', 'i': '𝚒',
        'j': '𝚓', 'k': '𝚔', 'l': '𝚕', 'm': '𝚖', 'n': '𝚗', 'o': '𝚘', 'p': '𝚙', 'q': '𝚚', 'r': '𝚛',
        's': '𝚜', 't': '𝚝', 'u': '𝚞', 'v': '𝚟', 'w': '𝚠', 'x': '𝚡', 'y': '𝚢', 'z': '𝚣',
        '0': '𝟶', '1': '𝟷', '2': '𝟸', '3': '𝟹', '4': '𝟺', '5': '𝟻', '6': '𝟼', '7': '𝟽', '8': '𝟾', '9': '𝟿'
    },
    "Ⓒⓘⓡⓒⓛⓔⓓ": {
        'A': 'Ⓐ', 'B': 'Ⓑ', 'C': 'Ⓒ', 'D': 'Ⓓ', 'E': 'Ⓔ', 'F': 'Ⓕ', 'G': 'Ⓖ', 'H': 'Ⓗ', 'I': 'Ⓘ',
        'J': 'Ⓙ', 'K': 'Ⓚ', 'L': 'Ⓛ', 'M': 'Ⓜ', 'N': 'Ⓝ', 'O': 'Ⓞ', 'P': 'Ⓟ', 'Q': 'Ⓠ', 'R': 'Ⓡ',
        'S': 'Ⓢ', 'T': 'Ⓣ', 'U': 'Ⓤ', 'V': 'Ⓥ', 'W': 'Ⓦ', 'X': 'Ⓧ', 'Y': 'Ⓨ', 'Z': 'Ⓩ',
        'a': 'ⓐ', 'b': 'ⓑ', 'c': 'ⓒ', 'd': 'ⓓ', 'e': 'ⓔ', 'f': 'ⓕ', 'g': 'ⓖ', 'h': 'ⓗ', 'i': 'ⓘ',
        'j': 'ⓙ', 'k': 'ⓚ', 'l': 'ⓛ', 'm': 'ⓜ', 'n': 'ⓝ', 'o': 'ⓞ', 'p': 'ⓟ', 'q': 'ⓠ', 'r': 'ⓡ',
        's': 'ⓢ', 't': 'ⓣ', 'u': 'ⓤ', 'v': 'ⓥ', 'w': 'ⓦ', 'x': 'ⓧ', 'y': 'ⓨ', 'z': 'ⓩ',
         # Numbers 1-20 exist, then 0, then some others. For simplicity, only including 0-9
        '0': '⓪', '1': '①', '2': '②', '3': '③', '4': '④', '5': '⑤', '6': '⑥', '7': '⑦', '8': '⑧', '9': '⑨'
    },
    "Slashed": { # Not all chars exist
        'A': 'Ⱥ', 'B': 'Ƀ', 'C': 'Ȼ', 'D': 'Đ', 'E': 'Ɇ', 'F': 'Ƒ', 'G': 'Ǥ', 'H': 'Ħ', 'I': 'Ɨ',
        'J': 'Ɉ', 'K': 'Ꝁ', 'L': 'Ł', 'M': 'Ӎ', 'N': '₦', 'O': 'Ø', 'P': 'Ꝑ', 'Q': 'Ꝗ', 'R': 'Ɍ',
        'S': 'S̸', 'T': 'Ŧ', 'U': 'Ʉ', 'V': 'V̸', 'W': 'W̸', 'X': 'X̸', 'Y': 'Ɏ', 'Z': 'Ƶ',
        'a': 'ⱥ', 'b': 'ƀ', 'c': 'ȼ', 'd': 'đ', 'e': 'ɇ', 'f': 'ƒ', 'g': 'ǥ', 'h': 'ħ', 'i': 'ɨ',
        'j': 'ɉ', 'k': 'ꝁ', 'l': 'ł', 'm': 'ӎ', 'n': 'ɲ', 'o': 'ø', 'p': 'ꝑ', 'q': 'ꝗ', 'r': 'ɍ',
        's': 's̸', 't': 'ŧ', 'u': 'ʉ', 'v': 'v̸', 'w': 'w̸', 'x': 'x̸', 'y': 'ɏ', 'z': 'ƶ',
        '0': '0̸', '1': '1̸', '2': '2̸', '3': '3̸', '4': '4̸', '5': '5̸', '6': '6̸', '7': '7̸', '8': '8̸', '9': '9̸'
    },
    "Upside Down": { # Very limited character set
        'a': 'ɐ', 'b': 'q', 'c': 'ɔ', 'd': 'p', 'e': 'ǝ', 'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ',
        'i': 'ᴉ', 'j': 'ɾ', 'k': 'ʞ', 'l': 'l', 'm': 'ɯ', 'n': 'u', 'o': 'o', 'p': 'd',
        'q': 'b', 'r': 'ɹ', 's': 's', 't': 'ʇ', 'u': 'n', 'v': 'ʌ', 'w': 'ʍ', 'x': 'x',
        'y': 'ʎ', 'z': 'z',
        'A': '∀', 'B': 'B', 'C': 'Ɔ', 'D': 'D', 'E': 'Ǝ', 'F': 'Ⅎ', 'G': 'פ', 'H': 'H',
        'I': 'I', 'J': 'ſ', 'K': 'K', 'L': '˥', 'M': 'W', 'N': 'N', 'O': 'O', 'P': 'Ԁ',
        'Q': 'Q', 'R': 'R', 'S': 'S', 'T': '⊥', 'U': '∩', 'V': 'Λ', 'W': 'M', 'X': 'X',
        'Y': '⅄', 'Z': 'Z',
        '0':'0', '1':'Ɩ', '2':'ᄅ', '3':'Ɛ', '4':'ㄣ', '5':'ϛ', '6':'9', '7':'ㄥ', '8':'8', '9':'6',
        '.':'˙', ',':'\'', '?':'¿', '!':'¡'
    }
}

DEFAULT_STYLE_FOR_GENERATE = "𝗕𝗼𝗹𝗱 𝗦𝗮𝗻𝘀" # Or choose one randomly

# --- Helper Functions ---
def generate_single_username(keyword: str = None) -> str:
    """Generates a single unique-ish username."""
    name = ""
    if keyword:
        keyword = keyword.capitalize()
        # Try to integrate keyword
        rand_choice = random.randint(0, 4)
        if rand_choice == 0 and keyword not in PREFIXES : name = keyword + random.choice(CORES)
        elif rand_choice == 1 and keyword not in CORES: name = random.choice(PREFIXES) + keyword
        elif rand_choice == 2 and keyword not in SUFFIXES: name = keyword + random.choice(SUFFIXES)
        elif rand_choice == 3: name = keyword + str(random.randint(1, 999))
        else: name = keyword # Fallback if keyword is too generic or to use as is

    if not name or len(name) < 3: # If keyword logic didn't produce much, or no keyword
        pattern = random.randint(0, 7)
        if pattern == 0: name = random.choice(PREFIXES) + random.choice(CORES)
        elif pattern == 1: name = random.choice(CORES) + random.choice(SUFFIXES)
        elif pattern == 2: name = random.choice(PREFIXES) + random.choice(CORES) + random.choice(SUFFIXES)
        elif pattern == 3: name = random.choice(ALL_WORDS) + str(random.randint(1, 999))
        elif pattern == 4: name = random.choice(PREFIXES) + str(random.randint(10, 999))
        elif pattern == 5: name = random.choice(CORES) + str(random.randint(1, 99)) + random.choice(SUFFIXES)
        elif pattern == 6: name = random.choice(ALL_WORDS) + random.choice(ALL_WORDS) # Could be long
        else: name = random.choice(ALL_WORDS)

    # Add numbers sometimes
    if random.random() < 0.4 and not any(char.isdigit() for char in name):
        name += str(random.randint(1, 999))

    # Basic cleanup: remove spaces, ensure reasonable length
    name = re.sub(r'\s+', '', name)
    if len(name) > 20: name = name[:20] # Max length
    if len(name) < 4: name = name + random.choice(CORES) # Ensure min length

    return name.capitalize()


def stylize_text(text: str, style_name: str) -> str:
    """Applies a Unicode style to the text."""
    if style_name not in STYLES:
        return text # Return original if style not found

    style_map = STYLES[style_name]
    styled_text = ""
    for char in text:
        styled_text += style_map.get(char, char) # Fallback to original char if not in map
    return styled_text

# --- Command Handlers ---
async def start_command(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message when the /start command is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Hello {user.mention_html()}!\n\n"
        f"I am 𝗦𝘁𝘆𝗹𝗲𝗡𝗮𝗺𝗲 𝗣𝗿𝗼, your game username generator.\n\n"
        f"Here's how to use me:\n"
        f"🔹 /generate - Get 20 cool username ideas.\n"
        f"🔹 /generate [keyword] - Get names based on your keyword (e.g., `/generate Dragon`).\n"
        f"🔹 /stylize [name] - See a name in all available styles.\n"
        f"🔹 /styles - Preview all available text styles.\n"
        f"🔹 /help - Show this message again.\n\n"
        f"Let's find your perfect game name!"
    )
    await update.message.reply_html(welcome_message)

async def help_command(update: Update, context: CallbackContext) -> None:
    """Sends help message."""
    await start_command(update, context) # Re-use the start message as help

async def styles_command(update: Update, context: CallbackContext) -> None:
    """Shows a preview of all available Unicode text styles."""
    sample_text = "StyleDemo123"
    response_lines = ["🎨 Here are the available styles:\n"]
    for style_name in STYLES:
        styled_sample = stylize_text(sample_text, style_name)
        response_lines.append(f"🔹 {style_name}: `{styled_sample}`") # Monospace for copy

    await update.message.reply_text("\n".join(response_lines), parse_mode='MarkdownV2')

async def generate_command(update: Update, context: CallbackContext) -> None:
    """Generates a list of unique base usernames."""
    keyword = None
    if context.args:
        keyword = " ".join(context.args).strip()
        if not re.match(r"^[a-zA-Z0-9\s]+$", keyword) or len(keyword) > 15: # Basic validation
            await update.message.reply_text("⚠️ Invalid keyword. Please use letters, numbers, and spaces (max 15 chars).")
            return
        keyword = keyword.split()[0] # Take first word if multiple

    num_suggestions = 20
    generated_names = set()
    attempts = 0
    max_attempts = num_suggestions * 3 # Try more to ensure uniqueness

    while len(generated_names) < num_suggestions and attempts < max_attempts:
        name = generate_single_username(keyword)
        if name: # Ensure name is not empty
            generated_names.add(name)
        attempts += 1

    if not generated_names:
        await update.message.reply_text("😥 Sorry, I couldn't generate any names. Try a different keyword or try again!")
        return

    response_lines = [f"✨ Here are {len(generated_names)} username ideas for you!"]
    if keyword:
        response_lines[0] += f" (based on '{keyword}')"
    response_lines.append("Tap a name to see styling options, or use `/stylize [name]`\n")


    keyboard = []
    for i, name in enumerate(list(generated_names)[:num_suggestions]):
        # Each name on its own line with an inline button
        response_lines.append(f"🔸 {name}")
        keyboard.append([InlineKeyboardButton(f"🎨 Style '{name}'", callback_data=f"style_{name[:30]}")]) # Limit callback data length

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("\n".join(response_lines), reply_markup=reply_markup)


async def stylize_command_or_callback(update: Update, context: CallbackContext, username_to_style: str = None) -> None:
    """
    Stylizes a given username in all available styles.
    Can be called directly by /stylize command or via callback query.
    """
    if username_to_style is None: # Called by /stylize command
        if not context.args:
            await update.message.reply_text("❓ Usage: /stylize [YourNameHere]")
            return
        username_to_style = " ".join(context.args)
    
    if not re.match(r"^[a-zA-Z0-9\s]+$", username_to_style) or len(username_to_style) > 25:
        msg = "⚠️ Invalid name for styling. Please use letters, numbers, and spaces (max 25 chars)."
        if update.callback_query: await update.callback_query.answer(msg, show_alert=True)
        else: await update.message.reply_text(msg)
        return

    username_to_style = username_to_style.strip()
    response_lines = [f"💅 Styles for '`{username_to_style}`':\n"]
    response_lines.append(f"🔹 Plain: `{username_to_style}`")

    for style_name, style_map in STYLES.items():
        # Check if style is applicable (e.g., "Upside Down" is very limited)
        can_style = True
        if style_name == "Upside Down": # Example of a style with limited char set
             if not all(c.lower() in style_map or c.isspace() or c.isdigit() for c in username_to_style if c.isalpha()):
                 can_style = False # Skip if many chars are not in this specific map
        
        if can_style:
            styled_name = stylize_text(username_to_style, style_name)
            # Using Markdown for `monospace` to make it copyable
            response_lines.append(f"🔹 {style_name}: `{styled_name}`")

    full_response = "\n".join(response_lines)

    if update.callback_query:
        try:
            # Try editing the original message if it's short enough and makes sense
            # For styling, sending a new message is usually clearer
            await update.callback_query.answer() # Acknowledge callback
            await context.bot.send_message(chat_id=update.effective_chat.id, text=full_response, parse_mode='MarkdownV2')
        except Exception as e:
            logger.error(f"Error in callback stylize: {e}")
            # Fallback if edit fails or message is too long
            await context.bot.send_message(chat_id=update.effective_chat.id, text=full_response, parse_mode='MarkdownV2')
    else:
        await update.message.reply_text(full_response, parse_mode='MarkdownV2')


async def button_callback(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and Ntargets the right handler."""
    query = update.callback_query
    await query.answer() # Acknowledge the button press

    data = query.data
    if data.startswith("style_"):
        username_to_style = data[len("style_"):]
        # Call the stylize logic, passing the username
        await stylize_command_or_callback(update, context, username_to_style=username_to_style)
    # Add more callback data handlers if needed

# --- Main Bot Execution ---
def main() -> None:
    """Start the bot."""
    if TELEGRAM_BOT_TOKEN == "8073261871:AAEA8o9R8loWe-PJB7epforlZOuDFB8_mlc":
        logger.error("CRITICAL: Bot token is not set. Please replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("styles", styles_command))
    application.add_handler(CommandHandler("generate", generate_command))
    application.add_handler(CommandHandler("stylize", stylize_command_or_callback)) # Direct command

    # CallbackQuery handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    logger.info("StyleName Pro Bot started!")
    application.run_polling()

if __name__ == '__main__':
    main()
