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
                return data if "games" in data else {"games": [], "posted_ids": []}
        except:
            return {"games": [], "posted_ids": []}
    return {"games": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    updates = bot.get_updates()
    
    # ၁။ ဂိမ်းဖိုင်နဲ့ Post ကို ခွဲခြားပြီး စာရင်းသွင်းမယ်
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # အကယ်၍ APK File ဖြစ်နေရင် Storage ဆီ ပို့မယ်
        if msg.document and msg.document.file_name.endswith(".apk"):
            bot.copy_message(FILE_STORE_CH, msg.chat.id, msg.message_id)
            print(f"File Saved: {msg.document.file_name}")
            
        # အကယ်၍ ပုံ+စာ ပါတဲ့ Post ဖြစ်နေရင် Database ထဲ မှတ်မယ်
        elif (msg.caption or msg.text) and not msg.document:
            text = msg.caption if msg.caption else msg.text
            if "Game:" in text:
                game_name = text.split("Game:")[1].split("\n")[0].strip()
                if not any(g['name'] == game_name for g in db["games"]):
                    db["games"].append({
                        "name": game_name,
                        "post_id": msg.message_id,
                        "chat_id": msg.chat.id
                    })
    save_db(db)

    # ၂။ မတင်ရသေးတဲ့ ဂိမ်းတစ်ခုတည်းကိုပဲ ရွေးမယ်
    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    
    if not available:
        print("တင်စရာ Post အသစ်မရှိပါ။")
        return

    selected = random.choice(available)
    
    try:
        # ၃။ Post တစ်ခုတည်းကိုပဲ Forward တင်မယ်
        bot.copy_message(POST_CH, selected["chat_id"], selected["post_id"])
        
        # ၄။ တင်ပြီးကြောင်း မှတ်မယ် (တစ်ခုပဲ တင်ပြီးတာနဲ့ ရပ်မယ်)
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print(f"Success: Posted {selected['name']} only.")
        return 

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
