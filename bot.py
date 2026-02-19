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
                # Key များစစ်ဆေးခြင်း
                if "games" not in data: data["games"] = []
                if "posted_ids" not in data: data["posted_ids"] = []
                if "file_data" not in data: data["file_data"] = {}
                return data
        except:
            return {"games": [], "posted_ids": [], "file_data": {}}
    return {"games": [], "posted_ids": [], "file_data": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    # Update အသစ်များကို ဖမ်းယူခြင်း
    updates = bot.get_updates(offset=-50, limit=100)
    
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # APK File သိမ်းဆည်းခြင်း
        if msg.document and msg.document.file_name.endswith(".apk"):
            file_key = msg.document.file_name.lower().split("-")[0].strip()
            db["file_data"][file_key] = {
                "message_id": msg.message_id,
                "chat_id": msg.chat.id
            }

        # Post (ပုံ+စာ) သိမ်းဆည်းခြင်း
        elif (msg.caption or msg.text) and (msg.photo or msg.video):
            text = msg.caption if msg.caption else msg.text
            if "Game:" in text:
                game_name = text.split("Game:")[1].split("\n")[0].strip().lower()
                if not any(g['post_id'] == msg.message_id for g in db["games"]):
                    db["games"].append({
                        "name": game_name,
                        "post_id": msg.message_id,
                        "chat_id": msg.chat.id
                    })
    save_db(db)

    # ၂။ မတင်ရသေးတာထဲက တစ်ခုတည်းကိုပဲ ကျပန်းရွေးမယ်
    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    
    if not available:
        print("တင်စရာ အသစ်မရှိပါ။")
        return

    # တစ်ခုတည်းကိုပဲ ကျပန်းရွေးချယ်
    selected = random.choice(available)
    game_key = selected["name"].split(" ")[0].strip()
    file_info = db["file_data"].get(game_key)

    try:
        # ၃။ Post ကို အရင်တင်မယ်
        bot.copy_message(POST_CH, selected["chat_id"], selected["post_id"])
        
        # ၄။ File ရှိရင် အောက်ကနေ ချက်ချင်းလိုက်တင်မယ်
        if file_info:
            bot.copy_message(POST_CH, file_info["chat_id"], file_info["message_id"])
            print(f"Success: Posted {selected['name']} with File.")
        else:
            print(f"Warning: File not found for {game_key}")

        # ၅။ တင်ပြီးကြောင်း ID ကို သေချာမှတ်မယ် (ဒါမှ နောက်တစ်ခါ အများကြီး ပြန်မတက်မှာပါ)
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        return 

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    auto_run_process()
