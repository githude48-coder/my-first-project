import telebot
import json
import random
import os

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
                if "file_data" not in data: data["file_data"] = {}
                return data
        except: pass
    return {"games": [], "posted_ids": [], "file_data": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def auto_run_process():
    db = load_db()
    updates = bot.get_updates(offset=-50, limit=100)
    
    for up in updates:
        if not up.message: continue
        msg = up.message
        
        # ၁။ File သိမ်းဆည်းခြင်း (ပိုမိုကောင်းမွန်သော နာမည်စစ်ဆေးမှု)
        if msg.document and msg.document.file_name.endswith(".apk"):
            # ရှေ့ဆုံးက စာလုံး ၂ လုံးကို ယူမယ် (ဥပမာ- days after)
            file_key = " ".join(msg.document.file_name.lower().replace("-", " ").split()[:2])
            db["file_data"][file_key] = {
                "message_id": msg.message_id,
                "chat_id": msg.chat.id,
                "url": f"https://t.me/{FILE_STORE_CH.replace('@','')}/{msg.message_id}"
            }

        # ၂။ Post သိမ်းဆည်းခြင်း
        elif (msg.caption or msg.text) and (msg.photo or msg.video):
            text = msg.caption if msg.caption else msg.text
            if "Game:" in text:
                game_name = text.split("Game:")[1].split("\n")[0].strip().lower()
                if not any(g['post_id'] == msg.message_id for g in db["games"]):
                    db["games"].append({
                        "name": game_name,
                        "post_id": msg.message_id,
                        "chat_id": msg.chat.id,
                        "caption": text
                    })
    save_db(db)

    available = [g for g in db["games"] if str(g["post_id"]) not in db["posted_ids"]]
    if not available: return

    selected = random.choice(available)
    # ရှေ့ဆုံးစာလုံး ၂ လုံးနဲ့ ပြန်ရှာမယ်
    search_key = " ".join(selected["name"].split()[:2])
    file_info = db["file_data"].get(search_key)
    
    download_url = file_info["url"] if file_info else f"https://t.me/{FILE_STORE_CH.replace('@','')}"

    try:
        # ၃။ Post တင်ခြင်း (Link ပါဝင်သော Caption နှင့်)
        new_caption = selected["caption"].replace("[ Download ]", f"[Download]({download_url})")
        
        orig_msg = bot.get_message(selected["chat_id"], selected["post_id"])
        if orig_msg.photo:
            bot.send_photo(POST_CH, orig_msg.photo[-1].file_id, caption=new_caption, parse_mode="Markdown", disable_web_page_preview=True)
        
        # ၄။ File ကို ချက်ချင်းလိုက်တင်ခြင်း (ဒီအပိုင်းက အရေးကြီးဆုံး)
        if file_info:
            bot.copy_message(POST_CH, file_info["chat_id"], file_info["message_id"])
        
        db["posted_ids"].append(str(selected["post_id"]))
        save_db(db)
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    auto_run_process()
