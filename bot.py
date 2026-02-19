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

# Bot ဆီ ဖိုင်ပို့ရင် သိမ်းမယ့်အပိုင်း
@bot.message_handler(content_types=['document'])
def handle_incoming_file(message):
    db = load_db()
    file_name = message.document.file_name.replace(".apk", "").replace("-", " ").title()
    db["games"].append({
        "original_msg_id": message.message_id,
        "from_chat_id": message.chat.id,
        "name": file_name
    })
    save_db(db)
    bot.reply_to(message, f"✅ သိမ်းပြီးပါပြီ - {file_name}")

def auto_run_process():
    print("Process စတင်နေပြီ...")
    db = load_db()
    all_games = db.get("games", [])
    posted_ids = db.get("posted_ids", [])
    
    # မတင်ရသေးတဲ့ Game ရှာမယ်
    available = [g for g in all_games if str(g["original_msg_id"]) not in posted_ids]
    
    print(f"စုစုပေါင်း Game: {len(all_games)} ခုရှိပြီး မတင်ရသေးတာ {len(available)} ခု ရှိပါတယ်။")

    if not available:
        print("တင်စရာ Game မရှိပါ။ ဖိုင်အရင်ပို့ထားပါ။")
        return

    selected = random.choice(available)
    try:
        # ၁။ File ကို Storage ဆီပို့မယ်
        sent_file = bot.copy_message(FILE_STORE_CH, selected["from_chat_id"], selected["original_msg_id"])
        
        # ၂။ Link တည်ဆောက်မယ်
        clean_ch = FILE_STORE_CH.replace("@", "")
        file_link = f"https://t.me/{clean_ch}/{sent_file.message_id}"

        # ၃။ Post တင်မယ်
        caption = (
            f"Game: **{selected['name']}** ❞\n\n"
            f"Offline 🚩 ❞\n\n"
            f"Link: [ [Download]({file_link}) ] ❞"
        )
        bot.send_message(POST_CH, caption, parse_mode="Markdown")
        
        # ၄။ မှတ်တမ်းသွင်းမယ်
        db["posted_ids"].append(str(selected["original_msg_id"]))
        save_db(db)
        print(f"အောင်မြင်စွာ တင်ပြီးပါပြီ: {selected['name']}")
    except Exception as e:
        print(f"အမှားဖြစ်သွားပါတယ်: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_run_process()
    else:
        bot.polling(none_stop=True)
       import
