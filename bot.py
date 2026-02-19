import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
OFFLINE_CH = "@offlinegamelink" # ဖိုင်တွေ သိမ်းမယ့်နေရာ
MAIN_CH = "@offlinegame99"      # Post တင်မယ့်နေရာ (Screenshot အရ @offlinegame99 ဖြစ်နေလို့ ပြန်ပြင်ပေးထားပါတယ်)
DB_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                content = f.read().strip()
                return json.loads(content) if content else {"games": [], "posted_ids": []}
        except:
            return {"games": [], "posted_ids": []}
    return {"games": [], "posted_ids": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ၁။ Bot ဆီ ဖိုင်ပို့ရင် Forward ဖျောက်သိမ်းမယ့်အပိုင်း
@bot.message_handler(content_types=['document'])
def handle_file(message):
    db = load_db()
    file_name = message.document.file_name
    
    try:
        # Forward ဖျောက်ပြီး ပို့ခြင်း (Copy Message)
        sent_msg = bot.copy_message(OFFLINE_CH, message.chat.id, message.message_id)
        
        # Link ဖန်တီးခြင်း
        clean_ch = OFFLINE_CH.replace("@", "")
        file_link = f"https://t.me/{clean_ch}/{sent_msg.message_id}"
        
        new_game = {
            "id": sent_msg.message_id, 
            "name": file_name.replace(".apk", "").replace("-", " ").title(), # နာမည်ကို လှလှပပ ပြင်ပေးခြင်း
            "link": file_link
        }
        
        db["games"].append(new_game)
        save_db(db)
        bot.reply_to(message, f"✅ Database ထဲ သိမ်းလိုက်ပါပြီ - {file_name}")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# ၂။ ကျပန်းစနစ်နဲ့ Post တင်မည့် Function (GitHub Actions က ဒါကို ခေါ်သုံးမှာပါ)
def run_auto_post():
    db = load_db()
    all_games = db.get("games", [])
    posted_ids = db.get("posted_ids", [])

    if not all_games:
        print("တင်စရာ Game မရှိသေးပါ။")
        return

    # တင်ပြီးသားတွေ အားလုံးကုန်သွားရင် အစက ပြန်စမယ်
    if len(posted_ids) >= len(all_games):
        db["posted_ids"] = []
        posted_ids = []
        print("Limit ပြည့်သွားပြီဖြစ်လို့ အစက ပြန်စပါမယ်။")

    # မတင်ရသေးတဲ့ Game ကို ရှာမယ်
    available = [g for g in all_games if g["id"] not in posted_ids]
    if not available: return
    
    selected = random.choice(available)

    # Post ပုံစံ (Screenshot ထဲကအတိုင်း)
    caption = (
        f"Game: {selected['name']} ❞\n\n"
        f"Offline 🚩 ❞\n\n"
        f"Link: [ [Download]({selected['link']}) ] ❞"
    )

    try:
        bot.send_message(MAIN_CH, caption, parse_mode="Markdown")
        db["posted_ids"].append(selected["id"])
        save_db(db)
        print(f"Posted: {selected['name']}")
    except Exception as e:
        print(f"Error Posting: {e}")

# GitHub Actions က နှိုးလိုက်ရင် Post တင်ဖို့ အပိုင်း
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        run_auto_post()
    else:
        print("Bot is listening for files...")
        bot.polling(none_stop=True)
