import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
OFFLINE_CH = "@offlinegamelink"
MAIN_CH = "@offlinegame999"
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"games": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# File ပို့ရင် Database ထဲ ထည့်မယ့်အပိုင်း
@bot.message_handler(content_types=['document'])
def handle_file(message):
    db = load_db()
    file_name = message.document.file_name
    sent_msg = bot.copy_message(OFFLINE_CH, message.chat.id, message.message_id)
    file_link = f"https://t.me/{OFFLINE_CH.replace('@','')}/{sent_msg.message_id}"
    
    # Game နာမည်ကို File နာမည်ကနေ အလိုလိုယူမယ်
    db["games"].append({"id": sent_msg.message_id, "name": file_name, "link": file_link})
    save_db(db)
    bot.reply_to(message, "✅ Database ထဲ သိမ်းလိုက်ပါပြီ!")

# မတင်ရသေးတာကို ခြေရာခံပြီး တင်ပေးမယ့်အပိုင်း
def auto_post():
    db = load_db()
    all_games = db["games"]
    posted_ids = db["posted_ids"]

    # မတင်ရသေးတဲ့ Game တွေကိုပဲ စစ်ထုတ်မယ်
    available = [g for g in all_games if g["id"] not in posted_ids]

    if not available:
        # အကုန်တင်ပြီးရင် အစက ပြန်စမယ် (Limit ပြည့်သွားလျှင်)
        db["posted_ids"] = []
        available = all_games
        if not available: return

    selected = random.choice(available)
    caption = f"Game: {selected['name']}\n\nOffline 🚩\n\nLink: [ [Download]({selected['link']}) ]"

    try:
        bot.send_message(MAIN_CH, caption, parse_mode="Markdown")
        db["posted_ids"].append(selected["id"])
        save_db(db)
        print(f"Posted: {selected['name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_post()
    else:
        bot.polling(none_stop=True)
