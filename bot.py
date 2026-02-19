import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
POST_CH = "@offlinegame999"
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, dict) and "posts" in data else {"posts": [], "posted_ids": []}
        except:
            return {"posts": [], "posted_ids": []}
    return {"posts": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def sync_posts():
    db = load_db()
    updates = bot.get_updates()
    added = 0
    for update in updates:
        if update.message:
            msg_id = update.message.message_id
            if not any(p.get('id') == msg_id for p in db.get("posts", [])):
                db["posts"].append({"id": msg_id, "chat_id": update.message.chat.id})
                added += 1
    if added > 0:
        save_db(db)
        print(f"Added {added} new posts.")

def auto_run_process():
    sync_posts()
    db = load_db()
    available = [p for p in db.get("posts", []) if str(p.get('id')) not in db.get("posted_ids", [])]

    if not available:
        print("No new posts to forward.")
        return

    selected = random.choice(available)
    try:
        # သင်ရေးထားတဲ့ ပုံရော၊ စာရော ပါတဲ့ Message ကို Forward (Copy) လုပ်မယ်
        bot.copy_message(chat_id=POST_CH, from_chat_id=selected["chat_id"], message_id=selected["id"])
        db["posted_ids"].append(str(selected["id"]))
        save_db(db)
        print(f"Forwarded Post ID {selected['id']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
