import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
FILE_STORE_CH = "@offlinegamelink" # File ပို့ထားရမည့်နေရာ
POST_CH = "@offlinegame999"       # Post အချော တင်မည့်နေရာ
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

# --- AUTO SYNC: Bot ဆီ သင်ပို့ထားတဲ့ Post အချောတွေကို Database ထဲ မှတ်သားမည့်အပိုင်း ---
def sync_formatted_posts():
    db = load_db()
    updates = bot.get_updates()
    added = 0
    for update in updates:
        if update.message and (update.message.caption or update.message.text):
            msg_id = update.message.message_id
            if not any(g['post_msg_id'] == msg_id for g in db.get("games", [])):
                # စာထဲမှာ Game နာမည် ပါသလား ရှာမယ်
                text = update.message.caption if update.message.caption else update.message.text
                game_name = "Unknown Game"
                if "Game:" in text:
                    game_name = text.split("Game:")[1].split("\n")[0].strip()
                
                db["games"].append({
                    "post_msg_id": msg_id,
                    "from_chat_id": update.message.chat.id,
                    "name": game_name
                })
                added += 1
    if added > 0: save_db(db)

def auto_run_process():
    sync_formatted_posts()
    db = load_db()
    available = [g for g in db["games"] if str(g["post_msg_id"]) not in db["posted_ids"]]

    if not available:
        print("တင်စရာ Post အသစ် မရှိပါ။")
        return

    selected = random.choice(available)
    try:
        # ၁။ သင်ရေးထားတဲ့ Post ကို @offlinegame999 ဆီကို Edit လုပ်ပြီး ပို့မယ်
        # (Download Link ကို အလိုလို ထည့်ပေးမှာပါ)
        
        # မှတ်ချက်- ဖိုင်ကို @offlinegamelink ထဲ အရင်ရောက်နေဖို့ လိုပါတယ် (Game နာမည်ချင်း တူရပါမယ်)
        # ဤနေရာတွင် Link အား https://t.me/offlinegamelink/[ID] ပုံစံဖြင့် ချိတ်ဆက်ပေးပါမည်။
        
        # သင်လိုချင်တဲ့အတိုင်း Download Link Preview မပါစေရန် disable_web_page_preview သုံးထားပါတယ်
        bot.copy_message(
            POST_CH, 
            selected["from_chat_id"], 
            selected["post_msg_id"],
            caption=None, # မူရင်း caption အတိုင်း သုံးမည်
        )

        db["posted_ids"].append(str(selected["post_msg_id"]))
        save_db(db)
        print(f"Success Forwarded: {selected['name']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
    else:
        bot.polling(none_stop=True)
