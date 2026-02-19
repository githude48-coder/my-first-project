import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
FILE_STORE_CH = "@offlinegamelink" 
POST_CH = "@offlinegame999"      
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                if "games" not in data: data["games"] = []
                if "posted_ids" not in data: data["posted_ids"] = []
                return data
        except:
            return {"games": [], "posted_ids": []}
    return {"games": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- AUTO SYNC: Bot ဆီပို့ထားသမျှ ဖိုင်တွေကို Database ထဲ အလိုလို ထည့်ပေးမည့်အပိုင်း ---
def sync_new_files():
    db = load_db()
    print("Checking for new files in bot messages...")
    
    # ဤအပိုင်းသည် Bot ဆီသို့ သင်နောက်ဆုံးပို့ထားသော Update များကို စစ်ဆေးသည်
    updates = bot.get_updates()
    added_count = 0
    
    for update in updates:
        if update.message and update.message.document:
            file_id = update.message.message_id
            # စာရင်းထဲမှာ မရှိသေးရင် အသစ်ထည့်မယ်
            if not any(g['original_msg_id'] == file_id for g in db["games"]):
                file_name = update.message.document.file_name.replace(".apk", "").replace("-", " ").title()
                db["games"].append({
                    "original_msg_id": file_id,
                    "chat_id": update.message.chat.id,
                    "name": file_name
                })
                added_count += 1
    
    if added_count > 0:
        save_db(db)
        print(f"ဂိမ်းအသစ် {added_count} ခုကို Database ထဲ Auto ထည့်ပြီးပါပြီ။")
    else:
        print("ဂိမ်းအသစ် မတွေ့ပါ။")

def auto_run_process():
    sync_new_files() # အရင်ဆုံး ဖိုင်အသစ်တွေကို စာရင်းထဲ အလိုလို သွင်းမယ်
    
    db = load_db()
    all_games = db.get("games", [])
    posted_ids = db.get("posted_ids", [])
    
    available = [g for g in all_games if str(g["original_msg_id"]) not in posted_ids]

    if not available:
        print("တင်စရာ ဂိမ်းမရှိပါ။")
        return

    selected = random.choice(available)
    try:
        # ၁။ Storage Channel ဆီ File ကို Copy ကူးပို့မယ်
        sent_file = bot.copy_message(FILE_STORE_CH, selected["chat_id"], selected["original_msg_id"])
        
        # ၂။ Link တည်ဆောက်မယ်
        clean_ch = FILE_STORE_CH.replace("@", "")
        file_link = f"https://t.me/{clean_ch}/{sent_file.message_id}"

        # ၃။ Main Channel မှာ Post တင်မယ်
        caption = (
            f"Game: **{selected['name']}** ❞\n\n"
            f"Offline 🚩 ❞\n\n"
            f"Link: [ [Download]({file_link}) ] ❞"
        )
        bot.send_message(POST_CH, caption, parse_mode="Markdown")
        
        # ၄။ တင်ပြီးကြောင်း မှတ်မယ်
        db["posted_ids"].append(str(selected["original_msg_id"]))
        save_db(db)
        print(f"Success: Posted {selected['name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
    else:
        bot.polling(none_stop=True)
