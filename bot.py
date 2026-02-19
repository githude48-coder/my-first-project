import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
POST_CH = "@offlinegame999"  # Forward တင်မည့် Channel
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                if "posts" not in data: data["posts"] = []
                if "posted_ids" not in data: data["posted_ids"] = []
                return data
        except:
            return {"posts": [], "posted_ids": []}
    return {"posts": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# သင် Bot ဆီ ပို့ထားတဲ့ ပုံ+စာ ပါတဲ့ Post တွေကို Database ထဲ မှတ်မယ်
def sync_posts():
    db = load_db()
    updates = bot.get_updates()
    added = 0
    for update in updates:
        if update.message:
            msg_id = update.message.message_id
            # စာရင်းထဲမှာ မရှိသေးရင် မှတ်မယ် (KeyError မဖြစ်အောင် posts လို့ပဲ သုံးထားတယ်)
            if not any(p['id'] == msg_id for p in db["posts"]):
                db["posts"].append({
                    "id": msg_id,
                    "chat_id": update.message.chat.id
                })
                added += 1
    if added > 0:
        save_db(db)
        print(f"Added {added} new posts to database.")

def auto_run_process():
    sync_posts()
    db = load_db()
    
    # မတင်ရသေးတဲ့ Post တွေကို ရှာမယ်
    available = [p for p in db["posts"] if str(p["id"]) not in db["posted_ids"]]

    if not available:
        print("တင်စရာ Post အသစ် မရှိပါ။")
        return

    selected = random.choice(available)
    try:
        # သင်ကိုယ်တိုင် ရေးထားတဲ့ Post ကို Forward (Copy) လုပ်မယ်
        # disable_notification=True နဲ့ link_preview အကွက်ကြီး မပါအောင် လုပ်ထားတယ်
        bot.copy_message(
            chat_id=POST_CH,
            from_chat_id=selected["chat_id"],
            message_id=selected["id"]
        )
        
        db["posted_ids"].append(str(selected["id"]))
        save_db(db)
        print(f"Success: Forwarded Post ID {selected['id']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
    else:
        bot.polling(none_stop=True)
