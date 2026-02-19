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

# ၁။ Bot ဆီ ဖိုင်ပို့ရင် နာမည်နဲ့ ID ကို မှတ်ထားမယ့်အပိုင်း
@bot.message_handler(content_types=['document'])
def handle_incoming_file(message):
    db = load_db()
    # ဖိုင်နာမည်ကို ဂိမ်းနာမည်အဖြစ် သတ်မှတ်မယ်
    file_name = message.document.file_name.replace(".apk", "").replace("-", " ").title()
    
    db["games"].append({
        "original_msg_id": message.message_id,
        "chat_id": message.chat.id,
        "name": file_name
    })
    save_db(db)
    bot.reply_to(message, f"✅ Database ထဲ သိမ်းလိုက်ပါပြီ - {file_name}")

# ၂။ အဓိက အလုပ်လုပ်မယ့် ကျပန်း Post တင်စနစ်
def auto_run_process():
    db = load_db()
    all_games = db.get("games", [])
    posted_ids = db.get("posted_ids", [])

    # မတင်ရသေးတဲ့ Game ကို ရှာမယ်
    available = [g for g in all_games if str(g["original_msg_id"]) not in posted_ids]

    if not available:
        # အကုန်တင်ပြီးရင် အစက ပြန်စမယ် (Limit ပြည့်ရင်)
        db["posted_ids"] = []
        available = all_games
        if not available:
            print("Database ထဲမှာ ဂိမ်းမရှိသေးပါ။")
            return

    # ကျပန်းစနစ်နဲ့ ဂိမ်းတစ်ခု ရွေးမယ်
    selected = random.choice(available)

    try:
        # (က) File ကို Storage Channel (@offlinegamelink) ဆီ အရင်ပို့မယ်
        sent_file = bot.copy_message(FILE_STORE_CH, selected["chat_id"], selected["original_msg_id"])
        
        # (ခ) အဲ့ဒီ ပို့လိုက်တဲ့ File ရဲ့ Direct Link ကို တည်ဆောက်မယ်
        # ဒါမှ Download နှိပ်ရင် အဲ့ဒီဖိုင်ဆီ တန်းရောက်မှာပါ
        clean_ch = FILE_STORE_CH.replace("@", "")
        file_link = f"https://t.me/{clean_ch}/{sent_file.message_id}"

        # (ဂ) Main Channel မှာ Post တင်မယ်
        caption = (
            f"Game: **{selected['name']}** ❞\n\n"
            f"Offline 🚩 ❞\n\n"
            f"Link: [ [Download]({file_link}) ] ❞"
        )
        
        bot.send_message(POST_CH, caption, parse_mode="Markdown")

        # (ဃ) တင်ပြီးကြောင်း မှတ်မယ်
        db["posted_ids"].append(str(selected["original_msg_id"]))
        save_db(db)
        print(f"Success: Posted {selected['name']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # GitHub Actions က run တဲ့အခါ Post တင်မယ်
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
    else:
        # ပုံမှန်အချိန်ဆိုရင် Bot ကို ဖိုင်လက်ခံဖို့ ဖွင့်ထားမယ်
        print("Bot is listening for files...")
        bot.polling(none_stop=True)
