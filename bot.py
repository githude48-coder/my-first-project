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
                return json.load(f)
        except:
            return {"games": [], "posted_ids": []}
    return {"games": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- ဖိုင်ပို့ရင် ချက်ချင်း သိမ်းပြီး ပြန်ဖြေမယ့်အပိုင်း ---
@bot.message_handler(content_types=['document'])
def handle_incoming_file(message):
    db = load_db()
    file_name = message.document.file_name.replace(".apk", "").replace("-", " ").title()
    
    # Database ထဲ ထည့်မယ်
    db["games"].append({
        "original_msg_id": message.message_id,
        "from_chat_id": message.chat.id,
        "name": file_name
    })
    save_db(db)
    
    # ဒီစာသားလေး ပေါ်လာရင် Bot အလုပ်လုပ်နေတာ သေချာပါပြီ
    bot.reply_to(message, f"✅ သိမ်းလိုက်ပါပြီ- {file_name}\n\nအခု GitHub Actions ကိုသွားပြီး Run workflow နှိပ်ရင် Post တင်ပေးပါလိမ့်မယ်။")

def auto_run_process():
    db = load_db()
    all_games = db.get("games", [])
    posted_ids = db.get("posted_ids", [])
    available = [g for g in all_games if str(g["original_msg_id"]) not in posted_ids]

    if not available:
        db["posted_ids"] = []
        available = all_games
        if not available: return

    selected = random.choice(available)
    try:
        sent_file = bot.copy_message(FILE_STORE_CH, selected["from_chat_id"], selected["original_msg_id"])
        clean_ch = FILE_STORE_CH.replace("@", "")
        file_link = f"https://t.me/{clean_ch}/{sent_file.message_id}"

        caption = (
            f"Game: **{selected['name']}** ❞\n\n"
            f"Offline 🚩 ❞\n\n"
            f"Link: [ [Download]({file_link}) ] ❞"
        )
        bot.send_message(POST_CH, caption, parse_mode="Markdown")
        db["posted_ids"].append(str(selected["original_msg_id"]))
        save_db(db)
        print(f"Success: Posted {selected['name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
    else:
        # Bot ကို ခဏ Live ပေးထားမယ် (ဖိုင်တွေ ပို့နေတဲ့အချိန်မှာ)
        print("Bot is listening... (ဖိုင်တွေ ပို့လို့ရပါပြီ)")
        bot.polling(none_stop=True)

