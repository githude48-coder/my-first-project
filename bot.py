import telebot
import json
import random
import os
import sys

# --- CONFIGURATION ---
TOKEN = "8274761916:AAF5wk3UDg51JFQnFCwa58WGvLiN8vpzgSQ"
OFFLINE_CH = "@offlinegamelink" # ဖိုင်တွေ သိမ်းမယ့်နေရာ
MAIN_CH = "@offlinegame999"    # Post တင်မယ့်နေရာ
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

# ၁။ Bot ဆီ File ပို့ရင် Forward ဖျောက်ပြီး ပို့မယ့်အပိုင်း
@bot.message_handler(content_types=['document'])
def handle_file(message):
    db = load_db()
    file_name = message.document.file_name
    
    try:
        # copy_message က Forward Tag မပါဘဲ ပို့ပေးတာပါ
        sent_msg = bot.copy_message(OFFLINE_CH, message.chat.id, message.message_id)
        
        # Link ဖန်တီးခြင်း (Channel က Public ဖြစ်ဖို့လိုပါတယ်)
        # Link ပုံစံ: https://t.me/offlinegamelink/123
        clean_ch_name = OFFLINE_CH.replace("@", "")
        file_link = f"https://t.me/{clean_ch_name}/{sent_msg.message_id}"
        
        new_game = {
            "id": sent_msg.message_id, 
            "name": file_name, 
            "link": file_link
        }
        
        db["games"].append(new_game)
        save_db(db)
        bot.reply_to(message, f"✅ သိမ်းပြီးပါပြီ- {file_name}")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# ၂။ ကျပန်းစနစ်နဲ့ Post တင်မည့် Function
def auto_post():
    db = load_db()
    all_games = db.get("games", [])
    posted_ids = db.get("posted_ids", [])

    if not all_games:
        print("တင်စရာ Game မရှိသေးပါ။")
        return

    # တင်ပြီးသားတွေ Limit ပြည့်သွားရင် (အကုန်ကုန်သွားရင်) အစက ပြန်စမယ်
    if len(posted_ids) >= len(all_games):
        db["posted_ids"] = []
        posted_ids = []
        print("Limit ပြည့်သွားလို့ အစက ပြန်စပါမယ်။")

    # မတင်ရသေးတဲ့ Game တွေကိုပဲ ရွေးမယ်
    available = [g for g in all_games if g["id"] not in posted_ids]
    if not available: return
    
    selected = random.choice(available)

    # Post ပုံစံ (Game နာမည် နဲ့ Download Link ပါမယ်)
    caption = (
        f"Game: {selected['name']} ❞\n\n"
        f"Offline 🚩 ❞\n\n"
        f"Link: [ [Download]({selected['link']}) ] ❞"
    )

    try:
        bot.send_message(MAIN_CH, caption, parse_mode="Markdown")
        db["posted_ids"].append(selected["id"])
        save_db(db)
        print(f"အောင်မြင်စွာ တင်ပြီးပါပြီ- {selected['name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        auto_post()
    else:
        print("Bot စတင်နေပါပြီ... ဖိုင်များ ပို့နိုင်ပါသည်။")
        bot.polling(none_stop=True)
