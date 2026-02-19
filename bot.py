import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
FILE_STORE_CH = "@offlinegamelink" # File များသာ သိမ်းမည့်နေရာ
POST_CH = "@offlinegame999"      # Post အလှများသာ တင်မည့်နေရာ
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"posts": [], "posted_ids": []}
    return {"posts": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def sync_data():
    db = load_db()
    updates = bot.get_updates()
    for update in updates:
        if update.message:
            msg = update.message
            # ၁။ အကယ်၍ ပို့လိုက်တာက APK File ဖြစ်နေရင် Storage Channel ဆီ ပို့မယ်
            if msg.document and msg.document.file_name.endswith(".apk"):
                bot.copy_message(FILE_STORE_CH, msg.chat.id, msg.message_id)
                print(f"File Saved to Storage: {msg.document.file_name}")
            
            # ၂။ အကယ်၍ ပို့လိုက်တာက ပုံ+စာ ပါတဲ့ Post ဖြစ်နေရင် Database ထဲ မှတ်မယ်
            elif (msg.caption or msg.text) and not msg.document:
                if not any(p.get('id') == msg.message_id for p in db.get("posts", [])):
                    db["posts"].append({"id": msg.message_id, "chat_id": msg.chat.id})
                    print("New Formatted Post Synced!")
    save_db(db)

def auto_run_process():
    sync_data()
    db = load_db()
    available = [p for p in db.get("posts", []) if str(p.get('id')) not in db.get("posted_ids", [])]

    if not available:
        print("No new posts to forward.")
        return

    selected = random.choice(available)
    try:
        # သင်ရေးထားတဲ့ Post သန့်သန့်လေးကိုပဲ Forward တင်မယ်
        # ဖိုင်ကပ်ပါလာတာမျိုး လုံးဝမဖြစ်စေရပါဘူး
        bot.copy_message(
            chat_id=POST_CH, 
            from_chat_id=selected["chat_id"], 
            message_id=selected["id"]
        )
        
        db["posted_ids"].append(str(selected["id"]))
        save_db(db)
        print(f"Post {selected['id']} Forwarded Successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
    else:
        bot.polling(none_stop=True)
