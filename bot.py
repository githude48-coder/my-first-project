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
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"games": [], "posted_ids": []}
    return {"games": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    db = load_db()
    file_name = message.document.file_name
    try:
        sent_msg = bot.copy_message(OFFLINE_CH, message.chat.id, message.message_id)
        file_link = f"https://t.me/offlinegamelink/{sent_msg.message_id}"
        
        new_game = {"id": sent_msg.message_id, "name": file_name, "link": file_link}
        db["games"].append(new_game)
        save_db(db)
        bot.reply_to(message, f"✅ သိမ်းပြီးပါပြီ - {file_name}")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

def auto_post():
    db = load_db()
    all_games = db.get("games", [])
    posted_ids = db.get("posted_ids", [])

    if not all_games:
        print("Database ထဲမှာ Game မရှိသေးပါ။")
        return

    if len(posted_ids) >= len(all_games):
        db["posted_ids"] = []
        posted_ids = []

    available = [g for g in all_games if g["id"] not in posted_ids]
    if not available: return
    selected = random.choice(available)

    caption = (
        f"Game: {selected['name']} ❞\n\n"
        f"Offline 🚩 ❞\n\n"
        f"Link: [ [Download]({selected['link']}) ] ❞"
    )

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
        print("Bot is listening...")
        bot.polling(none_stop=True)
